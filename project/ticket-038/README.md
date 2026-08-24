# Ticket 038: Quality gates: Float and Percentage comparator with pyqual stage integration

- **ID**: ticket-038
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-08-24

## Goal and scope

Expand the `DeterministicComparator` capabilities by adding support for `float`
and `percentage` metric types (needed for quality gate metrics like code2llm
health scores, cyclomatic complexity averages, test coverage percentages, and
pyqual gate thresholds).

## Acceptance criteria

- [x] AC-01: `DeterministicComparator` handles `float` values, producing `MATCH` or `CONFLICT` with typed arithmetic float deltas.
- [x] AC-02: `DeterministicComparator` handles `percentage` values (e.g. `95.5` or `95.5%`), producing `MATCH` or `CONFLICT` with percentage deltas.
- [x] AC-03: `comparison.schema.json` is updated with `float` and `percentage` schema definitions.
- [x] AC-04: Unit tests for float and percentage comparisons pass in `tests/test_golden_case_e2e.py`.
- [x] AC-05: The deterministic governance gate passes.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
