# Ticket 022: ADR-003: natural language query and semcod/nlp2dsl integration evaluation

- **ID**: ticket-022
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-20

## Goal and scope

Evaluate integration of `semcod/nlp2dsl` (`nlp2cmd-intent`) as an upstream
front-end query compiler for `data2dsl`.
Publish ADR-003 establishing that natural language queries map to canonical
`autogrammar.data2dsl/query/v0` JSON AST queries at the outer boundary, preserving
the deterministic, effect-free and LLM-free core of `data2dsl`.

## Acceptance criteria

- [x] AC-01: `docs/decisions/ADR-003-natural-language-query-and-nlp2dsl-integration.md` is published with context, decision, and consequences.
- [x] AC-02: The deterministic governance gate passes.

## Result

Ticket 022 closed from integrated evidence:
- PR #23 approved at `6099068c42643c27686bdc6a19dcf8fbe8c4e753` (Decision `D-022-8684`), merged as `ee232e67df1bb746a51d95eeaa2d86161feee7d0`.
- Branch `agent/adr-003-nlp2dsl-022` deleted upon merge.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
