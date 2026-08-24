"""
data2dsl agent skill and tool interface.

Conforms to the wellmanifest/skills specification for governed agent tools.
Provides programmatic tool execution for comparing observations deterministically.
"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, Optional

from data2dsl_adapters import (
    Code2LogicAdapter,
    Code2LogicMetricResponse,
    Code2SchemaAdapter,
    Code2SchemaMetricResponse,
    CurllmAdapter,
    CurllmMetricResponse,
    DetaAdapter,
    DetaTopologyResponse,
    DiagitCommitMetricResponse,
    GitHubDiagitAdapter,
    IntentContractAdapter,
    IntentContractResponse,
    PlanfileAdapter,
    PlanfileMetricResponse,
    WorkSummaryMarkdownAdapter,
)
from data2dsl_comparator import DeterministicComparator
from data2dsl_contract_v0.validate import self_test as contract_self_test


def _normalize_raw(source_type: str, raw: Dict[str, Any], query: Dict[str, Any], side: str = "left") -> Dict[str, Any]:
    """Helper to normalize raw input via corresponding source adapter."""
    st = source_type.lower().replace("-", "_")
    if st == "markdown":
        adapter = WorkSummaryMarkdownAdapter()
        md_text = raw.get("markdown_content", "")
        claim = adapter.extract_commit_claim(
            markdown_text=md_text,
            actor=query["subject"]["actor"],
            path=raw.get("path", "work-summary.md"),
            source_uri=raw.get("source_uri"),
            source_revision=raw.get("source_revision"),
        )
        return adapter.normalize(query, claim, side=side)
    elif st == "github":
        adapter = GitHubDiagitAdapter()
        resp = DiagitCommitMetricResponse(
            status="OK" if raw.get("commit_count") is not None else "NOT_FOUND",
            commit_count=raw.get("commit_count"),
        )
        return adapter.normalize(query, resp, side=side)
    elif st == "curllm":
        adapter = CurllmAdapter()
        resp = raw.get("response")
        if not isinstance(resp, CurllmMetricResponse):
            resp = CurllmMetricResponse(
                status="OK" if raw.get("value") is not None else "ERROR",
                value=raw.get("value"),
            )
        return adapter.normalize(query, resp, side=side)
    elif st == "code2logic":
        adapter = Code2LogicAdapter()
        resp = raw.get("response")
        if not isinstance(resp, Code2LogicMetricResponse):
            resp = Code2LogicMetricResponse(
                status="OK" if raw.get("value") is not None else "ERROR",
                value=raw.get("value"),
            )
        return adapter.normalize(query, resp, side=side)
    elif st == "code2schema":
        adapter = Code2SchemaAdapter()
        resp = raw.get("response")
        if not isinstance(resp, Code2SchemaMetricResponse):
            entities = raw.get("entities") if raw.get("entities") is not None else raw.get("value", ())
            resp = Code2SchemaMetricResponse(
                status="OK" if entities is not None else "ERROR",
                entities=entities if isinstance(entities, (list, tuple)) else (entities,),
            )
        return adapter.normalize(query, resp, side=side)
    elif st == "planfile":
        adapter = PlanfileAdapter()
        resp = raw.get("response")
        if not isinstance(resp, PlanfileMetricResponse):
            count = raw.get("count") if raw.get("count") is not None else raw.get("value")
            resp = PlanfileMetricResponse(
                status="OK" if (count is not None or raw.get("tickets")) else "ERROR",
                count=int(count) if count is not None else None,
                tickets=raw.get("tickets", ()),
            )
        return adapter.normalize(query, resp, side=side)
    elif st == "deta":
        adapter = DetaAdapter()
        resp = raw.get("response")
        if not isinstance(resp, DetaTopologyResponse):
            sc = raw.get("service_count") if raw.get("service_count") is not None else raw.get("value")
            resp = DetaTopologyResponse(
                status="OK" if (sc is not None or raw.get("services") or raw.get("ports")) else "ERROR",
                service_count=int(sc) if sc is not None else None,
                services=raw.get("services", ()),
                ports=raw.get("ports", ()),
            )
        return adapter.normalize(query, resp, side=side)
    elif st in ("intent_contract", "intentcontract"):
        adapter = IntentContractAdapter()
        resp = raw.get("response")
        if not isinstance(resp, IntentContractResponse):
            resp = IntentContractResponse(
                status="OK" if (raw.get("deliverables") or raw.get("parties") or raw.get("obligations") or raw.get("contract_id")) else "ERROR",
                contract_id=raw.get("contract_id", "intent-contract-001"),
                parties=raw.get("parties", ()),
                deliverables=raw.get("deliverables", ()),
                obligations=raw.get("obligations", ()),
            )
        return adapter.normalize(query, resp, side=side)
    else:
        raise ValueError(f"Unknown source adapter kind: {source_type}")



class Data2DslSkill:
    """Governed agent skill exposing data2dsl capabilities."""

    SCHEMA_VERSION = "wellmanifest.skills/v1"
    SKILL_NAME = "autogrammar.data2dsl"
    VERSION = "0.1.0"

    @classmethod
    def get_tool_definitions(cls) -> list[Dict[str, Any]]:
        """Return MCP / JSON schema tool definitions for agent discovery."""
        return [
            {
                "name": "data2dsl_compare",
                "description": (
                    "Compare two evidence-bearing observations (e.g. GitHub commit "
                    "metrics, work summary claims, or browser extractions) against a "
                    "formal query deterministically."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "object",
                            "description": "Canonical autogrammar.data2dsl/query/v0 query object."
                        },
                        "left_observation": {
                            "type": "object",
                            "description": "Normalized left observation dictionary."
                        },
                        "right_observation": {
                            "type": "object",
                            "description": "Normalized right observation dictionary."
                        },
                        "left_raw": {
                            "type": "object",
                            "description": "Raw adapter input for left source."
                        },
                        "left_source_type": {
                            "type": "string",
                            "description": "Source adapter kind (e.g. github, markdown, curllm, code2logic, code2schema)."
                        },
                        "right_raw": {
                            "type": "object",
                            "description": "Raw adapter input for right source."
                        },
                        "right_source_type": {
                            "type": "string",
                            "description": "Source adapter kind (e.g. github, markdown, curllm, code2logic, code2schema)."
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "data2dsl_self_test",
                "description": "Run the built-in self-test suite verifying comparator integrity and schema conformance.",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]

    @classmethod
    def self_test(cls) -> Dict[str, Any]:
        """Execute self-test suite."""
        try:
            contract_self_test()
            return {
                "status": "PASS",
                "skill": cls.SKILL_NAME,
                "version": cls.VERSION
            }
        except Exception as exc:
            return {
                "status": "FAIL",
                "error": str(exc),
                "skill": cls.SKILL_NAME,
                "version": cls.VERSION
            }

    @classmethod
    def execute_compare(
        cls,
        query: Dict[str, Any],
        left_observation: Optional[Dict[str, Any]] = None,
        right_observation: Optional[Dict[str, Any]] = None,
        left_raw: Optional[Dict[str, Any]] = None,
        left_source_type: Optional[str] = None,
        right_raw: Optional[Dict[str, Any]] = None,
        right_source_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute deterministic comparison with either pre-normalized or raw adapter inputs."""
        try:
            # Resolve left observation
            if left_observation is None:
                if left_raw is not None and left_source_type is not None:
                    left_observation = _normalize_raw(left_source_type, left_raw, query, side="left")
                else:
                    return {
                        "status": "ERROR",
                        "error_code": "MISSING_LEFT_OBSERVATION",
                        "message": "Either left_observation or (left_raw and left_source_type) must be provided."
                    }

            # Resolve right observation
            if right_observation is None:
                if right_raw is not None and right_source_type is not None:
                    right_observation = _normalize_raw(right_source_type, right_raw, query, side="right")
                else:
                    return {
                        "status": "ERROR",
                        "error_code": "MISSING_RIGHT_OBSERVATION",
                        "message": "Either right_observation or (right_raw and right_source_type) must be provided."
                    }

            comparator = DeterministicComparator()
            bundle = comparator.compare(query, left_observation, right_observation)
            return {
                "status": "OK",
                "result": bundle["result"],
                "bundle": bundle
            }
        except Exception as exc:
            return {
                "status": "ERROR",
                "error_code": "COMPARISON_EXCEPTION",
                "message": str(exc)
            }


def urirun_bindings() -> Dict[str, Any]:
    """Return urirun bindings descriptor and router for data2dsl:// URI schemes."""
    def _route_compare(payload: Dict[str, Any]) -> Dict[str, Any]:
        return Data2DslSkill.execute_compare(**payload)

    def _route_selftest(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return Data2DslSkill.self_test()

    return {
        "scheme": "data2dsl",
        "version": Data2DslSkill.VERSION,
        "routes": {
            "data2dsl://host/compare/run": _route_compare,
            "data2dsl://host/selftest/run": _route_selftest,
        },
        "handler": lambda route, payload: {
            "data2dsl://host/compare/run": _route_compare,
            "data2dsl://host/selftest/run": _route_selftest,
        }.get(route, lambda p: {"status": "ERROR", "message": f"Unknown route: {route}"})(payload)
    }


def handle_mcp_message(msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Process a single Model Context Protocol (MCP) JSON-RPC 2.0 message."""
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

