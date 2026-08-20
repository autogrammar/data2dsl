# Ticket 027: Fix adapter normalization in data2dsl_skill

- **ID**: ticket-027
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-08-20

## Goal and scope

Fix adapter normalization helper in `src/data2dsl_skill.py` to invoke the concrete adapter classes
(`WorkSummaryMarkdownAdapter`, `GitHubDiagitAdapter`, `CurllmAdapter`, `Code2LogicAdapter`, `Code2SchemaAdapter`)
with query context.

## Acceptance criteria

- [x] AC-01: `src/data2dsl_skill.py` implements `_normalize_raw` correctly.
- [x] AC-02: All 15 tests in `tests/` pass with `pytest`.
- [x] AC-03: The deterministic governance gate passes.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
