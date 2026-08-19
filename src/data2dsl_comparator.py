"""Deterministic comparator for data2dsl observations.

This module compares two normalized observations (left and right) against a
bounded query according to explicit scalar/set equality rules, producing a
canonical comparison result with typed deltas and sorted evidence references.
"""

from __future__ import annotations

from typing import Any


DEFAULT_PROFILE_BINDINGS = {
    "query": "wellmanifest.dsl/profile/query/v1",
    "observation": "wellmanifest.dsl/profile/observation/v1",
    "result": "wellmanifest.dsl/profile/result/v1",
    "revision": "0e088f9efa06a903d1674f42b8ac6afaa0fdf071",
    "contract_digest": "sha256:85010d33a3a1a5a311ad73591b0676b184f475d2aa5323bd2e32ef6d7aca3bd1",
}

SCHEMA_BUNDLE = "autogrammar.data2dsl/comparison-bundle/v0"
SCHEMA_RESULT = "autogrammar.data2dsl/comparison-result/v0"


class DeterministicComparator:
    """Performs deterministic comparison of two normalized observations."""

    def __init__(self, profile_bindings: dict[str, str] | None = None) -> None:
        self._profile_bindings = profile_bindings or DEFAULT_PROFILE_BINDINGS

    def compare(
        self,
        query: dict[str, Any],
        left: dict[str, Any] | None,
        right: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Compare left and right observations against the query, returning a full comparison bundle."""
        query_id = query["query_id"]
        policy = query["comparison"]

        observations: list[dict[str, Any]] = []
        evidence_ids: set[str] = set()

        if left is not None:
            observations.append(left)
            for ev in left.get("evidence", []):
                evidence_ids.add(ev["evidence_id"])

        if right is not None:
            observations.append(right)
            for ev in right.get("evidence", []):
                evidence_ids.add(ev["evidence_id"])

        left_id = left["observation_id"] if left else None
        right_id = right["observation_id"] if right else None

        if left is None:
            outcome = "MISSING_LEFT"
            delta = None
        elif right is None:
            outcome = "MISSING_RIGHT"
            delta = None
        elif left.get("state") != "OBSERVED" or right.get("state") != "OBSERVED":
            outcome = "UNEVALUABLE"
            delta = None
        else:
            outcome, delta = self._compare_values(left["value"], right["value"])

        result = {
            "schema": SCHEMA_RESULT,
            "query_id": query_id,
            "outcome": outcome,
            "left_observation_id": left_id,
            "right_observation_id": right_id,
            "delta": delta,
            "evidence_ids": sorted(evidence_ids),
            "comparison": policy,
        }

        return {
            "schema": SCHEMA_BUNDLE,
            "profile_bindings": self._profile_bindings,
            "query": query,
            "observations": observations,
            "result": result,
        }

    def _compare_values(
        self, left_val: dict[str, Any], right_val: dict[str, Any]
    ) -> tuple[str, dict[str, Any] | None]:
        kind = left_val["kind"]
        if kind == "integer":
            left_num = int(left_val["value"])
            right_num = int(right_val["value"])
            if left_num == right_num:
                return "MATCH", None
            return "CONFLICT", {"kind": "integer", "value": str(right_num - left_num)}

        if kind == "string":
            left_str = left_val["value"]
            right_str = right_val["value"]
            if left_str == right_str:
                return "MATCH", None
            return "CONFLICT", None

        if kind == "string-set":
            left_set = set(left_val["items"])
            right_set = set(right_val["items"])
            if left_set == right_set:
                return "MATCH", None
            return "CONFLICT", {
                "kind": "string-set",
                "added": sorted(right_set - left_set),
                "removed": sorted(left_set - right_set),
            }

        raise ValueError(f"Unsupported value kind: {kind}")


def compare_observations(
    query: dict[str, Any],
    left: dict[str, Any] | None,
    right: dict[str, Any] | None,
) -> dict[str, Any]:
    """Helper function to execute deterministic comparison."""
    comparator = DeterministicComparator()
    return comparator.compare(query, left, right)
