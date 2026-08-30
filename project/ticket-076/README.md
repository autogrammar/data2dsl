# Ticket 076: Package public data2dsl CLI entry point

- **ID**: ticket-076
- **Owner**: founder:tom-sapletta-com
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-08-30

## Goal and scope

Repair the installed public CLI: the console script resolves
`data2dsl_cli:main`, but the explicitly enumerated wheel modules omit
`data2dsl_cli.py`.

## Acceptance criteria

- [x] AC-01: SESSION_EXECUTION_AUTHORIZATION is recorded from the founder's
  active autonomy repair request.
- [ ] AC-02: The wheel contains `data2dsl_cli.py` and its existing local
  runtime imports.
- [ ] AC-03: A clean isolated installation executes `data2dsl --self-test`.
- [ ] AC-04: Full tests and governance pass.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)
