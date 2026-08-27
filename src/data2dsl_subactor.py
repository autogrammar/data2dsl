"""Subactor delegation envelope conformance and closed-loop self-healing module."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Union

from data2dsl_comparator import DeterministicComparator
from data2dsl_doctor import DiagnosticProfileFormatter
from data2dsl_remediation import RemediationIntentFormatter

VALID_ROLES = {"founder", "supervisor", "observer"}
VALID_AUTHORITY_KEYWORDS = {"observe", "plan", "dry-run", "apply"}


@dataclass
class EnvelopeValidationError:
    code: str
    field_name: str
    message: str


@dataclass
class SubactorDelegationEnvelope:
    role: str
    goal: str
    scope: str
    acceptance: str
    authority: str
    limits: str
    report: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    valid: bool = True
    errors: List[EnvelopeValidationError] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "goal": self.goal,
            "scope": self.scope,
            "acceptance": self.acceptance,
            "authority": self.authority,
            "limits": self.limits,
            "report": self.report,
            "metadata": self.metadata,
            "valid": self.valid,
            "errors": [asdict(e) for e in self.errors],
        }

    def to_text(self) -> str:
        lines = [
            f"ROLE: {self.role}",
            f"GOAL: {self.goal}",
            f"SCOPE: {self.scope}",
            f"ACCEPTANCE: {self.acceptance}",
            f"AUTHORITY: {self.authority}",
            f"LIMITS: {self.limits}",
            f"REPORT: {self.report}",
        ]
        return "\n".join(lines)


def parse_delegation_envelope_text(raw_text: str) -> Dict[str, str]:
    """Parse text format of Subactor delegation envelope."""
    fields: Dict[str, str] = {}
    current_key: Optional[str] = None
    current_value_lines: List[str] = []

    known_keys = {"ROLE", "GOAL", "SCOPE", "ACCEPTANCE", "AUTHORITY", "LIMITS", "REPORT"}

    for line in raw_text.splitlines():
        trimmed = line.strip()
        if not trimmed:
            continue

        match = re.match(r"^([A-Za-z0-9_-]+)\s*:\s*(.*)$", trimmed)
        if match and match.group(1).upper() in known_keys:
            if current_key:
                fields[current_key.lower()] = " ".join(current_value_lines).strip()
            current_key = match.group(1).upper()
            current_value_lines = [match.group(2)] if match.group(2) else []
        else:
            if current_key:
                current_value_lines.append(trimmed)

    if current_key:
        fields[current_key.lower()] = " ".join(current_value_lines).strip()

    return fields


def validate_delegation_envelope(
    payload: Union[str, Dict[str, Any]]
) -> SubactorDelegationEnvelope:
    """Validate a Subactor delegation envelope in string or dictionary form."""
    if isinstance(payload, str):
        trimmed = payload.strip()
        if trimmed.startswith("{") and trimmed.endswith("}"):
            try:
                data = json.loads(trimmed)
            except Exception:
                data = parse_delegation_envelope_text(payload)
        else:
            data = parse_delegation_envelope_text(payload)
    elif isinstance(payload, dict):
        data = payload
    else:
        raise TypeError(f"Payload must be str or dict, got {type(payload)}")

    errors: List[EnvelopeValidationError] = []

    required_fields = ["role", "goal", "scope", "acceptance", "authority", "limits", "report"]
    extracted: Dict[str, str] = {}

    for req in required_fields:
        val = data.get(req)
        if not val or not str(val).strip():
            errors.append(
                EnvelopeValidationError(
                    code="COMM-ENVELOPE-001",
                    field_name=req,
                    message=f"Missing required envelope field '{req}'.",
                )
            )
            extracted[req] = ""
        else:
            extracted[req] = str(val).strip()

    # Validate role
    role = extracted.get("role", "").lower()
    if role and role not in VALID_ROLES:
        errors.append(
            EnvelopeValidationError(
                code="COMM-ROLE-001",
                field_name="role",
                message=f"Invalid role '{role}'. Must be one of: {sorted(list(VALID_ROLES))}.",
            )
        )

    # Validate authority
    authority = extracted.get("authority", "").lower()
    if authority:
        tokens = re.split(r"[\s,+;:|]+", authority)
        has_valid_keyword = any(
            any(kw in tok for kw in VALID_AUTHORITY_KEYWORDS) for tok in tokens if tok
        )
        if not has_valid_keyword:
            errors.append(
                EnvelopeValidationError(
                    code="COMM-AUTH-001",
                    field_name="authority",
                    message=f"Authority '{authority}' does not contain recognized keywords ({sorted(list(VALID_AUTHORITY_KEYWORDS))}).",
                )
            )

    is_valid = len(errors) == 0
    return SubactorDelegationEnvelope(
        role=extracted.get("role", ""),
        goal=extracted.get("goal", ""),
        scope=extracted.get("scope", ""),
        acceptance=extracted.get("acceptance", ""),
        authority=extracted.get("authority", ""),
        limits=extracted.get("limits", ""),
        report=extracted.get("report", ""),
        metadata=data.get("metadata", {}) if isinstance(data.get("metadata"), dict) else {},
        valid=is_valid,
        errors=errors,
    )


def simulate_self_healing_cycle(
    query: Dict[str, Any],
    left_observation: Dict[str, Any],
    right_observation: Dict[str, Any],
) -> Dict[str, Any]:
    """Simulate a DETECT -> PLAN -> EXECUTE -> VERIFY -> HEAL closed loop."""
    comparator = DeterministicComparator()
    doc_formatter = DiagnosticProfileFormatter()
    rem_formatter = RemediationIntentFormatter()

    # 1. DETECT: Compare initial observations
    pre_bundle = comparator.compare(query, left_observation, right_observation)

    # 2. PLAN: Generate diagnostic profile & remediation intent
    diag_profile = doc_formatter.format_profile(pre_bundle)
    rem_intent = rem_formatter.format_intent(pre_bundle)

    # 3. EXECUTE: Synthesize repair actions on right observation
    repaired_right = json.loads(json.dumps(right_observation))

    if "value" in left_observation and "value" in repaired_right:
        repaired_right["value"] = json.loads(json.dumps(left_observation["value"]))

    if "evidence" in repaired_right and isinstance(repaired_right["evidence"], list):
        if len(repaired_right["evidence"]) > 0 and isinstance(repaired_right["evidence"][0], dict):
            ev = dict(repaired_right["evidence"][0])
            ev["evidence_id"] = str(ev.get("evidence_id", "ev:repaired:1")) + ":repaired"
            ev["source_uri"] = str(ev.get("source_uri", "")) + "#repaired"
            repaired_right["evidence"] = [ev]

    # 4. VERIFY: Re-compare post repair
    post_bundle = comparator.compare(query, left_observation, repaired_right)

    # 5. HEAL: Re-generate remediation intent to verify all items are SATISFIED
    post_rem_intent = rem_formatter.format_intent(post_bundle)

    all_satisfied = post_rem_intent.get("status") == "SATISFIED"
    is_clean = post_bundle.get("result", {}).get("outcome") == "MATCH"
    status = "HEALED" if (all_satisfied and is_clean) else "FAILED"

    actionable_count = len(rem_intent.get("actionable_items", []))

    return {
        "status": status,
        "pre_repair": {
            "outcome": pre_bundle.get("result", {}).get("outcome"),
            "delta": pre_bundle.get("result", {}).get("delta"),
            "diagnostic_severity_summary": diag_profile.get("severitySummary"),
            "remediation_status": rem_intent.get("status"),
            "remediation_summary": rem_intent.get("summary"),
            "evidence_ids": pre_bundle.get("result", {}).get("evidence_ids"),
        },
        "remediation_actions_applied": actionable_count,
        "post_repair": {
            "outcome": post_bundle.get("result", {}).get("outcome"),
            "delta": post_bundle.get("result", {}).get("delta"),
            "remediation_status": post_rem_intent.get("status"),
            "remediation_summary": post_rem_intent.get("summary"),
            "evidence_ids": post_bundle.get("result", {}).get("evidence_ids"),
        },
        "closed_loop_verification": {
            "outcome_before": pre_bundle.get("result", {}).get("outcome"),
            "outcome_after": post_bundle.get("result", {}).get("outcome"),
            "is_clean": is_clean,
        },
    }
