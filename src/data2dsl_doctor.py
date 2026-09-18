"""Diagnostic Profile Feed generator for doctor-agent and semcod/koru triage.

Conforms to docs/research-doctor-agent-feed.md:
- Formats comparison bundles into prioritized diagnostic profiles.
- Provides zero-hallucination discrepancy symptoms with typed deltas.
- Constructs deterministic evidence chains with cryptographic SHA-256 digests.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union


SEVERITY_ORDER = {
    "CRITICAL": 5,
    "HIGH": 4,
    "MEDIUM": 3,
    "LOW": 2,
    "INFO": 1,
}


@dataclass(frozen=True)
class EvidenceRef:
    """Cryptographically verified evidence reference."""

    evidence_id: str
    target_uri: str
    source_uri: str
    source_revision: str
    media_type: str
    digest_sha256: str
    extractor: Dict[str, str]
    location: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "target_uri": self.target_uri,
            "source_uri": self.source_uri,
            "source_revision": self.source_revision,
            "media_type": self.media_type,
            "digest_sha256": self.digest_sha256,
            "extractor": self.extractor,
            "location": self.location,
        }


def _extract_evidence_ref(ev: Dict[str, Any]) -> EvidenceRef:
    return EvidenceRef(
        evidence_id=str(ev.get("evidence_id", "")),
        target_uri=str(ev.get("target_uri", "")),
        source_uri=str(ev.get("source_uri", "")),
        source_revision=str(ev.get("source_revision", "")),
        media_type=str(ev.get("media_type", "application/json")),
        digest_sha256=str(ev.get("digest_sha256", "")),
        extractor=dict(ev.get("extractor", {})),
        location=dict(ev.get("location", {})),
    )


_CONFLICT_THRESHOLDS = {
    "percentage": ((20.0, "CRITICAL"), (10.0, "HIGH"), (5.0, "MEDIUM")),
    "integer": ((50, "CRITICAL"), (10, "HIGH"), (3, "MEDIUM")),
    "float": ((50.0, "CRITICAL"), (10.0, "HIGH"), (1.0, "MEDIUM")),
    "string-set": ((10, "CRITICAL"), (5, "HIGH"), (1, "MEDIUM")),
}


def _abs_or(raw, conv, default):
    """abs(conv(raw)) with a deterministic fallback."""
    try:
        return abs(conv(raw))
    except (ValueError, TypeError):
        return default


def _delta_magnitude(delta: Dict[str, Any]) -> Optional[Tuple[str, float]]:
    """Resolve the absolute magnitude for a known delta kind."""
    kind = delta.get("kind")
    if kind == "percentage":
        raw_str = str(delta.get("value", "0")).rstrip("%").strip()
        val = _abs_or(raw_str, float, 0.0)
    elif kind == "integer":
        val = _abs_or(delta.get("value", 0), int, 0)
    elif kind == "float":
        val = _abs_or(delta.get("value", 0.0), float, 0.0)
    elif kind == "string-set":
        val = len(delta.get("added", [])) + len(delta.get("removed", []))
    else:
        return None
    return kind, float(val)


def _severity_for(val: float, thresholds) -> Tuple[str, float]:
    for limit, severity in thresholds:
        if val >= limit:
            return severity, float(val)
    return "LOW", float(val)


def _calculate_severity_and_magnitude(
    outcome: str, delta: Optional[Dict[str, Any]]
) -> Tuple[str, float]:
    """Calculate deterministic severity and priority magnitude for triage sorting."""
    if outcome == "CONFLICT":
        parsed = _delta_magnitude(delta) if delta is not None else None
        if parsed is None:
            return "HIGH", 10.0
        kind, val = parsed
        return _severity_for(val, _CONFLICT_THRESHOLDS[kind])
    if outcome == "UNEVALUABLE":
        return "HIGH", 50.0
    if outcome in ("MISSING_LEFT", "MISSING_RIGHT"):
        return "HIGH", 40.0
    return "INFO", 0.0


class DiagnosticProfileFormatter:
    """Formats data2dsl comparison bundles into triage feeds for doctor-agent."""

    DIAGNOSTIC_VERSION = "1.0.0"

    @classmethod
    def format_profile(
        cls,
        comparison_results: Union[Dict[str, Any], List[Dict[str, Any]]],
        query: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Format comparison result(s) into a unified diagnostic profile."""
        bundles = _as_bundles(comparison_results)

        evidence_registry: Dict[str, EvidenceRef] = {}
        symptoms_raw = [
            _bundle_symptom(item, query, evidence_registry) for item in bundles
        ]

        # Sort symptoms by severity (descending), magnitude (descending), then metric id
        symptoms_raw.sort(key=_symptom_sort_key)
        sorted_symptoms = [s for s, _ in symptoms_raw]
        summary = _severity_summary(sorted_symptoms)

        # Build sorted evidence chain
        sorted_evidence_chain = [
            evidence_registry[eid].to_dict()
            for eid in sorted(evidence_registry.keys())
        ]

        timestamp = datetime.now(timezone.utc).isoformat()

        return {
            "diagnostic_version": cls.DIAGNOSTIC_VERSION,
            "timestamp": timestamp,
            "symptoms": sorted_symptoms,
            "evidence_chain": sorted_evidence_chain,
            "summary": summary,
        }


def format_diagnostic_profile(
    comparison_results: Union[Dict[str, Any], List[Dict[str, Any]]],
    query: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Helper function to format comparison results into a diagnostic profile."""
    return DiagnosticProfileFormatter.format_profile(comparison_results, query=query)


def _collect_side_evidence(
    observations: List[Dict[str, Any]], registry: Dict[str, EvidenceRef]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Extract and register evidence refs for the left and right observations."""
    obs_by_side = {obs.get("side"): obs for obs in observations if isinstance(obs, dict)}
    collected: List[List[Dict[str, Any]]] = []
    for side in ("left", "right"):
        obs = obs_by_side.get(side)
        side_evidence: List[Dict[str, Any]] = []
        if obs:
            for ev in obs.get("evidence", []):
                ref = _extract_evidence_ref(ev)
                registry[ref.evidence_id] = ref
                side_evidence.append(ref.to_dict())
        collected.append(side_evidence)
    return collected[0], collected[1]


def _query_digest_fallback(
    bundle_query: Dict[str, Any],
    registry: Dict[str, EvidenceRef],
    left_evidence: List[Dict[str, Any]],
) -> None:
    qd = bundle_query.get("digest")
    if not qd:
        return
    minimal_ref = EvidenceRef(
        evidence_id="query_digest_fallback",
        target_uri="",
        source_uri="",
        source_revision="",
        media_type="application/json",
        digest_sha256=qd,
        extractor={},
        location={},
    )
    registry[minimal_ref.evidence_id] = minimal_ref
    left_evidence.append(minimal_ref.to_dict())


def _resolve_missing_keys(
    outcome: str,
    delta: Optional[Dict[str, Any]],
    item: Dict[str, Any],
    result: Dict[str, Any],
) -> List[str]:
    if outcome == "MISSING_LEFT":
        return ["left"]
    if outcome == "MISSING_RIGHT":
        return ["right"]
    if delta and delta.get("kind") == "string-set":
        return list(delta.get("removed", []))
    if "missing_in_right" in item:
        return list(item["missing_in_right"])
    if "missing_in_right" in result:
        return list(result["missing_in_right"])
    return []


def _bundle_symptom(
    item: Dict[str, Any],
    query: Optional[Dict[str, Any]],
    evidence_registry: Dict[str, EvidenceRef],
) -> Tuple[Dict[str, Any], float]:
    """Build one sorted symptom entry from a single comparison bundle."""
    bundle_query = item.get("query", query) or {}
    result = item.get("result", item if "outcome" in item else {})
    observations = item.get("observations", [])
    outcome = result.get("outcome", "UNEVALUABLE")
    delta = result.get("delta")

    left_evidence, right_evidence = _collect_side_evidence(observations, evidence_registry)
    if not left_evidence and not right_evidence:
        _query_digest_fallback(bundle_query, evidence_registry, left_evidence)

    missing_keys = _resolve_missing_keys(outcome, delta, item, result)
    severity, magnitude = _calculate_severity_and_magnitude(outcome, delta)

    subject = bundle_query.get("subject", item.get("subject"))
    metric = bundle_query.get("metric", item.get("metric"))
    if not observations:
        if not subject:
            subject = {"actor": "unknown", "repository": "unknown"}
        if not metric:
            metric = {"id": "unknown"}

    symptom = {
        "subject": subject,
        "metric": metric,
        "outcome": outcome,
        "delta": delta,
        "severity": severity,
        "missing_keys": missing_keys,
        "left_evidence": left_evidence,
        "right_evidence": right_evidence,
    }
    return symptom, magnitude


def _as_bundles(comparison_results: Union[Dict[str, Any], List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    if isinstance(comparison_results, list):
        return comparison_results
    if isinstance(comparison_results, dict):
        return [comparison_results]
    return []


def _symptom_sort_key(entry: Tuple[Dict[str, Any], float]) -> Tuple[int, float, str]:
    s, mag = entry
    sev_rank = SEVERITY_ORDER.get(s["severity"], 0)
    metric_id = str(s.get("metric", {}).get("id", "")) if s.get("metric") else ""
    return (-sev_rank, -mag, metric_id)


def _severity_summary(sorted_symptoms: List[Dict[str, Any]]) -> Dict[str, int]:
    summary = {
        sev: sum(1 for s in sorted_symptoms if s["severity"] == sev)
        for sev in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO")
    }
    summary["total"] = len(sorted_symptoms)
    return summary
