# Ticket 074: Package data discovery runtime in wheel

- **ID**: ticket-074
- **Owner**: founder:tom-sapletta-com
- **Status**: BACKLOG
- **Workflow state**: PLAN
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
- [ ] AC-03: A deterministic metadata test rejects missing local runtime
  imports from `tool.setuptools.py-modules`.
- [ ] AC-04: An isolated installed-wheel MCP discovery call succeeds.
- [ ] AC-05: Tests and governance pass.

## Coordination

The application finding is recorded but remains BACKLOG until integrated audit
ticket-072 is terminal. `pyproject.toml` belongs to the integration workstream;
the implementation must not bypass that active lifecycle reservation.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)
