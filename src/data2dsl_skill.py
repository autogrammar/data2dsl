"""
data2dsl agent skill and tool interface.

Conforms to the wellmanifest/skills specification for governed agent tools.
Provides programmatic tool execution for comparing observations deterministically.
"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, Optional

from data2dsl_comparator import DeterministicComparator
from data2dsl_contract_v0.validate import self_test as contract_self_test
from data2dsl_discovery import DiscoveryError, discover_data_network
from data2dsl_subactor import simulate_self_healing_cycle, validate_delegation_envelope
from data2dsl_skill_norms import _NORMALIZERS


def _normalize_raw(source_type: str, raw: Dict[str, Any], query: Dict[str, Any], side: str = "left") -> Dict[str, Any]:
    """Helper to normalize raw input via corresponding source adapter."""
    st = source_type.lower().replace("-", "_")
    handler = _NORMALIZERS.get(st)
    if handler is None:
        raise ValueError(f"Unknown source adapter kind: {source_type}")
    return handler(st, raw, query, side)


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
                "query": {
                    "oneOf": [
                        {"type": "string", "maxLength": 80},
                        {
                            "type": "array", "minItems": 1, "maxItems": 16,
                            "items": {"type": "string", "minLength": 1, "maxLength": 80},
                        },
                        {"type": "null"},
                    ]
                },
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

            if right_observation is None:
                if right_raw is not None and right_source_type is not None:
                    right_observation = _normalize_raw(right_source_type, right_raw, query, side="right")

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
        cls, sources: list[Dict[str, Any]], query: str | list[str] | None = None,
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


from data2dsl_skill_mcp import handle_mcp_message, main_mcp  # noqa: F401,E402
