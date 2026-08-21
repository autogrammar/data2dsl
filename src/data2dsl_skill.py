"""
data2dsl agent skill and tool interface.

Conforms to the wellmanifest/skills specification for governed agent tools.
Provides programmatic tool execution for comparing observations deterministically.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from data2dsl_adapters import (
    Code2LogicAdapter,
    Code2LogicMetricResponse,
    Code2SchemaAdapter,
    Code2SchemaMetricResponse,
    CurllmAdapter,
    CurllmMetricResponse,
    DiagitCommitMetricResponse,
    GitHubDiagitAdapter,
    WorkSummaryMarkdownAdapter,
)
from data2dsl_comparator import DeterministicComparator
from data2dsl_contract_v0.validate import self_test as contract_self_test


def _normalize_raw(source_type: str, raw: Dict[str, Any], query: Dict[str, Any], side: str = "left") -> Dict[str, Any]:
    """Helper to normalize raw input via corresponding source adapter."""
    if source_type == "markdown":
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
    elif source_type == "github":
        adapter = GitHubDiagitAdapter()
        resp = DiagitCommitMetricResponse(
            status="OK" if raw.get("commit_count") is not None else "NOT_FOUND",
            commit_count=raw.get("commit_count"),
        )
        return adapter.normalize(query, resp, side=side)
    elif source_type == "curllm":
        adapter = CurllmAdapter()
        resp = raw.get("response")
        if not isinstance(resp, CurllmMetricResponse):
            resp = CurllmMetricResponse(
                status="OK" if raw.get("value") is not None else "ERROR",
                value=raw.get("value"),
            )
        return adapter.normalize(query, resp, side=side)
    elif source_type == "code2logic":
        adapter = Code2LogicAdapter()
        resp = raw.get("response")
        if not isinstance(resp, Code2LogicMetricResponse):
            resp = Code2LogicMetricResponse(
                status="OK" if raw.get("value") is not None else "ERROR",
                value=raw.get("value"),
            )
        return adapter.normalize(query, resp, side=side)
    elif source_type == "code2schema":
        adapter = Code2SchemaAdapter()
        resp = raw.get("response")
        if not isinstance(resp, Code2SchemaMetricResponse):
            entities = raw.get("entities") if raw.get("entities") is not None else raw.get("value", ())
            resp = Code2SchemaMetricResponse(
                status="OK" if entities is not None else "ERROR",
                entities=entities if isinstance(entities, (list, tuple)) else (entities,),
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
