# Antigravity agent plan — ticket-060

## Objective

Fix audit finding F03: Comparability validation in `DeterministicComparator` and `BatchMultiQueryComparator`.

## SESSION_EXECUTION_AUTHORIZATION

Recorded from user prompt in conversation 78d87a8b-d52c-4b44-b8f5-077656700b95.

## Changes made

### 1. `src/data2dsl_comparator.py`
- Added `_is_compatible(query, obs)` method validating:
  - `obs.subject == query.subject` (actor, repository)
  - `obs.metric == query.metric` (id, value_kind)
  - `obs.window == query.window` (start, end)
  - `obs.query_id == query.query_id` (if present)
- In `compare()`, if either observation fails compatibility, outcome is strictly set to `UNEVALUABLE` and delta is `None`.

### 2. `src/data2dsl_batch.py`
- Updated batch observation indexing to use full composite key `(repository, actor, metric_id)` in addition to `query_id`.
- Eliminated synthesis of fake `state: "MISSING"` observation objects; passes `None` directly to comparator so `MISSING_LEFT` / `MISSING_RIGHT` are computed accurately.
- Fixed report formatting (`_format_val`, `_format_delta`) to handle sets, strings, missing values without `AttributeError`.

### 3. `tests/test_comparator_comparability.py`
- Added 8 targeted test cases verifying rejection of mismatched actor, repository, metric id, value kind, window, query_id, and cross-query batch false matches.

## Verification

- `pytest tests/test_comparator_comparability.py`: 8/8 passed.
- Full pytest suite: 99/99 passed.
- Ruff: passed.
