"""Markdown report rendering for data2dsl batch comparison."""

from __future__ import annotations

from typing import Any


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
        lines.extend(_batch_report_lines(doc))
    elif "query" in doc and "result" in doc:
        lines.extend(_single_report_lines(doc))

    return "\n".join(lines) + "\n"


def _side_observations(obs: Any) -> tuple[Any, Any]:
    """Extract (left, right) observations from a list-of-dicts or a dict."""
    if isinstance(obs, list):
        left = right = None
        for o in obs:
            if isinstance(o, dict):
                if o.get("side") == "left":
                    left = o
                elif o.get("side") == "right":
                    right = o
        return left, right
    if isinstance(obs, dict):
        return obs.get("left"), obs.get("right")
    return None, None


def _batch_report_lines(doc: dict) -> list[str]:
    """Summary table + per-query rows for a batch report document."""
    summary = doc["summary"]
    status_str = "CLEAN (All Match)" if summary.get("is_clean") else "CONFLICTS/DISCREPANCIES DETECTED"
    lines = [
        "## Summary\n",
        f"- **Batch ID**: `{doc.get('batch_id', summary.get('batch_id', 'batch'))}`",
        f"- **Status**: `{status_str}`",
        f"- **Total Queries**: {summary.get('total_queries', 0)}",
        f"- **Matches**: {summary.get('matches', 0)}",
        f"- **Conflicts**: {summary.get('conflicts', 0)}",
        f"- **Missing Left / Right**: {summary.get('missing_left', 0)} / {summary.get('missing_right', 0)}",
        f"- **Unevaluable**: {summary.get('unevaluable', 0)}",
        f"- **Ambiguous**: {summary.get('ambiguous_count', 0)}",
        f"- **Clean Ratio**: {summary.get('clean_ratio', 0.0):.2%}\n",
        "## Query Details\n",
        "| Query ID | Metric | Left Value | Right Value | Outcome | Delta |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |",
    ]
    for b in doc.get("bundles", []):
        lines.append(_bundle_row(b))
    return lines


def _bundle_row(b: dict) -> str:
    q = b.get("query", {})
    res = b.get("result", {})
    l_obs, r_obs = _side_observations(b.get("observations", []))
    qid = q.get("query_id", "")
    mid = q.get("metric", {}).get("id", "")
    outcome = res.get("outcome", "")
    l_val = _format_val(l_obs)
    r_val = _format_val(r_obs)
    delta_val = _format_delta(res.get("delta"))
    return f"| `{qid}` | `{mid}` | `{l_val}` | `{r_val}` | **{outcome}** | `{delta_val}` |"


def _single_report_lines(doc: dict) -> list[str]:
    q = doc["query"]
    res = doc["result"]
    l_obs, r_obs = _side_observations(doc.get("observations", []))
    qid = q.get("query_id", "")
    mid = q.get("metric", {}).get("id", "")
    outcome = res.get("outcome", "")
    return [
        "## Single Comparison Result\n",
        f"- **Query ID**: `{qid}`",
        f"- **Metric**: `{mid}`",
        f"- **Outcome**: **{outcome}**",
        f"- **Left Value**: `{_format_val(l_obs)}`",
        f"- **Right Value**: `{_format_val(r_obs)}`",
        f"- **Delta**: `{_format_delta(res.get('delta'))}`",
    ]



