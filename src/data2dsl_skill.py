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
    CurllmPageEvidence,
    DetaAdapter,
    DetaServiceEvidence,
    DetaTopologyResponse,
    DiagitCommitMetricResponse,
    DiagitPageEvidence,
    GitHubDiagitAdapter,
    IntentContractAdapter,
    IntentContractResponse,
    OqlScenarioSpecResponse,
    OqlTelemetryAdapter,
    OqlTelemetryLogResponse,
    PlanfileAdapter,
    PlanfileMetricResponse,
    PlanfileTicketEvidence,
    SUMDAdapter,
    SUMDMetricResponse,
    WorkSummaryMarkdownAdapter,
)
from data2dsl_comparator import DeterministicComparator
from data2dsl_contract_v0.validate import self_test as contract_self_test
from data2dsl_discovery import DiscoveryError, discover_data_network
from data2dsl_subactor import simulate_self_healing_cycle, validate_delegation_envelope


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
        resp = raw.get("response")
        if not isinstance(resp, DiagitCommitMetricResponse):
            pages_raw = raw.get("pages", ())
            pages_obj = []
            for p in pages_raw:
                if isinstance(p, DiagitPageEvidence):
                    pages_obj.append(p)
                elif isinstance(p, dict):
                    pages_obj.append(DiagitPageEvidence(
                        page=p.get("page", 1),
                        cursor=p.get("cursor"),
                        digest_sha256=p.get("digest_sha256", ""),
                        source_revision=p.get("source_revision", ""),
                        endpoint=p.get("endpoint", "/commits"),
                        media_type=p.get("media_type", "application/json"),
                        source_uri=p.get("source_uri", "https://api.github.com"),
                    ))
            resp = DiagitCommitMetricResponse(
                status="OK" if raw.get("commit_count") is not None else raw.get("status", "NOT_FOUND"),
                commit_count=raw.get("commit_count"),
                pages=tuple(pages_obj),
                error_message=raw.get("error_message"),
            )
        return adapter.normalize(query, resp, side=side)
    elif st == "curllm":
        adapter = CurllmAdapter()
        resp = raw.get("response")
        if not isinstance(resp, CurllmMetricResponse):
            pages_raw = raw.get("pages", ())
            pages_obj = []
            for p in pages_raw:
                if isinstance(p, CurllmPageEvidence):
                    pages_obj.append(p)
                elif isinstance(p, dict):
                    pages_obj.append(CurllmPageEvidence(
                        url=p.get("url", ""),
                        digest_sha256=p.get("digest_sha256", ""),
                        page=p.get("page", 1),
                        endpoint=p.get("endpoint", "web-page"),
                        source_revision=p.get("source_revision"),
                        media_type=p.get("media_type", "text/html"),
                    ))
            resp = CurllmMetricResponse(
                status="OK" if raw.get("value") is not None else raw.get("status", "ERROR"),
                value=raw.get("value"),
                pages=tuple(pages_obj),
                error_message=raw.get("error_message"),
            )
        return adapter.normalize(query, resp, side=side)
    elif st == "code2logic":
        adapter = Code2LogicAdapter()
        resp = raw.get("response")
        if not isinstance(resp, Code2LogicMetricResponse):
            resp = Code2LogicMetricResponse(
                status="OK" if raw.get("value") is not None else raw.get("status", "ERROR"),
                value=raw.get("value"),
                error_message=raw.get("error_message"),
            )
        return adapter.normalize(query, resp, side=side)
    elif st == "code2schema":
        adapter = Code2SchemaAdapter()
        resp = raw.get("response")
        if not isinstance(resp, Code2SchemaMetricResponse):
            resp = Code2SchemaMetricResponse(
                status="OK" if raw.get("value") is not None else raw.get("status", "ERROR"),
                value=raw.get("value"),
                error_message=raw.get("error_message"),
            )
        return adapter.normalize(query, resp, side=side)
    elif st == "planfile":
        planfile_adapter = PlanfileAdapter()
        resp = raw.get("response")
        if not isinstance(resp, PlanfileMetricResponse):
            tickets_raw = raw.get("tickets", ())
            tickets_obj = []
            for t in tickets_raw:
                if isinstance(t, PlanfileTicketEvidence):
                    tickets_obj.append(t)
                elif isinstance(t, dict):
                    tickets_obj.append(PlanfileTicketEvidence(
                        ticket_id=t.get("ticket_id", ""),
                        title=t.get("title", ""),
                        status=t.get("status", "OPEN"),
                        path=t.get("path", "planfile.yaml"),
                        start_line=t.get("start_line", 1),
                        end_line=t.get("end_line", 1),
                        digest_sha256=t.get("digest_sha256"),
                        media_type=t.get("media_type", "application/yaml"),
                    ))
            resp = PlanfileMetricResponse(
                status=raw.get("status", "OK"),
                count=raw.get("count") if raw.get("count") is not None else raw.get("value"),
                tickets=tuple(tickets_obj),
                path=raw.get("path", "planfile.yaml"),
                error_message=raw.get("error_message"),
            )
        return planfile_adapter.normalize(query, resp, side=side)
    elif st == "deta":
        deta_adapter = DetaAdapter()
        resp = raw.get("response")
        if not isinstance(resp, DetaTopologyResponse):
            services_raw = raw.get("services", ())
            services_obj = []
            for s in services_raw:
                if isinstance(s, DetaServiceEvidence):
                    services_obj.append(s)
                elif isinstance(s, dict):
                    services_obj.append(DetaServiceEvidence(
                        name=s.get("name", ""),
                        service_type=s.get("service_type", "service"),
                        ports=s.get("ports", ()),
                        manifest_path=s.get("manifest_path", "compose.yml"),
                        start_line=s.get("start_line", 1),
                        end_line=s.get("end_line", 1),
                        digest_sha256=s.get("digest_sha256"),
                    ))
            service_cnt = raw.get("service_count") if raw.get("service_count") is not None else raw.get("value")
            resp = DetaTopologyResponse(
                status=raw.get("status", "OK"),
                service_count=service_cnt,
                services=tuple(services_obj),
                ports=tuple(raw.get("ports", ())),
                manifest_path=raw.get("manifest_path", "compose.yml"),
                error_message=raw.get("error_message"),
            )
        return deta_adapter.normalize(query, resp, side=side)
    elif st in ("intent_contract", "subactor_intent_contract", "intentcontract"):
        intent_adapter = IntentContractAdapter()
        resp = raw.get("response")
        if not isinstance(resp, IntentContractResponse):
            resp = IntentContractResponse(
                status=raw.get("status", "OK"),
                parties=raw.get("parties", ()),
                deliverables=raw.get("deliverables", ()),
                obligations=raw.get("obligations", ()),
                error_message=raw.get("error_message"),
            )
        return intent_adapter.normalize(query, resp, side=side)
    elif st == "sumd":
        sumd_adapter = SUMDAdapter()
        resp = raw.get("response")
        if not isinstance(resp, SUMDMetricResponse):
            md_text = raw.get("markdown_content", "") or raw.get("text", "")
            metric_id = query.get("metric", {}).get("id", "metric")
            resp = sumd_adapter.extract_table_metric(
                markdown_text=md_text,
                metric_id=metric_id,
                path=raw.get("path", "document.sumd.md"),
                source_uri=raw.get("source_uri"),
                source_revision=raw.get("source_revision"),
            )
        return sumd_adapter.normalize(query, resp, side=side)
    elif st in ("oql", "oqlos", "oql_telemetry", "oql_spec"):
        oql_adapter = OqlTelemetryAdapter()
        is_telemetry = (
            st in ("oql_telemetry", "oqlos")
            or raw.get("kind") == "telemetry"
            or "log_id" in raw
            or "avg_sample_rate_hz" in raw
            or "peak_temperature_celsius" in raw
            or side == "right"
        )
        if is_telemetry and (raw.get("kind") != "spec" and "scenario_id" not in raw):
            resp = OqlTelemetryLogResponse(
                status=raw.get("status", "OK"),
                log_id=raw.get("log_id", "oql-telemetry-001"),
                path=raw.get("path", "logs/sensor.jsonl"),
                start_line=raw.get("start_line", 1),
                end_line=raw.get("end_line", 1),
                avg_sample_rate_hz=raw.get("avg_sample_rate_hz") or raw.get("sample_rate_hz") or raw.get("sample_rate"),
                peak_temperature_celsius=raw.get("peak_temperature_celsius") or raw.get("max_temperature_celsius") or raw.get("temperature"),
                observed_frequency_mhz=raw.get("observed_frequency_mhz") or raw.get("frequency_mhz"),
                avg_packet_throughput=raw.get("avg_packet_throughput") or raw.get("packet_throughput") or raw.get("throughput"),
                active_pins=raw.get("active_pins", ()),
                active_buses=raw.get("active_buses") or raw.get("buses", ()),
                error_message=raw.get("error_message"),
            )
        else:
            resp = OqlScenarioSpecResponse(
                status=raw.get("status", "OK"),
                scenario_id=raw.get("scenario_id", "oql-scenario-001"),
                path=raw.get("path", "scenarios/sensor.oql.json"),
                start_line=raw.get("start_line", 1),
                end_line=raw.get("end_line", 1),
                sample_rate_hz=raw.get("sample_rate_hz") or raw.get("sample_rate"),
                max_temperature_celsius=raw.get("max_temperature_celsius") or raw.get("temperature"),
                frequency_mhz=raw.get("frequency_mhz"),
                packet_throughput=raw.get("packet_throughput") or raw.get("throughput"),
                active_pins=raw.get("active_pins", ()),
                buses=raw.get("buses", ()),
                error_message=raw.get("error_message"),
            )
        return oql_adapter.normalize(query, resp, side=side)
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
        compare_schema = {
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
                    "description": "Source adapter kind (e.g. github, markdown, sumd, curllm, code2logic, code2schema, oql)."
                },
                "right_raw": {
                    "type": "object",
                    "description": "Raw adapter input for right source."
                },
                "right_source_type": {
                    "type": "string",
                    "description": "Source adapter kind (e.g. github, markdown, sumd, curllm, code2logic, code2schema, oql)."
                }
            },
            "required": ["query"]
        }
        self_test_schema = {
            "type": "object",
            "properties": {}
        }
        envelope_schema = {
            "type": "object",
            "properties": {
                "envelope": {
                    "type": ["string", "object"],
                    "description": "Subactor delegation envelope string or dictionary."
                }
            },
            "required": ["envelope"]
        }
        healing_schema = {
            "type": "object",
            "properties": {
                "query": {
                    "type": "object",
                    "description": "Canonical query dictionary."
                },
                "left_observation": {
                    "type": "object",
                    "description": "Baseline/expected left observation dictionary."
                },
                "right_observation": {
                    "type": "object",
                    "description": "Observed right observation dictionary with discrepancies."
                }
            },
            "required": ["query", "left_observation", "right_observation"]
        }
        discovery_schema = {
            "type": "object",
            "properties": {
                "sources": {
                    "type": "array", "minItems": 1, "maxItems": 32,
                    "items": {
                        "type": "object",
                        "properties": {
                            "uri": {"type": "string"},
                            "document": {"type": ["object", "array"]},
                        },
                        "required": ["uri", "document"],
                    },
                },
                "query": {"type": ["string", "null"]},
            },
            "required": ["sources"],
        }
        return [
            {
                "name": "data2dsl_compare",
                "description": (
                    "Compare two evidence-bearing observations (e.g. GitHub commit "
                    "metrics, work summary claims, SUMD tables, or browser extractions) against a "
                    "formal query deterministically."
                ),
                "inputSchema": compare_schema,
                "parameters": compare_schema,
            },
            {
                "name": "data2dsl_self_test",
                "description": "Run the built-in self-test suite verifying comparator integrity and schema conformance.",
                "inputSchema": self_test_schema,
                "parameters": self_test_schema,
            },
            {
                "name": "data2dsl_validate_envelope",
                "description": "Validate a Subactor delegation envelope payload in text or dictionary format.",
                "inputSchema": envelope_schema,
                "parameters": envelope_schema,
            },
            {
                "name": "data2dsl_simulate_healing",
                "description": "Simulate a closed-loop DETECT -> PLAN -> EXECUTE -> VERIFY -> HEAL self-healing cycle.",
                "inputSchema": healing_schema,
                "parameters": healing_schema,
            },
            {
                "name": "data2dsl_discover_data",
                "description": "Build or query a deterministic evidence graph from explicit JSON registries and projections.",
                "inputSchema": discovery_schema,
                "parameters": discovery_schema,
            },
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
            if left_observation is None:
                if left_raw is not None and left_source_type is not None:
                    left_observation = _normalize_raw(left_source_type, left_raw, query, side="left")
                else:
                    return {
                        "status": "ERROR",
                        "error_code": "MISSING_LEFT_OBSERVATION",
                        "message": "Either left_observation or (left_raw and left_source_type) must be provided."
                    }

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

    @classmethod
    def execute_validate_envelope(cls, envelope: Any) -> Dict[str, Any]:
        """Validate a Subactor delegation envelope."""
        try:
            env = validate_delegation_envelope(envelope)
            return {
                "status": "OK" if env.valid else "INVALID",
                "envelope": env.to_dict(),
            }
        except Exception as exc:
            return {
                "status": "ERROR",
                "error_code": "ENVELOPE_VALIDATION_EXCEPTION",
                "message": str(exc),
            }

    @classmethod
    def execute_simulate_healing(
        cls,
        query: Dict[str, Any],
        left_observation: Dict[str, Any],
        right_observation: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Run simulated self-healing cycle."""
        try:
            res = simulate_self_healing_cycle(query, left_observation, right_observation)
            return {
                "status": "OK",
                "healing_result": res,
            }
        except Exception as exc:
            return {
                "status": "ERROR",
                "error_code": "HEALING_SIMULATION_EXCEPTION",
                "message": str(exc),
            }

    @classmethod
    def execute_discover_data(
        cls, sources: list[Dict[str, Any]], query: str | None = None,
    ) -> Dict[str, Any]:
        """Build a bounded graph without implicit filesystem or network reads."""
        try:
            return {"status": "OK", "graph": discover_data_network(sources, query=query)}
        except (DiscoveryError, TypeError, ValueError) as exc:
            return {"status": "ERROR", "error_code": "DISCOVERY_INVALID", "message": str(exc)}


def urirun_bindings() -> Dict[str, Any]:
    """Return urirun bindings descriptor and router for data2dsl:// URI schemes."""
    def _route_compare(payload: Dict[str, Any]) -> Dict[str, Any]:
        return Data2DslSkill.execute_compare(**payload)

    def _route_selftest(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return Data2DslSkill.self_test()

    def _route_validate_envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
        return Data2DslSkill.execute_validate_envelope(**payload)

    def _route_simulate_healing(payload: Dict[str, Any]) -> Dict[str, Any]:
        return Data2DslSkill.execute_simulate_healing(**payload)

    return {
        "scheme": "data2dsl",
        "version": Data2DslSkill.VERSION,
        "routes": {
            "data2dsl://host/compare/run": _route_compare,
            "data2dsl://host/selftest/run": _route_selftest,
            "data2dsl://host/subactor/validate": _route_validate_envelope,
            "data2dsl://host/healing/simulate": _route_simulate_healing,
        },
        "handler": lambda route, payload: {
            "data2dsl://host/compare/run": _route_compare,
            "data2dsl://host/selftest/run": _route_selftest,
            "data2dsl://host/subactor/validate": _route_validate_envelope,
            "data2dsl://host/healing/simulate": _route_simulate_healing,
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
