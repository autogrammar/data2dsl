# Antigravity agent plan — ticket-066

## Objective

Fix audit finding F08: Align MCP tool schemas with `inputSchema` specification and ensure clean STDIO logging.

## SESSION_EXECUTION_AUTHORIZATION

Recorded from user prompt in conversation 78d87a8b-d52c-4b44-b8f5-077656700b95.

## Changes made

### 1. `src/data2dsl_skill.py`
- Updated `get_tool_definitions()` so that all 4 MCP tools (`data2dsl_compare`, `data2dsl_self_test`, `data2dsl_validate_envelope`, `data2dsl_simulate_healing`) provide the standard MCP `"inputSchema"` property. Kept `"parameters"` alias for backwards compatibility.
- Verified STDIO framing in `main_mcp()` writes only JSON-RPC to `sys.stdout`.

### 2. `tests/test_mcp_protocol_compliance.py`
- Added tests verifying that `tools/list` message and direct tool definitions contain valid `"inputSchema"` dictionaries.

## Verification

- `pytest tests/test_mcp_protocol_compliance.py`: 2/2 passed.
- Full pytest suite: 117/117 passed.
- Ruff: passed.
