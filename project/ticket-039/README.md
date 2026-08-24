# Ticket 039: Pipeline integration: urirun connector manifest and MCP server endpoint

- **ID**: ticket-039
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-08-24

## Goal and scope

Integrate `data2dsl` with the broader `if-uri` / `urirun` mesh and Model Context Protocol (MCP) ecosystems:
1. Define `src/connector.manifest.json` exposing `data2dsl://` routes.
2. Implement `urirun_bindings` router and MCP JSON-RPC 2.0 STDIO server handler in `src/data2dsl_skill.py`.
3. Provide comprehensive unit test verification.

## Acceptance criteria

- [x] AC-01: `src/connector.manifest.json` is created with valid `data2dsl://` routes and metadata.
- [x] AC-02: `urirun_bindings` correctly handles `data2dsl://host/compare/run` and `data2dsl://host/selftest/run`.
- [x] AC-03: `handle_mcp_message` implements JSON-RPC 2.0 `tools/list` and `tools/call`.
- [x] AC-04: Unit tests in `tests/test_skill.py` pass.
- [x] AC-05: The deterministic governance gate passes.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
