# Ticket 047: Documentation and Capability Map Update for OQL Telemetry

- **ID**: ticket-047
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: VALIDATION
- **Created**: 2026-08-26
- **Receipt**: Updated CAPABILITY_MAP and research notes for OQL telemetry; passed all 55 tests and GOV-PASS.

## Goal and scope

Update `docs/CAPABILITY_MAP.md` and `docs/research-oql-telemetry.md` to reflect the implemented OQL Telemetry Source Adapter:
1. Add `OqlTelemetryAdapter` entry to the Source Adapters table in `docs/CAPABILITY_MAP.md`.
2. Update the Mermaid composition diagram in `docs/CAPABILITY_MAP.md` to include OQL scenario & telemetry log source.
3. Update `docs/research-oql-telemetry.md` status to `Implemented in ticket-046`.
4. Verify governance gate and full pytest test suite.

## Acceptance criteria

- [x] AC-01: `docs/CAPABILITY_MAP.md` table and mermaid graph document OQL Telemetry Adapter capabilities.
- [x] AC-02: `docs/research-oql-telemetry.md` status reflects implementation in ticket-046.
- [x] AC-03: Full pytest test suite (55 tests) passes.
- [x] AC-04: Deterministic governance gate passes (`GOV-PASS`).

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
