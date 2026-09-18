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
            item, outcome, resolved_ticket = _process_bundle(
                bundle, resolved_ticket, target_repo, evidence_digests
            )
            outcomes.append(outcome)
            if item is not None:
                actionable_items.append(item)

        status = _overall_status(outcomes)
        summary = _status_summary(status, actionable_items)

        return {
            "schema": cls.SCHEMA_VERSION,
            "ticket": resolved_ticket or "remediation-intent-auto",
            "remediation_version": cls.REMEDIATION_VERSION,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": status,
            "actionable_items": actionable_items,
            "evidence_digest": sorted(evidence_digests),
            "summary": summary,
        }


def _bundle_ticket(bundle: Dict[str, Any], query: Dict[str, Any]) -> Optional[str]:
    return (
        bundle.get("ticket_id")
        or query.get("ticket_id")
        or bundle.get("ticket")
        or query.get("ticket")
    )


def _bundle_context(query: Dict[str, Any], bundle: Dict[str, Any]) -> tuple:
    """Resolve subject/metric with defaults from query or bundle."""
    subject = query.get("subject", bundle.get("subject")) if query else bundle.get("subject")
    metric = query.get("metric", bundle.get("metric")) if query else bundle.get("metric")
    if not subject:
        subject = {"actor": "unknown", "repository": "unknown"}
    if not metric:
        metric = {"id": "unknown"}
    return subject, metric


def _collect_digests(
    query: Dict[str, Any],
    bundle: Dict[str, Any],
    outcome: str,
    evidence: List[Dict[str, Any]],
    evidence_digests: set,
) -> None:
    if outcome == "MATCH":
        qd = query.get("digest") if query else bundle.get("digest")
        if qd:
            evidence_digests.add(qd)
    for ev in evidence:
        sha = ev.get("digest_sha256")
        if sha:
            evidence_digests.add(sha)


def _process_bundle(
    bundle: Dict[str, Any],
    resolved_ticket: Optional[str],
    target_repo: Optional[str],
    evidence_digests: set,
) -> tuple:
    """Process one comparison bundle into an optional actionable item."""
    query = bundle.get("query", {})
    result = bundle.get("result", bundle if "outcome" in bundle else {})
    observations = bundle.get("observations", [])

    if not resolved_ticket:
        resolved_ticket = _bundle_ticket(bundle, query)

    outcome = result.get("outcome", "UNEVALUABLE")
    delta = result.get("delta")
    subject, metric = _bundle_context(query, bundle)

    obs_by_side = {
        obs.get("side"): obs for obs in observations if isinstance(obs, dict)
    }
    if not observations:
        outcome = "UNEVALUABLE"
        delta = {"message": "Both observations absent."}

    left_evidence = _extract_evidence(obs_by_side.get("left"))
    right_evidence = _extract_evidence(obs_by_side.get("right"))
    _collect_digests(query, bundle, outcome, left_evidence + right_evidence, evidence_digests)

    target_subj = _target_subject(target_repo, subject)
    metric_id = metric.get("id", str(metric)) if isinstance(metric, dict) else str(metric)

    item = _action_item(
        outcome, delta, target_subj, subject, metric, left_evidence, right_evidence, metric_id
    )
    return item, outcome, resolved_ticket


def _target_subject(target_repo: Optional[str], subject: Any) -> str:
    if target_repo:
        return target_repo
    if isinstance(subject, dict) and subject.get("repository"):
        return str(subject["repository"])
    if subject:
        return str(subject)
    return "unknown"


def _conflict_action(
    delta: Optional[Dict[str, Any]], metric_id: str, target_subj: str
) -> tuple:
    if delta and delta.get("kind") in ("percentage", "integer", "float"):
        val = delta.get("value", "")
        return (
            "synchronize_metric",
            f"Synchronize metric '{metric_id}' on '{target_subj}' with required delta {val}.",
        )
    if delta and delta.get("kind") == "string-set":
        added = len(delta.get("added", []))
        removed = len(delta.get("removed", []))
        return (
            "resolve_conflict",
            f"Resolve set conflict for '{metric_id}' on '{target_subj}' "
            f"({added} added, {removed} removed).",
        )
    return (
        "synchronize_metric",
        f"Resolve conflict for metric '{metric_id}' on '{target_subj}'.",
    )


def _action_item(
    outcome: str,
    delta: Optional[Dict[str, Any]],
    target_subj: str,
    subject: Any,
    metric: Any,
    left_evidence: List[Dict[str, Any]],
    right_evidence: List[Dict[str, Any]],
    metric_id: str,
) -> Optional[Dict[str, Any]]:
    if outcome == "CONFLICT":
        action, description = _conflict_action(delta, metric_id, target_subj)
    elif outcome in ("MISSING_LEFT", "MISSING_RIGHT"):
        action = "restore_missing_entries"
        description = (
            f"Restore missing observation data for '{metric_id}' on '{target_subj}' "
            f"({outcome})."
        )
    elif outcome == "UNEVALUABLE":
        action = "investigate_missing_telemetry"
        description = (
            f"Investigate unevaluable observation for '{metric_id}' on '{target_subj}'."
        )
    else:
        return None
    return {
        "action": action,
        "target_subject": target_subj,
        "subject": subject,
        "metric": metric,
        "outcome": outcome,
        "required_delta": delta,
        "left_evidence": left_evidence,
        "right_evidence": right_evidence,
        "description": description,
    }


def _overall_status(outcomes: List[str]) -> str:
    if not outcomes or all(o == "MATCH" for o in outcomes):
        return "SATISFIED"
    if any(o in ("CONFLICT", "MISSING_LEFT", "MISSING_RIGHT") for o in outcomes):
        return "PROPOSED"
    if any(o == "UNEVALUABLE" for o in outcomes):
        return "BLOCKED"
    return "PROPOSED"


def _status_summary(status: str, actionable_items: List[Dict[str, Any]]) -> str:
    if status == "SATISFIED":
        return (
            "All observed metrics match expected contracts. "
            "Verification satisfied; no remediation required."
        )
    if status == "BLOCKED":
        return (
            f"Remediation blocked: {len(actionable_items)} unevaluable item(s) detected. "
            "Missing telemetry must be restored first."
        )
    actions_summary = ", ".join(sorted(set(item["action"] for item in actionable_items)))
    return (
        f"Proposed remediation for {len(actionable_items)} actionable item(s): "
        f"{actions_summary}."
    )


def format_remediation_intent(
    comparison_results: Union[Dict[str, Any], Sequence[Dict[str, Any]]],
    target_repo: Optional[str] = None,
    ticket_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Helper function to format comparison results into a remediation intent."""
    return RemediationIntentFormatter.format_intent(
        comparison_results, target_repo=target_repo, ticket_id=ticket_id
    )
