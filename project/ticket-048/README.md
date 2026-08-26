# Ticket 048: OQL Telemetry Integration for Agent Skill and MCP

- **ID**: ticket-048
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: VALIDATION
- **Created**: 2026-08-26
- **Receipt**: Integrated OqlTelemetryAdapter into Data2DslSkill and MCP dispatch; 57/57 tests passing and GOV-PASS.

## Goal and scope

Integrate the OQL Telemetry Source Adapter (`OqlTelemetryAdapter`) into `Data2DslSkill` and MCP tool execution (`src/data2dsl_skill.py`):
1. Support `oql` / `oqlos` / `oql_telemetry` source kind in `_normalize_raw`.
2. Add tool parameter documentation for OQL in `Data2DslSkill.get_tool_definitions()`.
3. Add unit tests for skill and MCP handling of OQL in `tests/test_skill.py`.
4. Verify governance gate and pytest suite.

## Acceptance criteria

- [x] AC-01: `_normalize_raw` in `src/data2dsl_skill.py` normalizes raw OQL scenario specs and telemetry inputs.
- [x] AC-02: Unit tests in `tests/test_skill.py` verify skill execution and MCP tool dispatch for OQL.
- [x] AC-03: Full pytest test suite passes cleanly (57 tests passing).
- [x] AC-04: Deterministic governance gate passes (`GOV-PASS`).

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
