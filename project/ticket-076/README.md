# Ticket 076: Package public data2dsl CLI entry point

- **ID**: ticket-076
- **Owner**: founder:tom-sapletta-com
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-08-30

## Goal and scope

Repair the installed public CLI: the console script resolves
`data2dsl_cli:main`, but the explicitly enumerated wheel modules omit
`data2dsl_cli.py`.

## Acceptance criteria

- [x] AC-01: SESSION_EXECUTION_AUTHORIZATION is recorded from the founder's
  active autonomy repair request.
- [x] AC-02: The wheel contains `data2dsl_cli.py` and its existing local
  runtime imports.
- [x] AC-03: A clean isolated installation executes `data2dsl --self-test`.
- [x] AC-04: Full tests and governance pass.

## Validation evidence

- An out-of-tree wheel contains `data2dsl_cli.py`,
  `data2dsl_discovery.py` and the console entry-point metadata.
- A clean venv installed the wheel and executed `data2dsl --self-test` outside
  the checkout; the imported CLI path was inside `site-packages`.
- The complete suite passes: 132 tests; governance and whitespace checks pass.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)
