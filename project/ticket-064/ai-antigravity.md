# Antigravity agent plan — ticket-064

## Objective

Fix audit finding F01: Configure wheel packaging in `pyproject.toml` so all standalone `.py` modules in `src/` are included in built distributions.

## SESSION_EXECUTION_AUTHORIZATION

Recorded from user prompt in conversation 78d87a8b-d52c-4b44-b8f5-077656700b95.

## Changes made

### 1. `pyproject.toml`
- Declared all top-level Python modules under `[tool.setuptools]` (`py-modules = ["data2dsl_adapters", "data2dsl_batch", "data2dsl_comparator", "data2dsl_consumer", "data2dsl_doctor", "data2dsl_generator", "data2dsl_remediation", "data2dsl_skill", "data2dsl_subactor"]`).
- Explicitly configured `package-dir = {"" = "src"}` and `[tool.setuptools.package-data] "*" = ["*.json"]`.

## Verification

- Built wheel via `pip wheel` and verified all 9 standalone `.py` modules, schema JSON files, and contract package modules are present.
- Full pytest suite: 112/112 passed.
- Ruff: passed.
