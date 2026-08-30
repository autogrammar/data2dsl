# Ticket 073: Build autonomous data-source discovery graph

- **ID**: ticket-073
- **Owner**: founder:tom-sapletta-com
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-08-30

## Goal and scope

Build a deterministic, read-only discovery graph from explicitly supplied
configuration, registry and runtime-projection JSON documents. Expose bounded
query access through the existing MCP skill without granting execution
authority or reading implicit filesystem locations.

## Acceptance criteria

- [x] AC-01: The user's autonomous execution request records
  `SESSION_EXECUTION_AUTHORIZATION` for this bounded scope.
- [x] AC-02: Explicit JSON sources produce stable source, entity, schema and
  reference nodes with typed edges and canonical SHA-256 evidence.
- [x] AC-03: Queries return a bounded connected subgraph through MCP.
- [x] AC-04: Secret-value fields, oversized inputs and excessive graph depth
  fail closed or are redacted without exposing values.
- [x] AC-05: Unit, repository and governance checks pass.

## Validation evidence

- Full suite: 130 tests passed.
- New discovery module: Ruff passed; repository governance passed with zero
  errors and zero warnings; `git diff --check` passed.
- Read-only live canary: four explicit Subactor projections produced 1,560
  nodes and 1,556 edges with graph SHA-256
  `1defb70a7564a7cac3d2d9ced798ec4cedadb8d7d40ad24f6169bbfa8f70a661`.
- Queries resolved connected subgraphs for `subactor/supervisor` and
  `maskservice/update` without copying source values into the graph.

## Participants

- Human participant: founder request in the active chat session; no user-* file
  was created or modified.
- Agent participant: [ai-codex.md](ai-codex.md)
