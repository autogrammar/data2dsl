# Ticket 052: MCP Subactor Tools and SUMD Source Adapter

- **ID**: ticket-052
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-08-27
- **Receipt**: Implemented SUMD source adapter, extended Data2DslSkill and MCP dispatch with Subactor validation and healing tools; 76/76 pytest tests passing and GOV-PASS.

## Goal and scope

Extend `data2dsl` with MCP Subactor tool handlers and SUMD Structured Markdown Source Adapter:
1. Implement `SUMDAdapter` in `src/data2dsl_adapters.py` to extract and normalize facts from SUMD (Structured Unified Markdown Document) tables and descriptor blocks into `Observation` records.
2. Extend `Data2DslSkill` in `src/data2dsl_skill.py` with `data2dsl_validate_envelope` and `data2dsl_simulate_healing` MCP tool definitions and JSON-RPC dispatch.
3. Add `urirun` route bindings for `data2dsl://host/subactor/validate` and `data2dsl://host/healing/simulate`.
4. Add comprehensive unit tests in `tests/test_sumd_adapter.py` and extend `tests/test_skill.py`.
5. Verify all test suites pass cleanly and governance check passes (`GOV-PASS`).

## Acceptance criteria

- [x] AC-01: `SUMDAdapter` parses SUMD tables/descriptors into normalized observations with SHA-256 evidence.
- [x] AC-02: `Data2DslSkill` exposes `data2dsl_validate_envelope` and `data2dsl_simulate_healing` via MCP JSON-RPC 2.0 and `urirun`.
- [x] AC-03: Unit tests in `tests/test_sumd_adapter.py` and `tests/test_skill.py` pass.
- [x] AC-04: Full pytest test suite and governance check pass (`GOV-PASS`).

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
