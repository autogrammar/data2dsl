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
        # Index left observations by query_id and by composite (repo, actor, metric_id)
        left_by_qid: Dict[str, Dict[str, Any]] = {}
        left_by_key: Dict[tuple, Dict[str, Any]] = {}
        if isinstance(left_observations, dict):
            left_by_qid = dict(left_observations)
        else:
            for obs in left_observations:
                if not isinstance(obs, dict):
                    continue
                if "query_id" in obs and obs["query_id"]:
                    left_by_qid[obs["query_id"]] = obs
                subj = obs.get("subject", {})
                met = obs.get("metric", {})
                if subj and met and "id" in met:
                    key = (subj.get("repository"), subj.get("actor"), met.get("id"))
                    left_by_key[key] = obs

        # Index right observations by query_id and by composite (repo, actor, metric_id)
        right_by_qid: Dict[str, Dict[str, Any]] = {}
        right_by_key: Dict[tuple, Dict[str, Any]] = {}
        if isinstance(right_observations, dict):
            right_by_qid = dict(right_observations)
        else:
            for obs in right_observations:
                if not isinstance(obs, dict):
                    continue
                if "query_id" in obs and obs["query_id"]:
                    right_by_qid[obs["query_id"]] = obs
                subj = obs.get("subject", {})
                met = obs.get("metric", {})
                if subj and met and "id" in met:
                    key = (subj.get("repository"), subj.get("actor"), met.get("id"))
                    right_by_key[key] = obs

        bundles: List[Dict[str, Any]] = []
        matches = 0
        conflicts = 0
        missing_left = 0
        missing_right = 0
        unevaluable = 0

        for q in queries:
            qid = q.get("query_id", "")
            subj = q.get("subject", {})
            met = q.get("metric", {})
            q_key = (subj.get("repository"), subj.get("actor"), met.get("id")) if subj and met else None

            left_obs = left_by_qid.get(qid)
            if left_obs is None and q_key:
                candidate = left_by_key.get(q_key)
                if candidate and candidate.get("query_id") in (None, "", qid):
                    left_obs = candidate

            right_obs = right_by_qid.get(qid)
            if right_obs is None and q_key:
                candidate = right_by_key.get(q_key)
                if candidate and candidate.get("query_id") in (None, "", qid):
                    right_obs = candidate

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


def _format_val(obs: Any) -> str:
    if not obs or not isinstance(obs, dict):
        return "(missing)"
    val = obs.get("value")
    if val is None:
        return "None" if obs.get("state") == "OBSERVED" else f"({obs.get('state', 'missing').lower()})"
    if isinstance(val, dict):
        if "value" in val:
            return str(val["value"]).replace("|", "\\|")
        if "items" in val:
            items_str = ", ".join(str(i) for i in val.get("items", []))
            return f"[{items_str}]".replace("|", "\\|")
    return str(val).replace("|", "\\|")


def _format_delta(delta: Any) -> str:
    if not delta or not isinstance(delta, dict):
        return "-"
    if "value" in delta:
        return str(delta["value"]).replace("|", "\\|")
    if "added" in delta or "removed" in delta:
        added = ", ".join(str(i) for i in delta.get("added", []))
        removed = ", ".join(str(i) for i in delta.get("removed", []))
        parts = []
        if added:
            parts.append(f"+[{added}]")
        if removed:
            parts.append(f"-[{removed}]")
        res = " ".join(parts) if parts else "-"
        return res.replace("|", "\\|")
    return str(delta).replace("|", "\\|")


def format_markdown_report(report_or_bundle: Any) -> str:
    """Format a batch report or single comparison bundle as a structured Markdown document."""
    if hasattr(report_or_bundle, "to_dict"):
        doc = report_or_bundle.to_dict()
    elif isinstance(report_or_bundle, dict):
        doc = report_or_bundle
    else:
        doc = report_or_bundle

    lines = []
    lines.append("# data2dsl Comparison Report\n")

    if "summary" in doc and "bundles" in doc:
        summary = doc["summary"]
        status_str = "CLEAN (All Match)" if summary.get("is_clean") else "CONFLICTS/DISCREPANCIES DETECTED"
        lines.append("## Summary\n")
        lines.append(f"- **Batch ID**: `{doc.get('batch_id', summary.get('batch_id', 'batch'))}`")
        lines.append(f"- **Status**: `{status_str}`")
        lines.append(f"- **Total Queries**: {summary.get('total_queries', 0)}")
        lines.append(f"- **Matches**: {summary.get('matches', 0)}")
        lines.append(f"- **Conflicts**: {summary.get('conflicts', 0)}")
        lines.append(f"- **Missing Left / Right**: {summary.get('missing_left', 0)} / {summary.get('missing_right', 0)}")
        lines.append(f"- **Unevaluable**: {summary.get('unevaluable', 0)}")
        clean_ratio = summary.get("clean_ratio", 0.0)
        lines.append(f"- **Clean Ratio**: {clean_ratio:.2%}\n")

        lines.append("## Query Details\n")
        lines.append("| Query ID | Metric | Left Value | Right Value | Outcome | Delta |")
        lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")

        for b in doc.get("bundles", []):
            q = b.get("query", {})
            res = b.get("result", {})
            obs = b.get("observations", [])
            qid = q.get("query_id", "")
            mid = q.get("metric", {}).get("id", "")
            outcome = res.get("outcome", "")

            l_obs = None
            r_obs = None
            if isinstance(obs, list):
                for o in obs:
                    if isinstance(o, dict):
                        if o.get("side") == "left":
                            l_obs = o
                        elif o.get("side") == "right":
                            r_obs = o
            elif isinstance(obs, dict):
                l_obs = obs.get("left")
                r_obs = obs.get("right")

            l_val = _format_val(l_obs)
            r_val = _format_val(r_obs)
            delta_val = _format_delta(res.get("delta"))

            lines.append(f"| `{qid}` | `{mid}` | `{l_val}` | `{r_val}` | **{outcome}** | `{delta_val}` |")

    elif "query" in doc and "result" in doc:
        q = doc["query"]
        res = doc["result"]
        obs = doc.get("observations", [])
        qid = q.get("query_id", "")
        mid = q.get("metric", {}).get("id", "")
        outcome = res.get("outcome", "")
        l_obs = None
        r_obs = None
        if isinstance(obs, list):
            for o in obs:
                if isinstance(o, dict):
                    if o.get("side") == "left":
                        l_obs = o
                    elif o.get("side") == "right":
                        r_obs = o
        elif isinstance(obs, dict):
            l_obs = obs.get("left")
            r_obs = obs.get("right")

        l_val = _format_val(l_obs)
        r_val = _format_val(r_obs)
        delta_val = _format_delta(res.get("delta"))

        lines.append("## Single Comparison Result\n")
        lines.append(f"- **Query ID**: `{qid}`")
        lines.append(f"- **Metric**: `{mid}`")
        lines.append(f"- **Outcome**: **{outcome}**")
        lines.append(f"- **Left Value**: `{l_val}`")
        lines.append(f"- **Right Value**: `{r_val}`")
        lines.append(f"- **Delta**: `{delta_val}`")

    return "\n".join(lines) + "\n"
