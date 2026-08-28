# Antigravity agent plan — ticket-059

## Objective

Fix audit finding F02: comparison contract schema and query generator mismatch.

## SESSION_EXECUTION_AUTHORIZATION

Recorded from user approval of implementation plan in conversation
78d87a8b-d52c-4b44-b8f5-077656700b95. The user request explicitly authorized
autonomous execution.

## Changes made

### 1. `src/data2dsl_contract_v0/comparison.schema.json`

- Extended `source.kind` enum from `["markdown", "github"]` to include all 10
  adapter source kinds: `code2logic`, `code2schema`, `curllm`, `planfile`,
  `deta`, `intent_contract`, `oql`, `sumd`.
- Extended `location` oneOf from 2 variants to 3:
  - Line-based: `markdown-lines`, `yaml-lines`, `json-lines` (shared shape)
  - Page-based: `github-page` (unchanged)
  - Path-based: `oql-scenario`, `oql-telemetry-log`, `sumd-document`,
    `sumd-missing` (new, with optional `scenario_id`)

### 2. `src/data2dsl_generator.py`

- Fixed `metric.version` from `"1.0.0"` to `"v1"` (contract pattern `^v[1-9][0-9]*$`).
- Added `_EQUALITY_MAP` for deriving contract-valid equality from `value_kind`.
- Replaced raw `"exact"` and `"set-exact"` with `"integer-exact"`,
  `"string-set-exact"` etc.
- Made time window dynamic (defaults to current month, not Aug 2026).
- Added `window_start`/`window_end` parameters for explicit control.
- Right source kind now defaults to valid contract source kinds.

### 3. `tests/test_generator.py`

- Updated existing tests to assert `v1` version and contract-valid equality.
- Added `test_generate_query_template_float` and `_string` for coverage.
- Added `test_generate_query_template_dynamic_window` and `_explicit_window`.
- Added `test_generate_query_template_right_source_defaults` verifying all
  right sources are in `VALID_SOURCE_KINDS`.
- Added `test_generated_query_passes_contract_validation` — the key acceptance
  test: every adapter × value_kind combination's generated query is validated
  against the full contract schema.
- Added `test_legacy_exact_equality_mapped` for backward compatibility.

## Verification

- 11/11 generator tests pass.
- Full suite regression run in progress.
