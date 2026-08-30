# Ticket 074: Package data discovery runtime in wheel

- **ID**: ticket-074
- **Owner**: founder:tom-sapletta-com
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-08-30

## Goal and scope

Fix the ticket-073 wheel regression: `data2dsl_skill` imports
`data2dsl_discovery`, but setuptools does not include that new standalone
module. Add a packaging-closure regression test so future local runtime imports
cannot silently be omitted from the wheel.

## Acceptance criteria

- [x] AC-01: SESSION_EXECUTION_AUTHORIZATION is recorded from the active
  founder request.
- [ ] AC-02: The built wheel contains `data2dsl_discovery.py`.
- [ ] AC-03: An isolated installed-wheel MCP discovery call succeeds.
- [ ] AC-04: Tests and governance pass.

## Coordination

Ticket-072 is terminal after protected lifecycle reconciliation PR #62.
`pyproject.toml` belongs to this ticket's integration workstream and the
implementation is now active. A dependent application ticket owns the
cross-module packaging regression test because `tests/**` is not an
integration-owned path.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)
