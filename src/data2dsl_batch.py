"""
Batch Multi-Query Comparison Engine for data2dsl.

Enables evaluating multiple formal queries against observation sets in a single
reproducible, deterministic batch execution.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence

from data2dsl_comparator import DeterministicComparator


def _compute_sha256(content: str | bytes) -> str:
    if isinstance(content, str):
        content = content.encode("utf-8")
    return hashlib.sha256(content).hexdigest()


@dataclass(frozen=True)
class BatchComparisonSummary:
    """Summary metrics for a batch comparison execution."""

    total_queries: int
    matches: int
    conflicts: int
    missing_left: int
    missing_right: int
    unevaluable: int
    clean_ratio: float
    is_clean: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_queries": self.total_queries,
            "matches": self.matches,
            "conflicts": self.conflicts,
            "missing_left": self.missing_left,
            "missing_right": self.missing_right,
            "unevaluable": self.unevaluable,
            "clean_ratio": round(self.clean_ratio, 4),
            "is_clean": self.is_clean,
        }


@dataclass(frozen=True)
class BatchComparisonReport:
    """Complete batch comparison execution report."""

    schema: str
    batch_id: str
    summary: BatchComparisonSummary
    bundles: Sequence[Dict[str, Any]]
    digest_sha256: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema": self.schema,
            "batch_id": self.batch_id,
            "summary": self.summary.to_dict(),
            "bundles": list(self.bundles),
            "digest_sha256": self.digest_sha256,
        }


class BatchMultiQueryComparator:
    """Executes multiple queries against observation pools deterministically."""

    SCHEMA = "autogrammar.data2dsl/batch-report/v0"

    def __init__(self, comparator: Optional[DeterministicComparator] = None) -> None:
        self._comparator = comparator or DeterministicComparator()

    def compare_batch(
        self,
        queries: Sequence[Dict[str, Any]],
        left_observations: Sequence[Dict[str, Any]] | Dict[str, Dict[str, Any]],
        right_observations: Sequence[Dict[str, Any]] | Dict[str, Dict[str, Any]],
        batch_id: Optional[str] = None,
    ) -> BatchComparisonReport:
        """Run batch comparison for all queries."""
        # Index left observations
        left_map: Dict[str, Dict[str, Any]] = {}
        if isinstance(left_observations, dict):
            left_map = dict(left_observations)
        else:
            for obs in left_observations:
                if not isinstance(obs, dict):
                    continue
                if "query_id" in obs:
                    left_map[obs["query_id"]] = obs
                if "metric" in obs and isinstance(obs["metric"], dict) and "id" in obs["metric"]:
                    left_map[f"metric:{obs['metric']['id']}"] = obs

        # Index right observations
        right_map: Dict[str, Dict[str, Any]] = {}
        if isinstance(right_observations, dict):
            right_map = dict(right_observations)
        else:
            for obs in right_observations:
                if not isinstance(obs, dict):
                    continue
                if "query_id" in obs:
                    right_map[obs["query_id"]] = obs
                if "metric" in obs and isinstance(obs["metric"], dict) and "id" in obs["metric"]:
                    right_map[f"metric:{obs['metric']['id']}"] = obs

        bundles: List[Dict[str, Any]] = []
        matches = 0
        conflicts = 0
        missing_left = 0
        missing_right = 0
        unevaluable = 0

        for q in queries:
            qid = q.get("query_id", "")
            mid = q.get("metric", {}).get("id", "")

            left_obs = left_map.get(qid) or left_map.get(f"metric:{mid}")
            right_obs = right_map.get(qid) or right_map.get(f"metric:{mid}")

            # Synthesize missing observations if not in map
            if left_obs is None:
                left_obs = {
                    "schema": "autogrammar.data2dsl/observation/v0",
                    "observation_id": f"observation:missing:left:{qid}",
                    "query_id": qid,
                    "side": "left",
                    "subject": q.get("subject", {}),
                    "metric": q.get("metric", {}),
                    "window": q.get("window", {}),
                    "state": "MISSING",
                    "value": None,
                    "evidence": [],
                }
            if right_obs is None:
                right_obs = {
                    "schema": "autogrammar.data2dsl/observation/v0",
                    "observation_id": f"observation:missing:right:{qid}",
                    "query_id": qid,
                    "side": "right",
                    "subject": q.get("subject", {}),
                    "metric": q.get("metric", {}),
                    "window": q.get("window", {}),
                    "state": "MISSING",
                    "value": None,
                    "evidence": [],
                }

            bundle = self._comparator.compare(q, left_obs, right_obs)
            bundles.append(bundle)

            outcome = bundle["result"]["outcome"]
            if outcome == "MATCH":
                matches += 1
            elif outcome == "CONFLICT":
                conflicts += 1
            elif outcome == "MISSING_LEFT":
                missing_left += 1
            elif outcome == "MISSING_RIGHT":
                missing_right += 1
            elif outcome == "UNEVALUABLE":
                unevaluable += 1

        total = len(queries)
        clean_ratio = (matches / total) if total > 0 else 1.0
        is_clean = (conflicts == 0 and missing_left == 0 and missing_right == 0 and unevaluable == 0 and matches == total)

        summary = BatchComparisonSummary(
            total_queries=total,
            matches=matches,
            conflicts=conflicts,
            missing_left=missing_left,
            missing_right=missing_right,
            unevaluable=unevaluable,
            clean_ratio=clean_ratio,
            is_clean=is_clean,
        )

        canonical_content = json.dumps(
            {"summary": summary.to_dict(), "bundles": bundles},
            sort_keys=True,
            ensure_ascii=False,
        )
        digest = _compute_sha256(canonical_content)
        resolved_batch_id = batch_id or f"batch:{digest[:12]}"

        return BatchComparisonReport(
            schema=self.SCHEMA,
            batch_id=resolved_batch_id,
            summary=summary,
            bundles=bundles,
            digest_sha256=digest,
        )
