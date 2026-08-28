# Antigravity agent plan — ticket-061

## Objective

Fix audit findings F04 (Markdown actor claim isolation) and F05 (metric.id mapping across adapters).

## SESSION_EXECUTION_AUTHORIZATION

Recorded from user prompt in conversation 78d87a8b-d52c-4b44-b8f5-077656700b95.

## Changes made

### 1. `src/data2dsl_adapters.py`
- **F04**: Fixed `extract_commit_claim` (line 235) to require matching `normalized_actor in line_lower` instead of `or "commit" in line_lower`. This prevents lines belonging to other actors from being incorrectly attributed.
- **F05 (DetaAdapter)**: Updated property detection to inspect `metric.get("id")` and `metric.get("name")` for ports vs service topology.
- **F05 (IntentContractAdapter)**: Updated property extraction to inspect `metric.get("id")` for `party`/`parties`, `obligation`/`obligations`, and `deliverable`/`deliverables` (both singular and plural forms). Unrecognized metrics return `UNEVALUABLE`.
- **F05 (OqlTelemetryAdapter)**: Updated `normalize_spec` and `normalize_telemetry` to map metrics using `metric.get("id")`. For missing sensor/log measurements (`raw_val is None`) and unrecognized metric IDs, observations are marked `state: "UNEVALUABLE"` with `value: None` instead of falling back to misleading `0.0` values.

### 2. `tests/test_adapters_f04_f05.py`
- Added 5 unit tests verifying:
  - Markdown actor isolation with multi-actor document
  - Deta metric mapping for ports vs services
  - IntentContract metric mapping for parties
  - OQL telemetry preservation of distinct measurements (100 Hz vs 42 Hz)
  - OQL unknown metric rejection as UNEVALUABLE

## Verification

- `pytest tests/test_adapters_f04_f05.py`: 5/5 passed.
- Full pytest suite: 104/104 passed.
- Ruff: passed.
