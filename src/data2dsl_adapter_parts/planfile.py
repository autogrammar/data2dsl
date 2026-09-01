"""Planfile source adapters for data2dsl observation normalization."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence


from data2dsl_adapter_parts.common import DEFAULT_PLANFILE_EXTRACTOR, SCHEMA_OBSERVATION, compute_sha256

@dataclass(frozen=True)
class PlanfileTicketEvidence:
    """Represents a single ticket or task evidence from Planfile."""

    ticket_id: str
    title: str = ""
    status: str = "OPEN"
    path: str = "planfile.yaml"
    start_line: int = 1
    end_line: int = 1
    digest_sha256: str | None = None
    media_type: str = "application/yaml"


@dataclass(frozen=True)
class PlanfileMetricResponse:
    """Response structure from semcod/planfile query."""

    status: str  # "OK", "ERROR", "NOT_FOUND"
    tickets: Sequence[PlanfileTicketEvidence] = field(default_factory=tuple)
    count: int | None = None
    path: str = "planfile.yaml"
    source_revision: str | None = None
    error_message: str | None = None


class PlanfileAdapter:
    """Adapter for converting semcod/planfile tickets and tasks into data2dsl observations."""

    def __init__(self, extractor: dict[str, str] | None = None) -> None:
        self._extractor = extractor or DEFAULT_PLANFILE_EXTRACTOR

    def normalize(
        self,
        query: dict[str, Any],
        response: PlanfileMetricResponse,
        side: str = "left",
        observation_id: str | None = None,
    ) -> dict[str, Any]:
        """Normalize a Planfile response into a data2dsl observation envelope."""
        query_id = query["query_id"]
        subject = query["subject"]
        metric = query["metric"]
        window = query["window"]
        target_uri = subject.get("repository", "file://local/planfile")

        if response.status != "OK" or (response.count is None and not response.tickets and response.error_message):
            obs_id = observation_id or f"observation:planfile:unevaluable:{side}"
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
                        "evidence_id": f"evidence:planfile:error:{side}",
                        "target_uri": target_uri,
                        "source_uri": f"{target_uri}/{response.path}",
                        "source_revision": f"sha256:{err_digest}",
                        "media_type": "application/yaml",
                        "digest_sha256": err_digest,
                        "extractor": self._extractor,
                        "location": {
                            "kind": "yaml-lines",
                            "path": response.path,
                            "start_line": 1,
                            "end_line": 1,
                        },
                    }
                ],
            }

        val_kind = metric.get("value_kind", "integer")
        val_obj: dict[str, Any]
        if val_kind == "string-set":
            ticket_ids = sorted([t.ticket_id for t in response.tickets])
            val_obj = {"kind": "string-set", "items": ticket_ids}
        elif val_kind == "integer":
            num = response.count if response.count is not None else len(response.tickets)
            val_obj = {"kind": "integer", "value": str(num)}
        else:
            val_obj = {"kind": "string", "value": str(response.count if response.count is not None else len(response.tickets))}

        evidence_list = []
        if response.tickets:
            for t in response.tickets:
                digest = t.digest_sha256 or compute_sha256(f"{t.ticket_id}:{t.status}")
                src_rev = response.source_revision or f"sha256:{digest}"
                evidence_list.append(
                    {
                        "evidence_id": f"evidence:planfile:{t.ticket_id}:{digest[:8]}",
                        "target_uri": target_uri,
                        "source_uri": f"{target_uri}/{t.path}",
                        "source_revision": src_rev,
                        "media_type": t.media_type,
                        "digest_sha256": digest,
                        "extractor": self._extractor,
                        "location": {
                            "kind": "yaml-lines",
                            "path": t.path,
                            "start_line": t.start_line,
                            "end_line": t.end_line,
                        },
                    }
                )
        else:
            digest = compute_sha256(f"count:{response.count}")
            src_rev = response.source_revision or f"sha256:{digest}"
            evidence_list.append(
                {
                    "evidence_id": f"evidence:planfile:{response.path.replace('/', ':')}:{digest[:8]}",
                    "target_uri": target_uri,
                    "source_uri": f"{target_uri}/{response.path}",
                    "source_revision": src_rev,
                    "media_type": "application/yaml",
                    "digest_sha256": digest,
                    "extractor": self._extractor,
                    "location": {
                        "kind": "yaml-lines",
                        "path": response.path,
                        "start_line": 1,
                        "end_line": 1,
                    },
                }
            )

        evidence_list.sort(key=lambda e: e["evidence_id"])
        first_digest = evidence_list[0]["digest_sha256"][:8] if evidence_list else "00000000"
        obs_id = observation_id or f"observation:planfile:{first_digest}"

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
# Deta Infrastructure / Topology Adapter
# ---------------------------------------------------------------------------


