# Ticket 068: Fix batch missing observation handling and markdown report formatting (F10, F12)

- **ID**: ticket-068
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-28

## Goal and scope

Fix audit findings F10 and F12:
1. **F10**: Ensure `BatchMultiQueryComparator` directly passes `None` for absent observations into `DeterministicComparator.compare(query, left_obs, right_obs)` instead of synthesizing non-contractual dummy observations. Verify `MISSING_LEFT`, `MISSING_RIGHT`, and both-missing cases.
2. **F12**: Improve `format_markdown_report` so missing values and string-set values render cleanly as `(missing)` / `(unevaluable)` / set items without formatting errors.

SESSION_EXECUTION_AUTHORIZATION recorded from user prompt.

## Acceptance criteria

- [x] AC-01: Scope is approved (SESSION_EXECUTION_AUTHORIZATION recorded).
- [x] AC-02: `BatchMultiQueryComparator` cleanly handles absent left/right observations yielding `MISSING_LEFT`, `MISSING_RIGHT`, and increments summary metrics correctly.
- [x] AC-03: `format_markdown_report` correctly formats missing observations and string-set delta values in markdown tables.
- [x] AC-04: Unit tests in `tests/test_batch_f10_f12.py` pass.
- [x] AC-05: Full pytest suite passes (121/121) and `governance-check.bat` reports GOV-PASS.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
