# Ticket 073: Build autonomous data-source discovery graph

- **ID**: ticket-073
- **Owner**: founder:tom-sapletta-com
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-08-30

## Goal and scope

Build a deterministic, read-only discovery graph from explicitly supplied
configuration, registry and runtime-projection JSON documents. Expose bounded
query access through the existing CLI and MCP skill without granting execution
authority or reading implicit filesystem locations.

## Acceptance criteria

- [x] AC-01: The user's autonomous execution request records
  `SESSION_EXECUTION_AUTHORIZATION` for this bounded scope.
- [ ] AC-02: Explicit JSON sources produce stable source, entity, schema and
  reference nodes with typed edges and canonical SHA-256 evidence.
- [ ] AC-03: Queries return a bounded connected subgraph through CLI and MCP.
- [ ] AC-04: Secret-value fields, oversized inputs and excessive graph depth
  fail closed or are redacted without exposing values.
- [ ] AC-05: Unit, repository and governance checks pass.

## Participants

- Human participant: founder request in the active chat session; no user-* file
  was created or modified.
- Agent participant: [ai-codex.md](ai-codex.md)
