"""Intent source adapters for data2dsl observation normalization."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence


from data2dsl_adapter_parts.common import (
    DEFAULT_INTENT_CONTRACT_EXTRACTOR,
    SCHEMA_OBSERVATION,
    compute_sha256,
    error_observation,
    evidence_entry,
    observation_envelope,
    set_value,
    unsupported_observation,
)

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
        target_uri = query["subject"].get("repository", "file://local/contracts")

        if response.status != "OK" or response.error_message:
            return error_observation(
                query, prefix="intent_contract", side=side,
                observation_id=observation_id, target_uri=target_uri,
                path=response.path, status=response.status,
                error_message=response.error_message, extractor=self._extractor,
                location_kind="json-lines",
            )

        val_obj = self._metric_value(query["metric"], response)
        if val_obj is None:
            return unsupported_observation(
                query, prefix="intent_contract", side=side,
                observation_id=observation_id, obs_suffix="unsupported",
                target_uri=target_uri, path=response.path,
                source_revision=response.source_revision, extractor=self._extractor,
                location_kind="json-lines",
            )

        val_repr = (
            ",".join(sorted(str(i) for i in val_obj["items"]))
            if val_obj.get("kind") == "string-set"
            else str(val_obj.get("value", ""))
        )
        parties_str = ",".join(sorted(response.parties))
        obligations_str = ",".join(sorted(response.obligations))
        deliverables_str = ",".join(sorted(response.deliverables))
        digest = compute_sha256(f"{response.contract_id}:{parties_str}:{obligations_str}:{deliverables_str}:{val_repr}")
        src_rev = response.source_revision or f"sha256:{digest}"
        obs_id = observation_id or f"observation:intent_contract:{digest[:8]}"

        evidence_list = [
            evidence_entry(
                evidence_id=f"evidence:intent_contract:{response.contract_id}:{digest[:8]}",
                target_uri=target_uri, path=response.path,
                source_revision=src_rev, digest=digest,
                extractor=self._extractor, location_kind="json-lines",
                start_line=response.start_line, end_line=response.end_line,
            )
        ]
        return observation_envelope(query, obs_id, side, "OBSERVED", val_obj, evidence_list)

    @staticmethod
    def _matches(metric_id: str, metric_prop: str, *keywords: str) -> bool:
        return any(k in metric_id or k in metric_prop for k in keywords)

    @classmethod
    def _metric_value(cls, metric: dict[str, Any], response: IntentContractResponse) -> dict[str, Any] | None:
        val_kind = metric.get("value_kind", "string-set")
        metric_id = (metric.get("id") or metric.get("name") or "").lower()
        metric_prop = metric.get("property", "").lower()
        if cls._matches(metric_id, metric_prop, "party", "parties"):
            return set_value(response.parties, val_kind)
        if cls._matches(metric_id, metric_prop, "obligation", "obligations"):
            return set_value(response.obligations, val_kind)
        if cls._matches(metric_id, metric_prop, "deliverable", "deliverables") or not metric_id:
            return set_value(response.deliverables, val_kind)
        return None
