"""Curllm source adapters for data2dsl observation normalization."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence


from data2dsl_adapter_parts.common import DEFAULT_CURLLM_EXTRACTOR, SCHEMA_OBSERVATION, compute_sha256

@dataclass(frozen=True)
class CurllmPageEvidence:
    """Represents page-level evidence from Curllm browser automation."""

    url: str
    digest_sha256: str
    page: int = 1
    endpoint: str = "web-page"
    source_revision: str | None = None
    media_type: str = "text/html"


@dataclass(frozen=True)
class CurllmMetricResponse:
    """Response structure from Curllm browser automation / BQL query."""

    status: str  # "OK", "ERROR", "TIMEOUT", "UNAVAILABLE"
    value: int | str | Sequence[str] | None = None
    pages: Sequence[CurllmPageEvidence] = field(default_factory=tuple)
    source_revision: str | None = None
    error_message: str | None = None


class CurllmAdapter:
    """Adapter for normalizing Curllm browser automation facts into observations."""

    def __init__(self, extractor: dict[str, str] | None = None) -> None:
        self._extractor = extractor or DEFAULT_CURLLM_EXTRACTOR

    def normalize(
        self,
        query: dict[str, Any],
        response: CurllmMetricResponse,
        side: str = "right",
        observation_id: str | None = None,
    ) -> dict[str, Any]:
        """Normalize Curllm BQL browser response into data2dsl observation."""
        query_id = query["query_id"]
        subject = query["subject"]
        metric = query["metric"]
        window = query["window"]
        target_uri = subject["repository"]

        if response.status != "OK" or response.value is None or not response.pages:
            obs_id = observation_id or f"observation:curllm:unevaluable:{side}"
            err_text = response.error_message or f"error:{response.status}"
            err_digest = compute_sha256(err_text)
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
                        "evidence_id": f"evidence:curllm:error:{side}",
                        "target_uri": target_uri,
                        "source_uri": target_uri,
                        "source_revision": f"sha256:{err_digest}",
                        "media_type": "text/html",
                        "digest_sha256": err_digest,
                        "extractor": self._extractor,
                        "location": {
                            "kind": "github-page",
                            "endpoint": "curllm-error",
                            "page": 1,
                            "cursor": None,
                        },
                    }
                ],
            }

        val_kind = metric.get("value_kind", "integer")
        val_obj: dict[str, Any]
        if val_kind == "integer":
            val_obj = {"kind": "integer", "value": str(int(response.value))}  # type: ignore[arg-type]
        elif val_kind == "string-set":
            items = sorted(list(response.value))  # type: ignore[arg-type]
            val_obj = {"kind": "string-set", "items": items}
        else:
            val_obj = {"kind": "string", "value": str(response.value)}

        evidence_list = []
        for idx, page in enumerate(response.pages, start=1):
            src_rev = page.source_revision or response.source_revision or f"sha256:{page.digest_sha256}"
            evidence_list.append(
                {
                    "evidence_id": f"evidence:curllm:page:{idx}:{page.digest_sha256[:8]}",
                    "target_uri": target_uri,
                    "source_uri": page.url,
                    "source_revision": src_rev,
                    "media_type": page.media_type,
                    "digest_sha256": page.digest_sha256,
                    "extractor": self._extractor,
                    "location": {
                        "kind": "github-page",
                        "endpoint": page.endpoint,
                        "page": page.page,
                        "cursor": None,
                    },
                }
            )

        # Sort evidence lexicographically by evidence_id
        evidence_list.sort(key=lambda e: e["evidence_id"])
        first_digest = evidence_list[0]["digest_sha256"][:8] if evidence_list else "00000000"
        obs_id = observation_id or f"observation:curllm:{first_digest}"

        return {
            "schema": SCHEMA_OBSERVATION,
            "observation_id": obs_id,
            "query_id": query_id,
            "side": side,
            "subject": subject,
            "metric": metric,
            "window": window,
            "state": "OBSERVED",
            "value": val_obj,
            "evidence": evidence_list,
        }


# ---------------------------------------------------------------------------
# Planfile SDLC / Ticket Adapter
# ---------------------------------------------------------------------------


