"""
data2dsl agent skill and tool interface.

Conforms to the wellmanifest/skills specification for governed agent tools.
Provides programmatic tool execution for comparing observations deterministically.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional, Union

from data2dsl_adapters import normalize_observation
from data2dsl_comparator import compare
from data2dsl_contract_v0.validate import self_test as contract_self_test


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
        passed = contract_self_test()
        return {
            "status": "PASS" if passed else "FAIL",
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
                    left_norm = normalize_observation(left_source_type, left_raw)
                    left_observation = left_norm.to_dict()
                else:
                    return {
                        "status": "ERROR",
                        "error_code": "MISSING_LEFT_OBSERVATION",
                        "message": "Either left_observation or (left_raw and left_source_type) must be provided."
                    }

            # Resolve right observation
            if right_observation is None:
                if right_raw is not None and right_source_type is not None:
                    right_norm = normalize_observation(right_source_type, right_raw)
                    right_observation = right_norm.to_dict()
                else:
                    return {
                        "status": "ERROR",
                        "error_code": "MISSING_RIGHT_OBSERVATION",
                        "message": "Either right_observation or (right_raw and right_source_type) must be provided."
                    }

            result = compare(query, left_observation, right_observation)
            return {
                "status": "OK",
                "result": result.to_dict()
            }
        except Exception as exc:
            return {
                "status": "ERROR",
                "error_code": "COMPARISON_EXCEPTION",
                "message": str(exc)
            }
