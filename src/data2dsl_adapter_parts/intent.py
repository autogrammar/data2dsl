"""Intent source adapters for data2dsl observation normalization."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence


from data2dsl_adapter_parts.common import DEFAULT_INTENT_CONTRACT_EXTRACTOR, SCHEMA_OBSERVATION, compute_sha256

@dataclass(frozen=True)
class IntentContractResponse:
    """Response structure from subactor/intent-contract-dsl-runtime."""

    status: str  # "OK", "ERROR", "UNAVAILABLE"
    contract_id: str = "intent-contract-001"
    parties: Sequence[str] = field(default_factory=tuple)
    deliverables: Sequence[str] = field(default_factory=tuple)
    obligations: Sequence[str] = field(default_factory=tuple)
    path: str = "intent-contract.dsl.json"
    start_line: int = 1
    end_line: int = 1
    source_revision: str | None = None
    error_message: str | None = None


class IntentContractAdapter:
    """Adapter for converting Subactor Intent Contracts into data2dsl observations."""

    def __init__(self, extractor: dict[str, str] | None = None) -> None:
        self._extractor = extractor or DEFAULT_INTENT_CONTRACT_EXTRACTOR

    def normalize(
        self,
        query: dict[str, Any],
        response: IntentContractResponse,
        side: str = "left",
        observation_id: str | None = None,
    ) -> dict[str, Any]:
        """Normalize an Intent Contract response into a data2dsl observation envelope."""
        query_id = query["query_id"]
        subject = query["subject"]
        metric = query["metric"]
        window = query["window"]
        target_uri = subject.get("repository", "file://local/contracts")

        if response.status != "OK" or response.error_message:
            obs_id = observation_id or f"observation:intent_contract:unevaluable:{side}"
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
                        "evidence_id": f"evidence:intent_contract:error:{side}",
                        "target_uri": target_uri,
                        "source_uri": f"{target_uri}/{response.path}",
                        "source_revision": f"sha256:{err_digest}",
                        "media_type": "application/json",
                        "digest_sha256": err_digest,
                        "extractor": self._extractor,
                        "location": {
                            "kind": "json-lines",
                            "path": response.path,
                            "start_line": 1,
                            "end_line": 1,
                        },
                    }
                ],
            }

        val_kind = metric.get("value_kind", "string-set")
        metric_id = (metric.get("id") or metric.get("name") or "").lower()
        metric_prop = metric.get("property", "").lower()

        val_obj: dict[str, Any]
        if "party" in metric_id or "parties" in metric_id or "parties" in metric_prop or "party" in metric_prop:
            parties_sorted = sorted(list(response.parties))
            if val_kind == "integer":
                val_obj = {"kind": "integer", "value": str(len(parties_sorted))}
            else:
                val_obj = {"kind": "string-set", "items": parties_sorted}
        elif "obligation" in metric_id or "obligations" in metric_id or "obligations" in metric_prop or "obligation" in metric_prop:
            obligations_sorted = sorted(list(response.obligations))
            if val_kind == "integer":
                val_obj = {"kind": "integer", "value": str(len(obligations_sorted))}
            else:
                val_obj = {"kind": "string-set", "items": obligations_sorted}
        elif "deliverable" in metric_id or "deliverables" in metric_id or "deliverables" in metric_prop or "deliverable" in metric_prop or not metric_id:
            deliverables_sorted = sorted(list(response.deliverables))
            if val_kind == "integer":
                val_obj = {"kind": "integer", "value": str(len(deliverables_sorted))}
            else:
                val_obj = {"kind": "string-set", "items": deliverables_sorted}
        else:
            return {
                "schema": SCHEMA_OBSERVATION,
                "observation_id": observation_id or f"observation:intent_contract:unsupported:{side}",
                "query_id": query_id,
                "side": side,
                "subject": subject,
                "metric": metric,
                "window": window,
                "state": "UNEVALUABLE",
                "value": None,
                "evidence": [
                    {
                        "evidence_id": f"evidence:intent_contract:unsupported:{side}",
                        "target_uri": target_uri,
                        "source_uri": f"{target_uri}/{response.path}",
                        "source_revision": response.source_revision or f"sha256:{compute_sha256(response.path)}",
                        "media_type": "application/json",
                        "digest_sha256": compute_sha256(response.path),
                        "extractor": self._extractor,
                        "location": {
                            "kind": "json-lines",
                            "path": response.path,
                            "start_line": 1,
                            "end_line": 1,
                        },
                    }
                ],
            }

        val_repr = ",".join(sorted(str(i) for i in val_obj["items"])) if val_obj.get("kind") == "string-set" else str(val_obj.get("value", ""))
        parties_str = ",".join(sorted(response.parties))
        obligations_str = ",".join(sorted(response.obligations))
        deliverables_str = ",".join(sorted(response.deliverables))
        digest = compute_sha256(f"{response.contract_id}:{parties_str}:{obligations_str}:{deliverables_str}:{val_repr}")
        src_rev = response.source_revision or f"sha256:{digest}"
        obs_id = observation_id or f"observation:intent_contract:{digest[:8]}"

        evidence_list = [
            {
                "evidence_id": f"evidence:intent_contract:{response.contract_id}:{digest[:8]}",
                "target_uri": target_uri,
                "source_uri": f"{target_uri}/{response.path}",
                "source_revision": src_rev,
                "media_type": "application/json",
                "digest_sha256": digest,
                "extractor": self._extractor,
                "location": {
                    "kind": "json-lines",
                    "path": response.path,
                    "start_line": response.start_line,
                    "end_line": response.end_line,
                },
            }
        ]

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
# OQL Scenario & Telemetry Adapter (oqlos)
# ---------------------------------------------------------------------------


