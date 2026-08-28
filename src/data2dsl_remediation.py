"""Koru Remediation Intent Generator for closed-loop self-healing.

Conforms to docs/research-koru-closed-loop.md:
- Transforms data2dsl comparison bundles into actionable remediation-intent manifests.
- Supports deterministic status mapping (PROPOSED, SATISFIED, BLOCKED).
- Generates typed actionable items (synchronize_metric, restore_missing_entries, resolve_conflict).
- Constructs cryptographically pinned SHA-256 evidence digests.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence, Union


def _extract_evidence(obs: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not obs or not isinstance(obs, dict):
        return []
    evidence_list = obs.get("evidence", [])
    if not isinstance(evidence_list, list):
        return []
    out: List[Dict[str, Any]] = []
    for ev in evidence_list:
        if isinstance(ev, dict):
            out.append({
                "evidence_id": str(ev.get("evidence_id", "")),
                "target_uri": str(ev.get("target_uri", "")),
                "source_uri": str(ev.get("source_uri", "")),
                "source_revision": str(ev.get("source_revision", "")),
                "media_type": str(ev.get("media_type", "application/json")),
                "digest_sha256": str(ev.get("digest_sha256", "")),
                "extractor": dict(ev.get("extractor", {})),
                "location": dict(ev.get("location", {})),
            })
    return out


class RemediationIntentFormatter:
    """Formats comparison bundles into structured remediation intents for semcod/koru."""

    SCHEMA_VERSION = "autogrammar.data2dsl/remediation-feed/v0"
    REMEDIATION_VERSION = "1.0.0"

    @classmethod
    def format_intent(
        cls,
        comparison_results: Union[Dict[str, Any], Sequence[Dict[str, Any]]],
        target_repo: Optional[str] = None,
        ticket_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Format comparison bundle(s) into a unified remediation-intent dictionary."""
        bundles: List[Dict[str, Any]] = []
        if isinstance(comparison_results, dict):
            bundles = [comparison_results]
        elif isinstance(comparison_results, (list, tuple)):
            bundles = list(comparison_results)

        actionable_items: List[Dict[str, Any]] = []
        evidence_digests: set[str] = set()

        outcomes: List[str] = []

        resolved_ticket = ticket_id

        for bundle in bundles:
            query = bundle.get("query", {})
            result = bundle.get("result", bundle if "outcome" in bundle else {})
            observations = bundle.get("observations", [])

            if not resolved_ticket:
                resolved_ticket = (
                    bundle.get("ticket_id")
                    or query.get("ticket_id")
                    or bundle.get("ticket")
                    or query.get("ticket")
                )

            outcome = result.get("outcome", "UNEVALUABLE")
            outcomes.append(outcome)
            delta = result.get("delta")

            subject = query.get("subject") if query else bundle.get("subject")
            metric = query.get("metric") if query else bundle.get("metric")

            # Extract observations by side
            obs_by_side = {
                obs.get("side"): obs
                for obs in observations
                if isinstance(obs, dict)
            }
            left_evidence = _extract_evidence(obs_by_side.get("left"))
            right_evidence = _extract_evidence(obs_by_side.get("right"))

            for ev in left_evidence + right_evidence:
                sha = ev.get("digest_sha256")
                if sha:
                    evidence_digests.add(sha)

            # Determine target subject identifier
            if target_repo:
                target_subj = target_repo
            elif isinstance(subject, dict) and subject.get("repository"):
                target_subj = str(subject["repository"])
            elif subject:
                target_subj = str(subject)
            else:
                target_subj = "unknown"

            metric_id = (
                metric.get("id", str(metric))
                if isinstance(metric, dict)
                else str(metric)
            )

            # Build actionable item if outcome is not MATCH
            if outcome == "CONFLICT":
                if delta and delta.get("kind") in ("percentage", "integer", "float"):
                    action = "synchronize_metric"
                    val = delta.get("value", "")
                    description = (
                        f"Synchronize metric '{metric_id}' on '{target_subj}' "
                        f"with required delta {val}."
                    )
                elif delta and delta.get("kind") == "string-set":
                    action = "resolve_conflict"
                    added = len(delta.get("added", []))
                    removed = len(delta.get("removed", []))
                    description = (
                        f"Resolve set conflict for '{metric_id}' on '{target_subj}' "
                        f"({added} added, {removed} removed)."
                    )
                else:
                    action = "synchronize_metric"
                    description = (
                        f"Resolve conflict for metric '{metric_id}' on '{target_subj}'."
                    )

                actionable_items.append({
                    "action": action,
                    "target_subject": target_subj,
                    "subject": subject,
                    "metric": metric,
                    "outcome": outcome,
                    "required_delta": delta,
                    "left_evidence": left_evidence,
                    "right_evidence": right_evidence,
                    "description": description,
                })
            elif outcome in ("MISSING_LEFT", "MISSING_RIGHT"):
                actionable_items.append({
                    "action": "restore_missing_entries",
                    "target_subject": target_subj,
                    "subject": subject,
                    "metric": metric,
                    "outcome": outcome,
                    "required_delta": delta,
                    "left_evidence": left_evidence,
                    "right_evidence": right_evidence,
                    "description": (
                        f"Restore missing observation data for '{metric_id}' on '{target_subj}' "
                        f"({outcome})."
                    ),
                })
            elif outcome == "UNEVALUABLE":
                actionable_items.append({
                    "action": "investigate_missing_telemetry",
                    "target_subject": target_subj,
                    "subject": subject,
                    "metric": metric,
                    "outcome": outcome,
                    "required_delta": delta,
                    "left_evidence": left_evidence,
                    "right_evidence": right_evidence,
                    "description": (
                        f"Investigate unevaluable observation for '{metric_id}' on '{target_subj}'."
                    ),
                })

        # Determine overall status
        if not outcomes or all(o == "MATCH" for o in outcomes):
            status = "SATISFIED"
        elif any(o in ("CONFLICT", "MISSING_LEFT", "MISSING_RIGHT") for o in outcomes):
            status = "PROPOSED"
        elif any(o == "UNEVALUABLE" for o in outcomes):
            status = "BLOCKED"
        else:
            status = "PROPOSED"

        # Generate summary description
        if status == "SATISFIED":
            summary = (
                "All observed metrics match expected contracts. "
                "Verification satisfied; no remediation required."
            )
        elif status == "BLOCKED":
            summary = (
                f"Remediation blocked: {len(actionable_items)} unevaluable item(s) detected. "
                "Missing telemetry must be restored first."
            )
        else:
            actions_summary = ", ".join(sorted(set(item["action"] for item in actionable_items)))
            summary = (
                f"Proposed remediation for {len(actionable_items)} actionable item(s): "
                f"{actions_summary}."
            )

        timestamp = datetime.now(timezone.utc).isoformat()

        return {
            "schema": cls.SCHEMA_VERSION,
            "ticket": resolved_ticket or "remediation-intent-auto",
            "remediation_version": cls.REMEDIATION_VERSION,
            "timestamp": timestamp,
            "status": status,
            "actionable_items": actionable_items,
            "evidence_digest": sorted(evidence_digests),
            "summary": summary,
        }


def format_remediation_intent(
    comparison_results: Union[Dict[str, Any], Sequence[Dict[str, Any]]],
    target_repo: Optional[str] = None,
    ticket_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Helper function to format comparison results into a remediation intent."""
    return RemediationIntentFormatter.format_intent(
        comparison_results, target_repo=target_repo, ticket_id=ticket_id
    )
