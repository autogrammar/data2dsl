# Ticket Changelog (ticket-038)

## [0.1.0] - 2026-08-24

- Extended `DeterministicComparator` in `src/data2dsl_comparator.py` with `float` and `percentage` comparison algorithms.
- Extended `src/data2dsl_contract_v0/comparison.schema.json` with `floatValue`, `percentageValue`, `floatDelta`, `percentageDelta`, and equality policies.
- Updated `src/data2dsl_contract_v0/validate.py` conformance checks for `float` and `percentage`.
- Added unit test cases `test_float_comparator_match_and_conflict` and `test_percentage_comparator_match_and_conflict` in `tests/test_golden_case_e2e.py` (33 total passing).
- Verified deterministic governance gate passes.
