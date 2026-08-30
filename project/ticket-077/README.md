# Ticket 077: Expose bounded data-network discovery through CLI

- **ID**: ticket-077
- **Owner**: founder:tom-sapletta-com
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-08-30

## Goal and scope

Expose the existing bounded discovery engine through the installed CLI so a
Supervisor can stream already-sanitized registry and projection documents into
a deterministic data graph without granting filesystem or network discovery.

## Acceptance criteria

- [x] AC-01: SESSION_EXECUTION_AUTHORIZATION is recorded from the founder's
  active autonomy repair request.
- [ ] AC-02: `data2dsl discover` accepts one JSON envelope from a named file or
  stdin and emits the deterministic graph.
- [ ] AC-03: Invalid or duplicate sources fail closed with a structured error
  and non-zero exit status.
- [ ] AC-04: Packaging metadata tests require every console entry-point module
  to be included in the wheel.
- [ ] AC-05: Full tests and governance pass.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)
