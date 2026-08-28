# Antigravity agent plan — ticket-063

## Objective

Fix audit finding F06: Fix evidence digest computation across adapters to ensure cryptographic integrity.

## SESSION_EXECUTION_AUTHORIZATION

Recorded from user prompt in conversation 78d87a8b-d52c-4b44-b8f5-077656700b95.

## Changes made

### 1. `src/data2dsl_adapters.py`
- **OqlTelemetryAdapter**: Fixed `normalize_spec` and `normalize_telemetry` digest calculations. Instead of `val_obj.get("value", "")` (which produced empty strings for string-set values like pins/buses), now serialize string-set items via `",".join(sorted(str(i) for i in val_obj["items"]))`. Different pin configurations now produce unique SHA-256 digests.
- **DetaAdapter**: In empty-services fallback digest, included `response.service_count` and sorted `response.ports`.
- **IntentContractAdapter**: In contract digest calculation, included sorted `parties`, sorted `obligations`, sorted `deliverables`, and canonical representation of `val_obj`.

### 2. `tests/test_evidence_digests.py`
- Added 4 unit tests verifying digest uniqueness when:
  - OQL spec pins change
  - OQL telemetry log pins change
  - Deta ports or counts change
  - IntentContract parties change

## Verification

- `pytest tests/test_evidence_digests.py`: 4/4 passed.
- Full pytest suite: 112/112 passed.
- Ruff: passed.
