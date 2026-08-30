# Ticket 075: Enforce wheel local-import closure

- **ID**: ticket-075
- **Owner**: founder:tom-sapletta-com
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-30

## Goal and scope

Prevent a repeat of the ticket-073/ticket-074 wheel regression by checking
that every local top-level runtime import reachable from an explicitly
packaged module is also declared in `tool.setuptools.py-modules`.

## Acceptance criteria

- [x] AC-01: SESSION_EXECUTION_AUTHORIZATION is recorded from the founder's
  active autonomy repair request.
- [x] AC-02: Current packaging metadata has no omitted local runtime imports.
- [x] AC-03: A negative probe that removes `data2dsl_discovery` reproduces the
  exact missing dependency through `data2dsl_skill`.
- [x] AC-04: Full tests and governance pass.

## Validation evidence

- The focused positive and negative probes pass: 2 tests.
- The complete checkout suite passes: 132 tests, with one pre-existing
  `jsonschema.RefResolver` deprecation warning.
- Ruff, governance and whitespace checks pass.
- Protected Validator run `33303497600` approved exact head
  `e697a22418f7209dfb3d3ecbf453cd7c5bdccad5`; PR #65 merged it as
  `c168b20a9ecbc262e30716397e6006d9abbbf49c`.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)
