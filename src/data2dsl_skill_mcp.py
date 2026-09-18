"""STDIO JSON-RPC transport (MCP) for the data2dsl skill."""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, Optional


def handle_mcp_message(msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Process a single Model Context Protocol (MCP) JSON-RPC 2.0 message."""
    from data2dsl_skill import Data2DslSkill

    method = msg.get("method")
    msg_id = msg.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "data2dsl", "version": Data2DslSkill.VERSION},
            },
        }

    if method == "notifications/initialized":
        return None

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"tools": Data2DslSkill.get_tool_definitions()},
        }

    if method == "tools/call":
        params = msg.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name == "data2dsl_compare":
            res = Data2DslSkill.execute_compare(**arguments)
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"content": [{"type": "text", "text": json.dumps(res)}]},
            }
        elif tool_name == "data2dsl_self_test":
            res = Data2DslSkill.self_test()
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"content": [{"type": "text", "text": json.dumps(res)}]},
            }
        elif tool_name == "data2dsl_validate_envelope":
            res = Data2DslSkill.execute_validate_envelope(**arguments)
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"content": [{"type": "text", "text": json.dumps(res)}]},
            }
        elif tool_name == "data2dsl_simulate_healing":
            res = Data2DslSkill.execute_simulate_healing(**arguments)
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"content": [{"type": "text", "text": json.dumps(res)}]},
            }
        elif tool_name == "data2dsl_discover_data":
            res = Data2DslSkill.execute_discover_data(**arguments)
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"content": [{"type": "text", "text": json.dumps(res)}]},
            }
        else:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Method not found: {tool_name}"},
            }

    if msg_id is not None:
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {"code": -32601, "message": f"Unsupported method: {method}"},
        }
    return None


def main_mcp() -> None:
    """STDIO JSON-RPC server loop for MCP."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            resp = handle_mcp_message(req)
            if resp is not None:
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()
        except Exception as exc:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {exc}"},
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()
