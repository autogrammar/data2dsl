# Ticket 085: Audit P1.3: Batch deduplication and ambiguity detection

- **ID**: ticket-085
- **Owner**: gemini (SESSION_EXECUTION_AUTHORIZATION)
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-31
- **Workstream**: application

## Goal and scope

Detect and reject ambiguous duplicate observations in `BatchMultiQueryComparator`:
- When multiple observations for the same query_id or composite key have conflicting values, mark them ambiguous
- Synthesize an `UNEVALUABLE` dummy observation rather than silently overwriting
- Track `ambiguous_count` in `BatchComparisonSummary` and report markdown

## Acceptance criteria

- [x] AC-01: SESSION_EXECUTION_AUTHORIZATION recorded
- [x] AC-02: Batch ambiguity tests pass
- [x] AC-03: Governance check passes

## Participants

- Human participant: USER (session authorization)
- Agent participant: [ai-gemini.md](ai-gemini.md)
