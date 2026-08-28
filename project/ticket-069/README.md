# Ticket 069: Tighten subactor authority token matching and fix diagnostic summary key (F13)

- **ID**: ticket-069
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: VALIDATION
- **Created**: 2026-08-28

## Goal and scope

Fix audit finding F13:
1. In `src/data2dsl_subactor.py`, replace loose substring matching for authority tokens (`kw in tok`) with exact token matching (`tok in VALID_AUTHORITY_KEYWORDS`) to prevent unauthorized tokens (e.g. `unauthorized_autonomous`) from passing validation.
2. In `simulate_self_healing_cycle`, fix the diagnostic severity summary dictionary access so that `"diagnostic_severity_summary"` receives the summary dictionary (`diag_profile.get("summary")`).

SESSION_EXECUTION_AUTHORIZATION recorded from user prompt.

## Acceptance criteria

- [x] AC-01: Scope is approved (SESSION_EXECUTION_AUTHORIZATION recorded).
- [x] AC-02: `validate_delegation_envelope` validates authority tokens using exact token equality against `VALID_AUTHORITY_KEYWORDS`.
- [x] AC-03: `simulate_self_healing_cycle` correctly captures diagnostic summary in `"diagnostic_severity_summary"`.
- [x] AC-04: Unit tests in `tests/test_subactor_f13.py` pass.
- [x] AC-05: Full pytest suite passes (123/123) and `governance-check.bat` reports GOV-PASS.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
