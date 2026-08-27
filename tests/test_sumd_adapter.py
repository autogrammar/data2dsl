from data2dsl_adapters import SUMDAdapter, SUMDMetricResponse


SUMD_TABLE_MARKDOWN = """
# Execution Summary

| Metric | Value | Status |
| :--- | :--- | :--- |
| tasks_completed | 15 | OK |
| error_rate | 2.5% | OK |
| active_services | auth, billing, gateway | OK |
"""

SUMD_DESCRIPTOR_MARKDOWN = """
---
descriptor: sumd.exec.v1
---
tasks_completed: 25
throughput_score: 98.4
"""

QUERY_INTEGER = {
    "schema": "autogrammar.data2dsl/query/v0",
    "query_id": "query:sumd:tasks",
    "subject": {
        "repository": "https://github.com/autogrammar/data2dsl",
        "actor": "github:alice",
    },
    "metric": {
        "id": "tasks_completed",
        "version": "v1",
        "value_kind": "integer",
        "unit": "count",
    },
    "window": {
        "start": "2026-08-01T00:00:00Z",
        "end": "2026-08-15T00:00:00Z",
        "semantics": "half-open-utc",
    },
    "left_source": {"id": "source:sumd", "kind": "sumd"},
    "right_source": {"id": "source:diagit", "kind": "github"},
    "comparison": {
        "equality": "integer-exact",
        "delta_direction": "right-minus-left",
        "missing_is_zero": False,
    },
}

QUERY_PERCENTAGE = {
    "schema": "autogrammar.data2dsl/query/v0",
    "query_id": "query:sumd:error_rate",
    "subject": {
        "repository": "https://github.com/autogrammar/data2dsl",
        "actor": "github:alice",
    },
    "metric": {
        "id": "error_rate",
        "version": "v1",
        "value_kind": "percentage",
        "unit": "percent",
    },
    "window": {
        "start": "2026-08-01T00:00:00Z",
        "end": "2026-08-15T00:00:00Z",
        "semantics": "half-open-utc",
    },
    "left_source": {"id": "source:sumd", "kind": "sumd"},
    "right_source": {"id": "source:diagit", "kind": "github"},
    "comparison": {
        "equality": "percentage-exact",
        "delta_direction": "right-minus-left",
        "missing_is_zero": False,
    },
}

QUERY_STRING_SET = {
    "schema": "autogrammar.data2dsl/query/v0",
    "query_id": "query:sumd:services",
    "subject": {
        "repository": "https://github.com/autogrammar/data2dsl",
        "actor": "github:alice",
    },
    "metric": {
        "id": "active_services",
        "version": "v1",
        "value_kind": "string-set",
        "unit": "set",
    },
    "window": {
        "start": "2026-08-01T00:00:00Z",
        "end": "2026-08-15T00:00:00Z",
        "semantics": "half-open-utc",
    },
    "left_source": {"id": "source:sumd", "kind": "sumd"},
    "right_source": {"id": "source:deta", "kind": "deta"},
    "comparison": {
        "equality": "set-exact",
        "delta_direction": "right-minus-left",
        "missing_is_zero": False,
    },
}


def test_sumd_adapter_extract_table_integer():
    adapter = SUMDAdapter()
    resp = adapter.extract_table_metric(SUMD_TABLE_MARKDOWN, "tasks_completed")
    assert resp is not None
    assert resp.status == "OK"
    assert resp.value == 15
    assert resp.value_kind == "integer"

    obs = adapter.normalize(QUERY_INTEGER, resp, side="left")
    assert obs["state"] == "OBSERVED"
    assert obs["value"] == {"kind": "integer", "value": "15"}
    assert len(obs["evidence"]) == 1


def test_sumd_adapter_extract_table_percentage():
    adapter = SUMDAdapter()
    resp = adapter.extract_table_metric(SUMD_TABLE_MARKDOWN, "error_rate")
    assert resp is not None
    assert resp.value == 2.5
    assert resp.value_kind == "percentage"

    obs = adapter.normalize(QUERY_PERCENTAGE, resp, side="left")
    assert obs["state"] == "OBSERVED"
    assert obs["value"] == {"kind": "percentage", "value": "2.5%"}


def test_sumd_adapter_extract_table_string_set():
    adapter = SUMDAdapter()
    resp = adapter.extract_table_metric(SUMD_TABLE_MARKDOWN, "active_services")
    assert resp is not None
    assert isinstance(resp.value, list)
    assert "auth" in resp.value

    obs = adapter.normalize(QUERY_STRING_SET, resp, side="left")
    assert obs["state"] == "OBSERVED"
    assert obs["value"] == {"kind": "string-set", "items": ["auth", "billing", "gateway"]}


def test_sumd_adapter_extract_descriptor():
    adapter = SUMDAdapter()
    resp = adapter.extract_table_metric(SUMD_DESCRIPTOR_MARKDOWN, "tasks_completed")
    assert resp is not None
    assert resp.value == 25

    obs = adapter.normalize(QUERY_INTEGER, resp, side="left")
    assert obs["value"] == {"kind": "integer", "value": "25"}


def test_sumd_adapter_missing_metric():
    adapter = SUMDAdapter()
    resp = adapter.extract_table_metric(SUMD_TABLE_MARKDOWN, "non_existent_metric")
    assert resp is None

    obs = adapter.normalize(QUERY_INTEGER, None, side="left")
    assert obs["state"] == "UNEVALUABLE"
    assert obs["value"] is None
