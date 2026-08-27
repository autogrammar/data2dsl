"""
Query Template Generator for data2dsl.

Generates canonical autogrammar.data2dsl/query/v0 query templates for various
source adapters and metric configurations.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


def generate_query_template(
    source_kind: str,
    metric_id: str,
    value_kind: str = "integer",
    repository: str = "https://github.com/autogrammar/data2dsl",
    actor: str = "antigravity",
    equality: str = "exact",
    unit: str = "count",
    right_source_kind: Optional[str] = None,
    query_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate a canonical data2dsl query object."""
    clean_src = source_kind.lower().strip()
    clean_metric = metric_id.strip()

    # Determine default unit if not explicitly overridden
    if value_kind == "percentage":
        unit = "percent"
    elif value_kind == "string-set":
        unit = "set"
    elif "temperature" in clean_metric or "celsius" in clean_metric:
        unit = "celsius"
    elif "rate" in clean_metric or "hz" in clean_metric:
        unit = "hz"
    elif "commit" in clean_metric:
        unit = "commits"

    # Determine default equality
    if equality == "exact":
        if value_kind == "percentage":
            equality = "percentage-exact"
        elif value_kind == "string-set":
            equality = "set-exact"

    resolved_query_id = query_id or f"query:{clean_src}:{clean_metric}"
    r_kind = right_source_kind or ("github" if clean_src == "markdown" else "telemetry" if clean_src == "oql" else "baseline")

    return {
        "schema": "autogrammar.data2dsl/query/v0",
        "query_id": resolved_query_id,
        "subject": {
            "repository": repository,
            "actor": actor,
        },
        "metric": {
            "id": clean_metric,
            "version": "1.0.0",
            "value_kind": value_kind,
            "unit": unit,
        },
        "window": {
            "start": "2026-08-01T00:00:00Z",
            "end": "2026-08-27T00:00:00Z",
            "semantics": "half-open-utc",
        },
        "left_source": {
            "id": f"source:{clean_src}",
            "kind": clean_src,
        },
        "right_source": {
            "id": f"source:{r_kind}",
            "kind": r_kind,
        },
        "comparison": {
            "equality": equality,
            "delta_direction": "right-minus-left",
            "missing_is_zero": False,
        },
    }
