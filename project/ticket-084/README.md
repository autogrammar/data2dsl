# Ticket 084: Audit P1.4-P1.6: Adapter semantics exact matching and evidence IDs

- **ID**: ticket-084
- **Owner**: gemini (SESSION_EXECUTION_AUTHORIZATION)
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-31
- **Workstream**: application

## Goal and scope

Fix adapter extraction semantics, exact key matching, and evidence integrity:
1. Actor matching: exact word boundary regex in `WorkSummaryMarkdownAdapter`
2. OQL buses: resolve `active_buses` / `buses` attributes in `OqlTelemetryAdapter`
3. SUMD exact key: match exact table metric keys without substring confusion
4. Code2Schema: pass `entities` keyword argument in `data2dsl_skill.py`
5. Evidence IDs: replace `/` with `:` in file paths

## Acceptance criteria

- [x] AC-01: SESSION_EXECUTION_AUTHORIZATION recorded
- [x] AC-02: All adapter tests pass
- [x] AC-03: ruff and mypy pass
- [x] AC-04: Governance check passes

## Participants

- Human participant: USER (session authorization)
- Agent participant: [ai-gemini.md](ai-gemini.md)
