"""Planfile source adapters for data2dsl observation normalization."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence


from data2dsl_adapter_parts.common import (
    DEFAULT_PLANFILE_EXTRACTOR,
    SCHEMA_OBSERVATION,
    compute_sha256,
    error_observation,
    evidence_entry,
    observation_envelope,
)

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
        target_uri = query["subject"].get("repository", "file://local/planfile")

        if response.status != "OK" or (response.count is None and not response.tickets and response.error_message):
            return error_observation(
                query, prefix="planfile", side=side,
                observation_id=observation_id, target_uri=target_uri,
                path=response.path, status=response.status,
                error_message=response.error_message, extractor=self._extractor,
                location_kind="yaml-lines", media_type="application/yaml",
            )

        val_obj = self._metric_value(query["metric"], response)
        evidence_list = self._evidence(response, target_uri)
        evidence_list.sort(key=lambda e: e["evidence_id"])
        first_digest = evidence_list[0]["digest_sha256"][:8] if evidence_list else "00000000"
        obs_id = observation_id or f"observation:planfile:{first_digest}"
        return observation_envelope(query, obs_id, side, "OBSERVED", val_obj, evidence_list)

    @staticmethod
    def _metric_value(metric: dict[str, Any], response: PlanfileMetricResponse) -> dict[str, Any]:
        val_kind = metric.get("value_kind", "integer")
        if val_kind == "string-set":
            ticket_ids = sorted([t.ticket_id for t in response.tickets])
            return {"kind": "string-set", "items": ticket_ids}
        count = response.count if response.count is not None else len(response.tickets)
        if val_kind == "integer":
            return {"kind": "integer", "value": str(count)}
        return {"kind": "string", "value": str(count)}

    def _evidence(self, response: PlanfileMetricResponse, target_uri: str) -> list[dict[str, Any]]:
        if response.tickets:
            return [self._ticket_evidence(response, t, target_uri) for t in response.tickets]
        return [self._count_evidence(response, target_uri)]

    def _ticket_evidence(self, response: PlanfileMetricResponse, ticket: Any, target_uri: str) -> dict[str, Any]:
        digest = ticket.digest_sha256 or compute_sha256(f"{ticket.ticket_id}:{ticket.status}")
        return evidence_entry(
            evidence_id=f"evidence:planfile:{ticket.ticket_id}:{digest[:8]}",
            target_uri=target_uri, path=ticket.path,
            source_revision=response.source_revision or f"sha256:{digest}",
            digest=digest, extractor=self._extractor,
            location_kind="yaml-lines", media_type=ticket.media_type,
            start_line=ticket.start_line, end_line=ticket.end_line,
        )

    def _count_evidence(self, response: PlanfileMetricResponse, target_uri: str) -> dict[str, Any]:
        digest = compute_sha256(f"count:{response.count}")
        return evidence_entry(
            evidence_id=f"evidence:planfile:{response.path.replace('/', ':')}:{digest[:8]}",
            target_uri=target_uri, path=response.path,
            source_revision=response.source_revision or f"sha256:{digest}",
            digest=digest, extractor=self._extractor,
            location_kind="yaml-lines", media_type="application/yaml",
        )
