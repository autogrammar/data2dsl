# Ticket 049: ADR-006 for OQL Telemetry and Hardware-in-the-Loop Normalization

- **ID**: ticket-049
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-26
- **Closed**: 2026-08-27
- **Receipt**: Authored ADR-006 for OQL telemetry and HIL normalization; 57/57 pytest tests passing and GOV-PASS.

## Goal and scope

Record ADR-006 (`docs/decisions/ADR-006-oql-telemetry-hardware-normalization.md`) documenting the architecture and normalization design for OQL hardware scenarios and sensor telemetry:
1. Define context, decision drivers, and normalization invariant for OQL scenario specifications and telemetry logs.
2. Document integration boundaries with `oqlos/*`, `Data2DslSkill`, MCP dispatch, and `DeterministicComparator`.
3. Verify full test suite and governance check.

## Acceptance criteria

- [x] AC-01: ADR-006 document created in `docs/decisions/ADR-006-oql-telemetry-hardware-normalization.md`.
- [x] AC-02: Full pytest test suite (57 tests) passes.
- [x] AC-03: Deterministic governance gate passes (`GOV-PASS`).

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
