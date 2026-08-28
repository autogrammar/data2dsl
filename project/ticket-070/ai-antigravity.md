# Antigravity agent plan — ticket-070

## Objective

Fix audit finding F14: Fix runnable examples 01 through 08 and synchronize README documentation with implemented features.

## SESSION_EXECUTION_AUTHORIZATION

Recorded from user prompt in conversation 78d87a8b-d52c-4b44-b8f5-077656700b95.

## Changes made

### 1. `examples/`
- `examples/01-markdown-github-comparison/expected-bundle.json`: Updated schema identifier to `autogrammar.data2dsl/comparison-bundle/v0`, added `profile_bindings`, valid `source_revision`, and `v1` metric version.
- `examples/02-oql-telemetry-verification/expected-bundle.json`: Fixed location kinds to `oql-scenario`/`oql-telemetry-log`, updated `metric.version` to `v1`, added `profile_bindings`.
- `examples/05-mcp-tool-dispatch/mcp-request.json`: Added complete query fields (`window`, `left_source`, `right_source`, `comparison`).
- `examples/07-sumd-table-comparison/README.md`: Corrected CLI parameter `--left-source-type`.
- `examples/08-batch-multi-query/`: Added missing evidence fields (`target_uri`, `media_type`, `extractor`, `location`) and canonical equality values (`integer-exact`, `percentage-exact`).

### 2. `README.md`
- Synchronized description to reflect completed factual comparison layer.
- Corrected list of MCP tools in `Data2DslSkill` and updated test pass numbers (127/127).

### 3. `tests/test_examples_integrity.py`
- Added comprehensive automated test validating examples 01, 02, 05, and 08.

## Verification

- `pytest tests/test_examples_integrity.py`: 4/4 passed.
- Full pytest suite: 127/127 passed.
- Ruff: passed.
