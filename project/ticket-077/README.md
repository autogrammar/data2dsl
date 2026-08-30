# Ticket 077: Expose bounded data-network discovery through CLI

- **ID**: ticket-077
- **Owner**: founder:tom-sapletta-com
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-30

## Goal and scope

Expose the existing bounded discovery engine through the installed CLI so a
Supervisor can stream already-sanitized registry and projection documents into
a deterministic data graph without granting filesystem or network discovery.

## Acceptance criteria

- [x] AC-01: SESSION_EXECUTION_AUTHORIZATION is recorded from the founder's
  active autonomy repair request.
- [x] AC-02: `data2dsl discover` accepts one JSON envelope from a named file or
  stdin and emits the deterministic graph.
- [x] AC-03: Invalid or duplicate sources fail closed with a structured error
  and non-zero exit status.
- [x] AC-04: Packaging metadata tests require every console entry-point module
  to be included in the wheel.
- [x] AC-05: Full tests and governance pass.

## Validation evidence

- Positive stdin and named-file graphs and the duplicate-source rejection pass.
- The packaging test now binds every local console entry-point target to an
  included standalone wheel module and reproduces omission of `data2dsl_cli`.
- Focused CLI/packaging tests: 10 passed; complete suite: 136 passed with one
  pre-existing jsonschema deprecation warning.
- Ruff, governance and whitespace gates pass.
- Protected Validator run `33304354058` approved exact head
  `2e50a07c6c22e6e61bf77dac4eae08d9e76f66a7`; PR #69 merged it as
  `11e8969b3567fc619dd0e0cc4663aa16c32fd398`.
- A wheel built from integrated main was installed into the Subactor runtime
  venv. Outside the checkout, `data2dsl discover --input -` produced a valid
  three-node graph and the installed contract self-test passed.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)
