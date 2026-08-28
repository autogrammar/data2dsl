# Ticket 060: Validate comparability in comparator and batch to prevent false matches (F03)

- **ID**: ticket-060
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-28

## Goal and scope

Fix audit finding F03: `DeterministicComparator.compare()` and batch comparator
must validate comparability between query and observations (subject, metric, window, query_id, side).
Mismatches must result in `UNEVALUABLE` or clear rejection rather than producing false `MATCH` outcomes.
Also ensure `Data2DslSkill.execute_compare` validates returned bundles.

SESSION_EXECUTION_AUTHORIZATION recorded from user prompt.

## Acceptance criteria

- [x] AC-01: Scope is approved (SESSION_EXECUTION_AUTHORIZATION recorded).
- [x] AC-02: `DeterministicComparator.compare()` validates that `left` and `right` observation fields match `query` (subject, metric, window, query_id). Mismatched observations result in `UNEVALUABLE`.
- [x] AC-03: `BatchMultiQueryComparator` matches observations by full key (`query_id` or canonical metric ID + subject) and handles missing observations as `None` without false matches.
- [x] AC-04: `Data2DslSkill.execute_compare` rejects / flags invalid comparisons.
- [x] AC-05: Unit tests in `tests/test_comparator_comparability.py` verify rejection of wrong actor, wrong repo, wrong metric, wrong window, and wrong query_id.
- [x] AC-06: Full test suite passes (99/99) and `governance-check.bat` reports GOV-PASS.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
