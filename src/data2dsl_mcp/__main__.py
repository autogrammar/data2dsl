"""data2dsl MCP server — dependency-free stdio JSON-RPC.

Adopts wellmanifest/poa (typed tools, closed inputSchema, fail-closed
dispatch) and wellmanifest/logs (append-only hash-chained JSONL event
stream under $XDG_STATE_HOME/data2dsl/mcp-events.jsonl, overridable with
DATA2DSL_MCP_EVENT_LOG).
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Callable

_PROTOCOL_VERSION = "2024-11-05"
_NOTIFICATIONS = frozenset({"notifications/initialized", "notifications/cancelled"})

SERVER_NAME = "data2dsl"
try:
    from importlib.metadata import version as _pkg_version

    SERVER_VERSION = _pkg_version("data2dsl")
except Exception:
    SERVER_VERSION = "0.0.0"

_ZERO_HASH = "0" * 64


def _event_log_path() -> Path:
    override = os.environ.get("DATA2DSL_MCP_EVENT_LOG")
    if override:
        return Path(override)
    state_home = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state"))
    return state_home / "data2dsl" / "mcp-events.jsonl"


def _emit_event(tool: str, status: str, duration_ms: int, detail: str = "") -> None:
    """Append one hash-chained event; logging failure never breaks a tool call."""
    try:
        path = _event_log_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        prev = _ZERO_HASH
        if path.exists() and path.stat().st_size:
            with path.open("rb") as fh:
                fh.seek(0, os.SEEK_END)
                tail = fh.read(65536).decode("utf-8", errors="replace")
            last = tail.rstrip().rsplit("\n", 1)[-1]
            prev = json.loads(last).get("event_hash", _ZERO_HASH)
        event = {
            "schema": "data2dsl.mcp/event/v1",
            "event_id": f"event:{uuid.uuid4().hex[:24]}",
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "actor": "agent:mcp",
            "tool": tool,
            "status": status,
            "duration_ms": duration_ms,
            "detail": detail[:200],
            "prev_hash": prev,
        }
        body = json.dumps(event, sort_keys=True)
        event["event_hash"] = hashlib.sha256(body.encode()).hexdigest()
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event) + "\n")
    except Exception:
        pass


def _load_json_arg(args: dict[str, Any], key: str) -> dict[str, Any]:
    """Load a JSON object from an inline `*_json` arg or a file path arg."""
    inline = args.get(f"{key}_json")
    if inline is not None:
        if isinstance(inline, str):
            return json.loads(inline)
        if isinstance(inline, dict):
            return inline
        raise ValueError(f"{key}_json must be a JSON object or string")
    path = args.get(key)
    if not path:
        raise ValueError(f"missing required argument: {key} (path) or {key}_json")
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _tool_compare(args: dict[str, Any]) -> str:
    from data2dsl_comparator import compare_observations

    query = _load_json_arg(args, "query") if (args.get("query") or args.get("query_json")) else {}
    left = _load_json_arg(args, "left")
    right = _load_json_arg(args, "right")
    result = compare_observations(query, left, right)
    return json.dumps(result, indent=2, ensure_ascii=False)


def _tool_validate_bundle(args: dict[str, Any]) -> str:
    from data2dsl_contract_v0.validate import validate_document

    bundle = _load_json_arg(args, "bundle")
    validate_document(bundle)
    return json.dumps({"status": "VALID"})


def _tool_discover(args: dict[str, Any]) -> str:
    from data2dsl_discovery import discover_data_network

    sources = args.get("sources")
    if sources is None and args.get("input"):
        envelope = json.loads(Path(args["input"]).read_text(encoding="utf-8"))
        sources = envelope.get("sources")
        args.setdefault("query", envelope.get("query"))
    if not isinstance(sources, list):
        raise ValueError("missing required argument: sources (list) or input (envelope path)")
    graph = discover_data_network(sources, query=args.get("query"))
    return json.dumps(graph, indent=2, ensure_ascii=False)


def _tool_self_test(_args: dict[str, Any]) -> str:
    from data2dsl_cli import run_self_test

    code = run_self_test()
    return json.dumps({"status": "OK" if code == 0 else "FAIL", "exit_code": code})


TOOL_SCHEMAS: dict[str, dict[str, Any]] = {
    "data2dsl_compare": {
        "name": "data2dsl_compare",
        "description": "Deterministically compare two observation JSON documents (paths or inline JSON).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "left": {"type": "string", "description": "Path to left observation JSON"},
                "right": {"type": "string", "description": "Path to right observation JSON"},
                "left_json": {"type": "object", "description": "Inline left observation"},
                "right_json": {"type": "object", "description": "Inline right observation"},
                "query": {"type": "string", "description": "Optional query JSON path"},
                "query_json": {"type": "object", "description": "Optional inline query"},
            },
            "required": [],
        },
    },
    "data2dsl_validate_bundle": {
        "name": "data2dsl_validate_bundle",
        "description": "Validate a comparison bundle JSON against contract v0.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "bundle": {"type": "string", "description": "Path to bundle JSON"},
                "bundle_json": {"type": "object", "description": "Inline bundle object"},
            },
            "required": [],
        },
    },
    "data2dsl_discover": {
        "name": "data2dsl_discover",
        "description": "Build a bounded data graph from a {sources, query} envelope.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "input": {
                    "type": "string",
                    "description": "Path to {sources, query} JSON envelope",
                },
                "sources": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Inline sources list",
                },
                "query": {"description": "Optional inline query object"},
            },
            "required": [],
        },
    },
    "data2dsl_self_test": {
        "name": "data2dsl_self_test",
        "description": "Run the built-in comparison self-test on bundled fixtures.",
        "inputSchema": {"type": "object", "properties": {}},
    },
}

TOOL_HANDLERS: dict[str, Callable[[dict[str, Any]], str]] = {
    "data2dsl_compare": _tool_compare,
    "data2dsl_validate_bundle": _tool_validate_bundle,
    "data2dsl_discover": _tool_discover,
    "data2dsl_self_test": _tool_self_test,
}


def _handle_initialize(request_id: Any, params: dict[str, Any] | None) -> dict[str, Any]:
    client_version = (params or {}).get("protocolVersion", _PROTOCOL_VERSION)
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "protocolVersion": client_version,
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            "capabilities": {"tools": {}},
        },
    }


def _handle_tools_list(request_id: Any) -> dict[str, Any]:
    tools = [
        {
            "name": schema["name"],
            "description": schema["description"],
            "inputSchema": schema["inputSchema"],
        }
        for schema in TOOL_SCHEMAS.values()
    ]
    return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": tools}}


def _handle_tools_call(request_id: Any, params: dict[str, Any]) -> dict[str, Any]:
    tool_name = params.get("name")
    arguments = params.get("arguments", {}) or {}

    if tool_name not in TOOL_HANDLERS:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": f"Tool '{tool_name}' not found"},
        }

    start = time.monotonic()
    try:
        result = TOOL_HANDLERS[tool_name](arguments)
        _emit_event(tool_name, "ok", int((time.monotonic() - start) * 1000))
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"content": [{"type": "text", "text": result}]},
        }
    except Exception as exc:
        _emit_event(
            tool_name, "error", int((time.monotonic() - start) * 1000), str(exc)
        )
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32603, "message": f"Tool execution failed: {exc}"},
        }


def handle_request(request: dict[str, Any]) -> dict[str, Any]:
    method = request.get("method", "")
    params = request.get("params", {}) or {}
    request_id = request.get("id")

    if method in _NOTIFICATIONS:
        return {}
    if method == "initialize":
        return _handle_initialize(request_id, params)
    if method == "tools/list":
        return _handle_tools_list(request_id)
    if method == "tools/call":
        return _handle_tools_call(request_id, params)

    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": -32601, "message": f"Method '{method}' not found"},
    }


def run_server() -> None:
    print("data2dsl MCP Server started", file=sys.stderr)
    print(f"Available tools: {', '.join(sorted(TOOL_SCHEMAS))}", file=sys.stderr)

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            response = handle_request(request)
            if response:
                print(json.dumps(response), flush=True)
        except json.JSONDecodeError as exc:
            print(
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "error": {"code": -32700, "message": f"Parse error: {exc}"},
                    }
                ),
                flush=True,
            )
        except Exception as exc:
            print(
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "error": {"code": -32603, "message": f"Internal error: {exc}"},
                    }
                ),
                flush=True,
            )


def main() -> None:
    run_server()


if __name__ == "__main__":
    main()
