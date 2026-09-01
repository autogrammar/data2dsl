"""Deta source adapters for data2dsl observation normalization."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence


from data2dsl_adapter_parts.common import DEFAULT_DETA_EXTRACTOR, SCHEMA_OBSERVATION, compute_sha256

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
        query_id = query["query_id"]
        subject = query["subject"]
        metric = query["metric"]
        window = query["window"]
        target_uri = subject.get("repository", "file://local/infra")

        if response.status != "OK" or (response.service_count is None and not response.services and not response.ports and response.error_message):
            obs_id = observation_id or f"observation:deta:unevaluable:{side}"
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
                        "evidence_id": f"evidence:deta:error:{side}",
                        "target_uri": target_uri,
                        "source_uri": f"{target_uri}/{response.manifest_path}",
                        "source_revision": f"sha256:{err_digest}",
                        "media_type": "application/yaml",
                        "digest_sha256": err_digest,
                        "extractor": self._extractor,
                        "location": {
                            "kind": "yaml-lines",
                            "path": response.manifest_path,
                            "start_line": 1,
                            "end_line": 1,
                        },
                    }
                ],
            }

        val_kind = metric.get("value_kind", "integer")
        metric_id = (metric.get("id") or metric.get("name") or "").lower()
        metric_prop = metric.get("property", "").lower()
        is_port_query = "port" in metric_id or "port" in metric_prop or "ports" in metric_id or "ports" in metric_prop

        val_obj: dict[str, Any]
        if is_port_query:
            if val_kind == "string-set":
                val_obj = {"kind": "string-set", "items": sorted(list(response.ports))}
            else:
                val_obj = {"kind": "integer", "value": str(len(response.ports))}
        else:
            if val_kind == "string-set":
                service_names = sorted([s.name for s in response.services])
                val_obj = {"kind": "string-set", "items": service_names}
            elif val_kind == "integer":
                count = response.service_count if response.service_count is not None else len(response.services)
                val_obj = {"kind": "integer", "value": str(count)}
            else:
                count = response.service_count if response.service_count is not None else len(response.services)
                val_obj = {"kind": "string", "value": str(count)}

        evidence_list = []
        if response.services:
            for s in response.services:
                digest = s.digest_sha256 or compute_sha256(f"{s.name}:{s.service_type}")
                src_rev = response.source_revision or f"sha256:{digest}"
                evidence_list.append(
                    {
                        "evidence_id": f"evidence:deta:service:{s.name}:{digest[:8]}",
                        "target_uri": target_uri,
                        "source_uri": f"{target_uri}/{s.manifest_path}",
                        "source_revision": src_rev,
                        "media_type": s.media_type,
                        "digest_sha256": digest,
                        "extractor": self._extractor,
                        "location": {
                            "kind": "yaml-lines",
                            "path": s.manifest_path,
                            "start_line": s.start_line,
                            "end_line": s.end_line,
                        },
                    }
                )
        else:
            ports_str = ",".join(str(p) for p in sorted(response.ports))
            digest = compute_sha256(f"topology:{response.manifest_path}:{response.service_count}:{ports_str}")
            src_rev = response.source_revision or f"sha256:{digest}"
            evidence_list.append(
                {
                    "evidence_id": f"evidence:deta:{response.manifest_path}:{digest[:8]}",
                    "target_uri": target_uri,
                    "source_uri": f"{target_uri}/{response.manifest_path}",
                    "source_revision": src_rev,
                    "media_type": "application/yaml",
                    "digest_sha256": digest,
                    "extractor": self._extractor,
                    "location": {
                        "kind": "yaml-lines",
                        "path": response.manifest_path,
                        "start_line": 1,
                        "end_line": 1,
                    },
                }
            )

        evidence_list.sort(key=lambda e: e["evidence_id"])
        first_digest = evidence_list[0]["digest_sha256"][:8] if evidence_list else "00000000"
        obs_id = observation_id or f"observation:deta:{first_digest}"

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
# Subactor Intent Contract Adapter
# ---------------------------------------------------------------------------


