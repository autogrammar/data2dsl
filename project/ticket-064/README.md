# Ticket 064: Fix wheel packaging to include standalone py modules (F01)

- **ID**: ticket-064
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-28

## Goal and scope

Fix audit finding F01:
`pyproject.toml` configured `[tool.setuptools.packages.find] where = ["src"]`, which discovered only subpackages (such as `data2dsl_contract_v0`) and omitted all 9 standalone `.py` modules located in `src/` (`data2dsl_adapters.py`, `data2dsl_batch.py`, `data2dsl_comparator.py`, `data2dsl_consumer.py`, `data2dsl_doctor.py`, `data2dsl_generator.py`, `data2dsl_remediation.py`, `data2dsl_skill.py`, `data2dsl_subactor.py`).
Configure `py-modules` under `[tool.setuptools]` in `pyproject.toml` so built wheels include all modules and package data (`comparison.schema.json`).

SESSION_EXECUTION_AUTHORIZATION recorded from user prompt.

## Acceptance criteria

- [x] AC-01: Scope is approved (SESSION_EXECUTION_AUTHORIZATION recorded).
- [x] AC-02: `pyproject.toml` declares all top-level Python modules under `[tool.setuptools.py-modules]`.
- [x] AC-03: `python -m build --wheel --no-isolation` or wheel inspection confirms all modules are packaged.
- [x] AC-04: Full pytest suite passes (112/112) and `governance-check.bat` reports GOV-PASS.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
