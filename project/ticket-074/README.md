# Ticket 074: Package data discovery runtime in wheel

- **ID**: ticket-074
- **Owner**: founder:tom-sapletta-com
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-30

## Goal and scope

Fix the ticket-073 wheel regression: `data2dsl_skill` imports
`data2dsl_discovery`, but setuptools does not include that new standalone
module. Add a packaging-closure regression test so future local runtime imports
cannot silently be omitted from the wheel.

## Acceptance criteria

- [x] AC-01: SESSION_EXECUTION_AUTHORIZATION is recorded from the active
  founder request.
- [x] AC-02: The built wheel contains `data2dsl_discovery.py`.
- [x] AC-03: An isolated installed-wheel MCP discovery call succeeds.
- [x] AC-04: Tests and governance pass.

## Validation evidence

- `/usr/bin/python3 -m build --wheel --no-isolation` produced a 20-file wheel
  containing `data2dsl_discovery.py`.
- A clean venv installed that wheel, imported `data2dsl_skill` outside the
  checkout and completed `data2dsl_discover_data` with status `OK` and graph
  SHA-256 `2d86aa4ae3eaef4b443f29f858b3c398d35127c0a83e051877f53f36e8229bdd`.
- Full suite: 130 tests passed. Governance and diff checks passed after build
  artifacts were removed from the delivery diff.
- Protected Validator run `33303079089` approved exact head
  `1e08ec9217f81f27b8f69c4191f5bb132241a220`; PR #63 merged it as
  `2c69c35c3f0b7c3dff9542f6901eb96b895cadff`.
- Integrated-main readback confirmed the module declaration and repeated all
  130 tests before terminal closure.

## Coordination

Ticket-072 is terminal after protected lifecycle reconciliation PR #62.
`pyproject.toml` belongs to this ticket's integration workstream and the
implementation is now active. A dependent application ticket owns the
cross-module packaging regression test because `tests/**` is not an
integration-owned path.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)
