# Ticket 027: Fix adapter normalization in data2dsl_skill

- **ID**: ticket-027
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-20

## Goal and scope

Fix adapter normalization helper in `src/data2dsl_skill.py` to invoke the concrete adapter classes
(`WorkSummaryMarkdownAdapter`, `GitHubDiagitAdapter`, `CurllmAdapter`, `Code2LogicAdapter`, `Code2SchemaAdapter`)
with query context.

## Acceptance criteria

- [x] AC-01: `src/data2dsl_skill.py` implements `_normalize_raw` correctly.
- [x] AC-02: All 15 tests in `tests/` pass with `pytest`.
- [x] AC-03: The deterministic governance gate passes.

## Result

Ticket 027 closed from integrated evidence:
- PR #28 approved at `ac1f1fa054b93f006ca2bbe36c8d14e386e45cb8` (Decision `D-027-9712`), merged as `ad53f7915309605cb4c55209c1221bca961a5b82`.
- Branch `agent/fix-skill-adapter-027` deleted upon merge.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
