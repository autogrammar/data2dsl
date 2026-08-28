# Antigravity agent plan — ticket-068

## Objective

Fix audit findings F10 and F12:
- F10: Fix batch missing observation lookup to prevent query_id mismatches and properly record `MISSING_LEFT` and `MISSING_RIGHT`.
- F12: Format missing observations and string-set values cleanly in markdown tables.

## SESSION_EXECUTION_AUTHORIZATION

Recorded from user prompt in conversation 78d87a8b-d52c-4b44-b8f5-077656700b95.

## Changes made

### 1. `src/data2dsl_batch.py`
- Updated `BatchMultiQueryComparator.compare_batch` to ensure fallback index `left_by_key`/`right_by_key` only matches candidate observations whose `query_id` is empty or matches the target query ID, ensuring true missing observations result in `MISSING_LEFT` or `MISSING_RIGHT`.
- Updated `_format_val` and `_format_delta` to render missing values as `(missing)` and format collections cleanly while escaping markdown pipe characters.

### 2. `tests/test_batch_f10_f12.py`
- Added tests verifying `MISSING_LEFT` and `MISSING_RIGHT` counter increments and report markdown formatting.

## Verification

- `pytest tests/test_batch_f10_f12.py`: 2/2 passed.
- Full pytest suite: 121/121 passed.
- Ruff: passed.
