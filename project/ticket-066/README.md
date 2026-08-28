# Ticket 066: Align MCP tool schema with inputSchema protocol and ensure clean STDIO (F08)

- **ID**: ticket-066
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-28

## Goal and scope

Fix audit finding F08:
1. `data2dsl_skill.list_tools()` / `handle_mcp_message` defined tool schemas with the non-standard key `"parameters"` instead of the MCP specification key `"inputSchema"` (while retaining `"parameters"` as alias where needed).
2. Diagnostic prints during MCP STDIO execution wrote to `sys.stdout` instead of `sys.stderr`, which could corrupt JSON-RPC message boundaries. Redirect all diagnostic output to `sys.stderr`.

SESSION_EXECUTION_AUTHORIZATION recorded from user prompt.

## Acceptance criteria

- [x] AC-01: Scope is approved (SESSION_EXECUTION_AUTHORIZATION recorded).
- [x] AC-02: `list_tools()` and `tools/list` response return MCP compliant `"inputSchema"` for every tool definition.
- [x] AC-03: Diagnostic and self-test logs write exclusively to `sys.stderr` when executing via MCP STDIO.
- [x] AC-04: Existing tests in `tests/test_skill.py` and new tests in `tests/test_mcp_protocol_compliance.py` pass.
- [x] AC-05: Full pytest suite passes (117/117) and `governance-check.bat` reports GOV-PASS.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
