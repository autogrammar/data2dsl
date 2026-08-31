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


def _calculate_severity_and_magnitude(
    outcome: str, delta: Optional[Dict[str, Any]]
) -> Tuple[str, float]:
    """Calculate deterministic severity and priority magnitude for triage sorting."""
    if outcome == "CONFLICT":
        if delta is not None:
            kind = delta.get("kind")
            if kind == "percentage":
                raw_str = str(delta.get("value", "0")).rstrip("%").strip()
                try:
                    val = abs(float(raw_str))
                except (ValueError, TypeError):
                    val = 0.0
                if val >= 20.0:
                    return "CRITICAL", val
                elif val >= 10.0:
                    return "HIGH", val
                elif val >= 5.0:
                    return "MEDIUM", val
                else:
                    return "LOW", val
            elif kind == "integer":
                try:
                    val = abs(int(delta.get("value", 0)))
                except (ValueError, TypeError):
                    val = 0
                if val >= 50:
                    return "CRITICAL", float(val)
                elif val >= 10:
                    return "HIGH", float(val)
                elif val >= 3:
                    return "MEDIUM", float(val)
                else:
                    return "LOW", float(val)
            elif kind == "float":
                try:
                    val = abs(float(delta.get("value", 0.0)))
                except (ValueError, TypeError):
                    val = 0.0
                if val >= 50.0:
                    return "CRITICAL", val
                elif val >= 10.0:
                    return "HIGH", val
                elif val >= 1.0:
                    return "MEDIUM", val
                else:
                    return "LOW", val
            elif kind == "string-set":
                added = delta.get("added", [])
                removed = delta.get("removed", [])
                cnt = len(added) + len(removed)
                if cnt >= 10:
                    return "CRITICAL", float(cnt)
                elif cnt >= 5:
                    return "HIGH", float(cnt)
                elif cnt >= 1:
                    return "MEDIUM", float(cnt)
                else:
                    return "LOW", float(cnt)
        return "HIGH", 10.0
    elif outcome == "UNEVALUABLE":
        return "HIGH", 50.0
    elif outcome in ("MISSING_LEFT", "MISSING_RIGHT"):
        return "HIGH", 40.0
    elif outcome == "MATCH":
        return "INFO", 0.0
    else:
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
        bundles: List[Dict[str, Any]] = []
        if isinstance(comparison_results, list):
            bundles = comparison_results
        elif isinstance(comparison_results, dict):
            bundles = [comparison_results]

        symptoms_raw: List[Tuple[Dict[str, Any], float]] = []
        evidence_registry: Dict[str, EvidenceRef] = {}

        for item in bundles:
            bundle_query = item.get("query", query) or {}
            result = item.get("result", item if "outcome" in item else {})
            observations = item.get("observations", [])

            outcome = result.get("outcome", "UNEVALUABLE")
            delta = result.get("delta")

            # Extract left and right observations
            obs_by_side = {obs.get("side"): obs for obs in observations if isinstance(obs, dict)}
            left_obs = obs_by_side.get("left")
            right_obs = obs_by_side.get("right")

            left_evidence: List[Dict[str, Any]] = []
            right_evidence: List[Dict[str, Any]] = []

            if left_obs:
                for ev in left_obs.get("evidence", []):
                    ref = _extract_evidence_ref(ev)
                    evidence_registry[ref.evidence_id] = ref
                    left_evidence.append(ref.to_dict())

            if right_obs:
                for ev in right_obs.get("evidence", []):
                    ref = _extract_evidence_ref(ev)
                    evidence_registry[ref.evidence_id] = ref
                    right_evidence.append(ref.to_dict())

            if not left_evidence and not right_evidence:
                qd = bundle_query.get("digest")
                if qd:
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
                    evidence_registry[minimal_ref.evidence_id] = minimal_ref
                    left_evidence.append(minimal_ref.to_dict())

            # Missing keys resolution
            missing_keys: List[str] = []
            if outcome == "MISSING_LEFT":
                missing_keys = ["left"]
            elif outcome == "MISSING_RIGHT":
                missing_keys = ["right"]
            elif delta and delta.get("kind") == "string-set":
                missing_keys = list(delta.get("removed", []))
            elif "missing_in_right" in item:
                missing_keys = list(item["missing_in_right"])
            elif "missing_in_right" in result:
                missing_keys = list(result["missing_in_right"])

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
            symptoms_raw.append((symptom, magnitude))

        # Sort symptoms by severity (descending), magnitude (descending), then metric id
        def sort_key(entry: Tuple[Dict[str, Any], float]) -> Tuple[int, float, str]:
            s, mag = entry
            sev_rank = SEVERITY_ORDER.get(s["severity"], 0)
            metric_id = str(s.get("metric", {}).get("id", "")) if s.get("metric") else ""
            return (-sev_rank, -mag, metric_id)

        symptoms_raw.sort(key=sort_key)
        sorted_symptoms = [s for s, _ in symptoms_raw]

        # Calculate summary counts
        summary = {
            "CRITICAL": sum(1 for s in sorted_symptoms if s["severity"] == "CRITICAL"),
            "HIGH": sum(1 for s in sorted_symptoms if s["severity"] == "HIGH"),
            "MEDIUM": sum(1 for s in sorted_symptoms if s["severity"] == "MEDIUM"),
            "LOW": sum(1 for s in sorted_symptoms if s["severity"] == "LOW"),
            "INFO": sum(1 for s in sorted_symptoms if s["severity"] == "INFO"),
            "total": len(sorted_symptoms),
        }

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
