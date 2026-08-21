# Ticket 033: Mypy typecheck fix and Data2DslSkill unit test expansion

- **ID**: ticket-033
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-08-21

## Goal and scope

Fix mypy type narrowing issue in `src/data2dsl_contract_v0/validate.py`
and add comprehensive unit tests for `Data2DslSkill` agent tool interface
covering all 5 source adapter raw payload types, error scenarios, and self-test.

## Acceptance criteria

- [x] AC-01: `src/data2dsl_contract_v0/validate.py` passes `mypy` without union-attr errors.
- [x] AC-02: `tests/test_skill.py` covers tool definitions, self-test, raw normalization across markdown, github, curllm, code2logic, code2schema, and error modes.
- [x] AC-03: `python -m pytest tests/ -q` passes with 25/25 tests green.
- [x] AC-04: `python -m ruff check src/ tests/` reports zero errors.
- [x] AC-05: The deterministic governance gate passes.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
