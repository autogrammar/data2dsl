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
from data2dsl_batch_report import format_markdown_report  # noqa: F401

_AMBIGUOUS = object()

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
    ambiguous_count: int
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
            "ambiguous_count": self.ambiguous_count,
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
        left_by_qid, left_by_key = _index_observations(left_observations)
        right_by_qid, right_by_key = _index_observations(right_observations)

        bundles: List[Dict[str, Any]] = []
        counts = {"MATCH": 0, "CONFLICT": 0, "MISSING_LEFT": 0, "MISSING_RIGHT": 0, "UNEVALUABLE": 0}
        ambiguous_count = 0

        for q in queries:
            left_obs, left_ambiguous = _resolve_observation(q, left_by_qid, left_by_key, "left")
            right_obs, right_ambiguous = _resolve_observation(q, right_by_qid, right_by_key, "right")
            if left_ambiguous or right_ambiguous:
                ambiguous_count += 1

            bundle = self._comparator.compare(q, left_obs, right_obs)
            bundles.append(bundle)
            outcome = bundle["result"]["outcome"]
            if outcome in counts:
                counts[outcome] += 1

        total = len(queries)
        matches = counts["MATCH"]
        conflicts = counts["CONFLICT"]
        missing_left = counts["MISSING_LEFT"]
        missing_right = counts["MISSING_RIGHT"]
        unevaluable = counts["UNEVALUABLE"]
        clean_ratio = (matches / total) if total > 0 else 1.0
        is_clean = (conflicts == 0 and missing_left == 0 and missing_right == 0 and unevaluable == 0 and ambiguous_count == 0 and matches == total)

        summary = BatchComparisonSummary(
            total_queries=total,
            matches=matches,
            conflicts=conflicts,
            missing_left=missing_left,
            missing_right=missing_right,
            unevaluable=unevaluable,
            ambiguous_count=ambiguous_count,
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


def _index_observations(
    observations: Sequence[Dict[str, Any]] | Dict[str, Dict[str, Any]],
) -> tuple[Dict[str, Any], Dict[tuple, Any]]:
    """Index observations by query_id and by composite (repo, actor, metric_id)."""
    by_qid: Dict[str, Any] = {}
    by_key: Dict[tuple, Any] = {}
    if isinstance(observations, dict):
        return dict(observations), by_key
    for obs in observations:
        if not isinstance(obs, dict):
            continue
        if obs.get("query_id"):
            _add_obs(by_qid, obs["query_id"], obs)
        subj = obs.get("subject", {})
        met = obs.get("metric", {})
        if subj and met and "id" in met:
            key = (subj.get("repository"), subj.get("actor"), met.get("id"))
            _add_obs(by_key, key, obs)
    return by_qid, by_key


def _add_obs(d: dict, k: Any, obs: dict) -> None:
    if k in d:
        ext = d[k]
        if ext is not _AMBIGUOUS:
            if ext.get("value", {}) != obs.get("value", {}):
                d[k] = _AMBIGUOUS
    else:
        d[k] = obs


def _resolve_observation(
    query: Dict[str, Any],
    by_qid: Dict[str, Any],
    by_key: Dict[tuple, Any],
    side: str,
) -> tuple[Any, bool]:
    """Resolve the observation for one query side; ambiguity yields an UNEVALUABLE stub."""
    qid = query.get("query_id", "")
    subj = query.get("subject", {})
    met = query.get("metric", {})
    q_key = (subj.get("repository"), subj.get("actor"), met.get("id")) if subj and met else None

    obs = by_qid.get(qid)
    if obs is None and q_key:
        candidate = by_key.get(q_key)
        if candidate and (candidate is _AMBIGUOUS or candidate.get("query_id") in (None, "", qid)):
            obs = candidate

    if obs is _AMBIGUOUS:
        return {
            "observation_id": f"ambiguous:{qid}:{side}",
            "query_id": qid,
            "side": side,
            "subject": query.get("subject", {}),
            "metric": query.get("metric", {}),
            "window": query.get("window", {}),
            "state": "UNEVALUABLE",
            "evidence": [],
        }, True
    return obs, False
