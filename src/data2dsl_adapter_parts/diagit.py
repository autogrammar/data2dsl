"""Diagit source adapters for data2dsl observation normalization."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence


from data2dsl_adapter_parts.common import DEFAULT_DIAGIT_EXTRACTOR, SCHEMA_OBSERVATION, compute_sha256



@dataclass(frozen=True)
class DiagitPageEvidence:
    """Represents raw page response evidence from the Diagit GitHub provider."""

    page: int
    endpoint: str
    digest_sha256: str
    source_revision: str
    source_uri: str
    cursor: str | None = None
    media_type: str = "application/json"


@dataclass(frozen=True)
class DiagitCommitMetricResponse:
    """Response structure from the extended Diagit GitHub provider for commit metrics."""

    status: str  # "OK", "NOT_FOUND", "UNAVAILABLE", "ERROR"
    commit_count: int | None = None
    pages: Sequence[DiagitPageEvidence] = field(default_factory=tuple)
    error_message: str | None = None


class GitHubDiagitAdapter:
    """Adapter for converting Diagit GitHub metrics into data2dsl observations."""

    def __init__(self, extractor: dict[str, str] | None = None) -> None:
        self._extractor = extractor or DEFAULT_DIAGIT_EXTRACTOR

    def normalize(
        self,
        query: dict[str, Any],
        response: DiagitCommitMetricResponse,
        side: str = "right",
        observation_id: str | None = None,
    ) -> dict[str, Any]:
        """Normalize a Diagit provider response into a data2dsl observation envelope."""
        query_id = query["query_id"]
        subject = query["subject"]
        metric = query["metric"]
        window = query["window"]
        target_uri = subject["repository"]
        endpoint = "/repos" + target_uri.replace("https://github.com", "") + "/commits"

        if response.status != "OK" or response.commit_count is None:
            obs_id = observation_id or f"observation:github:unevaluable:{side}"
            err_text = response.error_message or f"error:{response.status}"
            err_digest = compute_sha256(err_text)
            err_rev = f"sha256:{err_digest}"
            ev_id = f"evidence:github:error:{side}"
            return {
                "schema": SCHEMA_OBSERVATION,
                "observation_id": obs_id,
                "query_id": query_id,
                "side": side,
                "subject": subject,
                "metric": metric,
                "window": window,
                "state": "UNEVALUABLE",
                "value": None,
                "evidence": [
                    {
                        "evidence_id": ev_id,
                        "target_uri": target_uri,
                        "source_uri": f"https://api.github.com{endpoint}",
                        "source_revision": err_rev,
                        "media_type": "application/json",
                        "digest_sha256": err_digest,
                        "extractor": self._extractor,
                        "location": {
                            "kind": "github-page",
                            "endpoint": endpoint,
                            "page": 1,
                            "cursor": None,
                        },
                    }
                ],
            }

        count = response.commit_count
        obs_id = observation_id or f"observation:github:{count}"

        evidence_list: list[dict[str, Any]] = []
        if response.pages:
            for page_ev in response.pages:
                ev_id = f"evidence:github:commits:page-{page_ev.page}"
                evidence_list.append(
                    {
                        "evidence_id": ev_id,
                        "target_uri": target_uri,
                        "source_uri": page_ev.source_uri,
                        "source_revision": page_ev.source_revision,
                        "media_type": page_ev.media_type,
                        "digest_sha256": page_ev.digest_sha256,
                        "extractor": self._extractor,
                        "location": {
                            "kind": "github-page",
                            "endpoint": page_ev.endpoint,
                            "page": page_ev.page,
                            "cursor": page_ev.cursor,
                        },
                    }
                )
        else:
            dummy_digest = compute_sha256(f"{target_uri}:{count}:{window['start']}:{window['end']}")
            dummy_rev = f"sha256:{dummy_digest}"
            evidence_list.append(
                {
                    "evidence_id": "evidence:github:commits:page-1",
                    "target_uri": target_uri,
                    "source_uri": f"https://api.github.com{endpoint}",
                    "source_revision": dummy_rev,
                    "media_type": "application/json",
                    "digest_sha256": dummy_digest,
                    "extractor": self._extractor,
                    "location": {
                        "kind": "github-page",
                        "endpoint": endpoint,
                        "page": 1,
                        "cursor": None,
                    },
                }
            )

        return {
            "schema": SCHEMA_OBSERVATION,
            "observation_id": obs_id,
            "query_id": query_id,
            "side": side,
            "subject": subject,
            "metric": metric,
            "window": window,
            "state": "OBSERVED",
            "value": {"kind": "integer", "value": str(count)},
            "evidence": evidence_list,
        }


def build_github_commit_observation(
    query: dict[str, Any],
    commit_count: int | None,
    pages: Sequence[DiagitPageEvidence] = (),
    status: str = "OK",
    side: str = "right",
    observation_id: str | None = None,
) -> dict[str, Any]:
    """Convenience helper to construct a normalized observation from raw commit fields."""
    adapter = GitHubDiagitAdapter()
    response = DiagitCommitMetricResponse(
        status=status,
        commit_count=commit_count,
        pages=pages,
    )
    return adapter.normalize(query, response, side=side, observation_id=observation_id)


