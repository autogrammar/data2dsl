# Antigravity agent plan — ticket-067

## Objective

Fix audit finding F09: Resolve remediation schema collision by changing the feed schema identifier and ensuring proper bundle structure.

## SESSION_EXECUTION_AUTHORIZATION

Recorded from user prompt in conversation 78d87a8b-d52c-4b44-b8f5-077656700b95.

## Changes made

### 1. `src/data2dsl_remediation.py`
- Changed `RemediationIntentFormatter.SCHEMA_VERSION` from `new-project.remediation-intent/v1` to `autogrammar.data2dsl/remediation-feed/v0` to eliminate schema collision with `.governance/remediation-intent.schema.json`.

### 2. `tests/test_remediation_feed.py` and `tests/test_remediation_f09.py`
- Updated schema assertions in unit and CLI feed tests.
- Added tests verifying schema separation and top-level feed properties.

## Verification

- `pytest tests/test_remediation_feed.py tests/test_remediation_f09.py`: 9/9 passed.
- Full pytest suite: 119/119 passed.
- Ruff: passed.
