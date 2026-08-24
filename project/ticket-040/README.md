# Ticket 040: Documentation: ADR-004 Multi-source pipeline and CAPABILITY_MAP update

- **ID**: ticket-040
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-24
- **Closed**: 2026-08-24
- **Receipt**: Committed locally as `99dd921`.

## Goal and scope

Document the multi-source verification pipeline architecture and update the repository capability map:
1. Author `docs/decisions/ADR-004-multi-source-pipeline-architecture.md` detailing the composition of `planfile`, `deta`, `intent-contract`, `pyqual`, and `urirun`/`MCP` connectors.
2. Refresh `docs/CAPABILITY_MAP.md` to index all 8 implemented source adapters and update the architecture diagram.

## Acceptance criteria

- [x] AC-01: `docs/decisions/ADR-004-multi-source-pipeline-architecture.md` is authored and accepted.
- [x] AC-02: `docs/CAPABILITY_MAP.md` is updated with all 8 source adapters and integration bindings.
- [x] AC-03: The deterministic governance gate passes.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
