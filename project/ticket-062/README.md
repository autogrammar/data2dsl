# Ticket 062: Harmonize float and percentage comparison semantics between comparator and validator (F11)

- **ID**: ticket-062
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-28

## Goal and scope

Fix audit finding F11:
`DeterministicComparator` in `data2dsl_comparator.py` allowed float / percentage epsilon tolerances (`1e-9` / `1e-6`), whereas contract validator `validate.py` enforced exact canonical equality `_canonical_value(left) == _canonical_value(right)`.
Harmonize the comparator and validator semantics so that:
1. Exact equality policies (`float-exact`, `percentage-exact`) produce MATCH if and only if values are strictly canonically equal or within agreed contract precision.
2. The validator in `data2dsl_contract_v0/validate.py` and `DeterministicComparator` in `data2dsl_comparator.py` agree on MATCH/CONFLICT outcomes for all float and percentage values.

SESSION_EXECUTION_AUTHORIZATION recorded from user prompt.

## Acceptance criteria

- [x] AC-01: Scope is approved (SESSION_EXECUTION_AUTHORIZATION recorded).
- [x] AC-02: `DeterministicComparator` and `validate.py` evaluate float and percentage comparisons identically.
- [x] AC-03: `validate_document(bundle)` passes for all valid comparison bundles produced by `DeterministicComparator`.
- [x] AC-04: Unit tests in `tests/test_float_percentage_harmony.py` verify edge cases (exact equality, near-zero differences, percentage formatting).
- [x] AC-05: Full pytest suite passes (108/108) and `governance-check.bat` reports GOV-PASS.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
