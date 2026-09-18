"""Deta source adapters for data2dsl observation normalization."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence


from data2dsl_adapter_parts.common import (
    DEFAULT_DETA_EXTRACTOR,
    SCHEMA_OBSERVATION,
    compute_sha256,
    error_observation,
    evidence_entry,
    observation_envelope,
)

@dataclass(frozen=True)
class DetaServiceEvidence:
    """Represents an infrastructure component or service from Deta topology."""

    name: str
    service_type: str = "service"
    ports: Sequence[str] = field(default_factory=tuple)
    manifest_path: str = "compose.yml"
    start_line: int = 1
    end_line: int = 1
    digest_sha256: str | None = None
    media_type: str = "application/yaml"


@dataclass(frozen=True)
class DetaTopologyResponse:
    """Response structure from semcod/deta topology analysis."""

    status: str  # "OK", "ERROR", "UNAVAILABLE"
    services: Sequence[DetaServiceEvidence] = field(default_factory=tuple)
    service_count: int | None = None
    ports: Sequence[str] = field(default_factory=tuple)
    manifest_path: str = "compose.yml"
    source_revision: str | None = None
    error_message: str | None = None


class DetaAdapter:
    """Adapter for converting semcod/deta infrastructure topology facts into data2dsl observations."""

    def __init__(self, extractor: dict[str, str] | None = None) -> None:
        self._extractor = extractor or DEFAULT_DETA_EXTRACTOR

    def normalize(
        self,
        query: dict[str, Any],
        response: DetaTopologyResponse,
        side: str = "left",
        observation_id: str | None = None,
    ) -> dict[str, Any]:
        """Normalize a Deta topology response into a data2dsl observation envelope."""
        target_uri = query["subject"].get("repository", "file://local/infra")

        if response.status != "OK" or (response.service_count is None and not response.services and not response.ports and response.error_message):
            return error_observation(
                query, prefix="deta", side=side,
                observation_id=observation_id, target_uri=target_uri,
                path=response.manifest_path, status=response.status,
                error_message=response.error_message, extractor=self._extractor,
                location_kind="yaml-lines", media_type="application/yaml",
            )

        val_obj = self._metric_value(query["metric"], response)
        evidence_list = self._evidence(response, target_uri)
        evidence_list.sort(key=lambda e: e["evidence_id"])
        first_digest = evidence_list[0]["digest_sha256"][:8] if evidence_list else "00000000"
        obs_id = observation_id or f"observation:deta:{first_digest}"
        return observation_envelope(query, obs_id, side, "OBSERVED", val_obj, evidence_list)

    @staticmethod
    def _metric_value(metric: dict[str, Any], response: DetaTopologyResponse) -> dict[str, Any]:
        val_kind = metric.get("value_kind", "integer")
        metric_id = (metric.get("id") or metric.get("name") or "").lower()
        metric_prop = metric.get("property", "").lower()
        is_port_query = "port" in metric_id or "port" in metric_prop or "ports" in metric_id or "ports" in metric_prop
        if is_port_query:
            if val_kind == "string-set":
                return {"kind": "string-set", "items": sorted(list(response.ports))}
            return {"kind": "integer", "value": str(len(response.ports))}
        if val_kind == "string-set":
            return {"kind": "string-set", "items": sorted([s.name for s in response.services])}
        count = response.service_count if response.service_count is not None else len(response.services)
        if val_kind == "integer":
            return {"kind": "integer", "value": str(count)}
        return {"kind": "string", "value": str(count)}

    def _evidence(self, response: DetaTopologyResponse, target_uri: str) -> list[dict[str, Any]]:
        if response.services:
            return [self._service_evidence(response, s, target_uri) for s in response.services]
        return [self._topology_evidence(response, target_uri)]

    def _service_evidence(self, response: DetaTopologyResponse, service: Any, target_uri: str) -> dict[str, Any]:
        digest = service.digest_sha256 or compute_sha256(f"{service.name}:{service.service_type}")
        return evidence_entry(
            evidence_id=f"evidence:deta:service:{service.name}:{digest[:8]}",
            target_uri=target_uri, path=service.manifest_path,
            source_revision=response.source_revision or f"sha256:{digest}",
            digest=digest, extractor=self._extractor,
            location_kind="yaml-lines", media_type=service.media_type,
            start_line=service.start_line, end_line=service.end_line,
        )

    def _topology_evidence(self, response: DetaTopologyResponse, target_uri: str) -> dict[str, Any]:
        ports_str = ",".join(str(p) for p in sorted(response.ports))
        digest = compute_sha256(f"topology:{response.manifest_path}:{response.service_count}:{ports_str}")
        return evidence_entry(
            evidence_id=f"evidence:deta:{response.manifest_path}:{digest[:8]}",
            target_uri=target_uri, path=response.manifest_path,
            source_revision=response.source_revision or f"sha256:{digest}",
            digest=digest, extractor=self._extractor,
            location_kind="yaml-lines", media_type="application/yaml",
        )
