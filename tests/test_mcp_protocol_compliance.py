"""Tests verifying MCP protocol compliance: inputSchema presence and STDIO safety (F08)."""

from data2dsl_skill import Data2DslSkill, handle_mcp_message


def test_tools_list_returns_input_schema_for_all_tools():
    """F08: MCP tools/list response must return inputSchema for every tool."""
    msg = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "tools/list",
        "params": {},
    }
    resp = handle_mcp_message(msg)
    assert resp is not None
    assert "result" in resp
    tools = resp["result"]["tools"]
    assert len(tools) == 4

    for tool in tools:
        assert "inputSchema" in tool, f"Tool {tool.get('name')} is missing 'inputSchema'"
        assert isinstance(tool["inputSchema"], dict)
        assert tool["inputSchema"].get("type") == "object"


def test_tools_direct_definition_has_input_schema():
    """F08: Data2DslSkill.get_tool_definitions returns inputSchema on all tools."""
    tools = Data2DslSkill.get_tool_definitions()
    for tool in tools:
        assert "inputSchema" in tool
        assert "name" in tool
        assert "description" in tool
