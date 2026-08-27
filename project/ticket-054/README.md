# Ticket 054: Batch Multi-Query Comparison Engine and CLI

- **ID**: ticket-054
- **Owner**: unresolved:human
- **Status**: PLAN
- **Workflow state**: PUBLICATION
- **Created**: 2026-08-27
- **Receipt**: Implemented BatchMultiQueryComparator and data2dsl batch CLI subcommand with clean ratio aggregation; 79/79 pytest tests passing and GOV-PASS.

## Goal and scope

Implement Batch Multi-Query Comparison Engine and CLI integration:
1. Implement `src/data2dsl_batch.py` with `BatchMultiQueryComparator` capable of evaluating lists of queries against left and right observation pools.
2. Aggregate batch summary metrics (`total_queries`, `matches`, `conflicts`, `missing_left`, `missing_right`, `unevaluable`, `clean_ratio`).
3. Add CLI subcommand `data2dsl batch --queries <queries.json> --left <left_obs.json> --right <right_obs.json> [--output <report.json>]`.
4. Add unit and E2E test suites in `tests/test_batch_compare.py`.
5. Verify all tests pass cleanly and deterministic governance gate passes (`GOV-PASS`).

## Acceptance criteria

- [x] AC-01: `BatchMultiQueryComparator` evaluates a collection of queries and returns a structured `BatchComparisonReport`.
- [x] AC-02: `data2dsl batch` CLI command executes with JSON output and proper exit codes (0 on full match, 1 on conflicts/errors).
- [x] AC-03: Unit and CLI tests pass in `tests/test_batch_compare.py`.
- [x] AC-04: Full pytest test suite and governance check pass (`GOV-PASS`).

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
