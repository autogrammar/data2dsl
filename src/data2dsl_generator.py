"""
Query Template Generator for data2dsl.

Generates canonical autogrammar.data2dsl/query/v0 query templates for various
source adapters and metric configurations.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional


# Valid source kinds from the comparison contract schema.
VALID_SOURCE_KINDS = frozenset([
    "markdown", "github", "code2logic", "code2schema", "curllm",
    "planfile", "deta", "intent_contract", "oql", "sumd",
])

# Map value_kind to the contract's equality policy name.
_EQUALITY_MAP = {
    "integer": "integer-exact",
    "float": "float-exact",
    "percentage": "percentage-exact",
    "string": "string-exact",
    "string-set": "string-set-exact",
}

# Default right-side source kind per left-side source kind.
_DEFAULT_RIGHT_SOURCE = {
    "markdown": "github",
    "oql": "oql",
    "sumd": "sumd",
    "planfile": "planfile",
    "deta": "deta",
    "intent_contract": "intent_contract",
    "code2logic": "code2logic",
    "code2schema": "code2schema",
    "curllm": "curllm",
    "github": "markdown",
}


def generate_query_template(
    source_kind: str,
    metric_id: str,
    value_kind: str = "integer",
    repository: str = "https://github.com/autogrammar/data2dsl",
    actor: str = "antigravity",
    equality: Optional[str] = None,
    unit: str = "count",
    right_source_kind: Optional[str] = None,
    query_id: Optional[str] = None,
    window_start: Optional[str] = None,
    window_end: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate a canonical data2dsl query object.

    All generated queries conform to autogrammar.data2dsl/query/v0 and pass
    the comparison contract validator.
    """
    clean_src = source_kind.lower().strip()
    clean_metric = metric_id.strip()
    unit = _default_unit(value_kind, clean_metric, unit)
    equality = _resolve_equality(equality, value_kind)

    resolved_query_id = query_id or f"query:{clean_src}:{clean_metric}"
    r_kind = right_source_kind or _DEFAULT_RIGHT_SOURCE.get(clean_src, clean_src)
    w_start, w_end = _resolve_window(window_start, window_end)

    return {
        "schema": "autogrammar.data2dsl/query/v0",
        "query_id": resolved_query_id,
        "subject": {
            "repository": repository,
            "actor": actor,
        },
        "metric": {
            "id": clean_metric,
            "version": "v1",
            "value_kind": value_kind,
            "unit": unit,
        },
        "window": {
            "start": w_start,
            "end": w_end,
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


def _default_unit(value_kind: str, clean_metric: str, unit: str) -> str:
    """Derive the default unit from value_kind or metric naming."""
    if value_kind == "percentage":
        return "percent"
    if value_kind == "string-set":
        return "set"
    if "temperature" in clean_metric or "celsius" in clean_metric:
        return "celsius"
    if "rate" in clean_metric or "hz" in clean_metric:
        return "hz"
    if "commit" in clean_metric:
        return "commits"
    return unit


def _resolve_equality(equality: Optional[str], value_kind: str) -> str:
    """Map the requested equality to the contract's vocabulary."""
    if equality is None or equality == "exact":
        return _EQUALITY_MAP.get(value_kind, "integer-exact")
    if equality == "set-exact":
        # Legacy alias; map to the contract form.
        return "string-set-exact"
    return equality


def _resolve_window(window_start: Optional[str], window_end: Optional[str]) -> tuple[str, str]:
    """Default to the current month when either bound is missing."""
    if window_start is not None and window_end is not None:
        return window_start, window_end
    now = datetime.now(timezone.utc)
    return (
        window_start or f"{now.year}-{now.month:02d}-01T00:00:00Z",
        window_end or now.strftime("%Y-%m-%dT00:00:00Z"),
    )
