"""Tests verifying robust deserialization of raw nested dictionary payloads in data2dsl_skill._normalize_raw (F07)."""

from data2dsl_skill import _normalize_raw


def _make_query(source_kind: str, metric_id: str, value_kind: str = "integer", equality: str = "integer-exact"):
    return {
        "schema": "autogrammar.data2dsl/query/v0",
        "query_id": "query:skill:raw_test",
        "subject": {
            "repository": "https://github.com/autogrammar/data2dsl",
            "actor": "antigravity",
        },
        "metric": {
            "id": metric_id,
            "version": "v1",
            "value_kind": value_kind,
            "unit": "items",
        },
        "window": {
            "start": "2026-08-01T00:00:00Z",
            "end": "2026-08-27T00:00:00Z",
            "semantics": "half-open-utc",
        },
        "left_source": {"id": f"source:{source_kind}", "kind": source_kind},
        "right_source": {"id": f"source:{source_kind}", "kind": source_kind},
        "comparison": {
            "equality": equality,
            "delta_direction": "right-minus-left",
            "missing_is_zero": False,
        },
    }


def test_planfile_raw_dict_tickets_deserialization():
    """F07: Planfile raw dictionary containing list of ticket dicts must be parsed without error."""
    query = _make_query("planfile", "planfile.tickets.count")
    raw_payload = {
        "status": "OK",
        "count": 2,
        "tickets": [
            {"ticket_id": "TICK-1", "title": "First", "status": "DONE", "path": "planfile.yaml", "start_line": 1, "end_line": 5},
            {"ticket_id": "TICK-2", "title": "Second", "status": "OPEN", "path": "planfile.yaml", "start_line": 6, "end_line": 10},
        ],
    }

    obs = _normalize_raw("planfile", raw_payload, query, side="right")
    assert obs["state"] == "OBSERVED"
    assert obs["value"] == {"kind": "integer", "value": "2"}
    assert len(obs["evidence"]) == 2
    assert obs["evidence"][0]["location"]["kind"] == "yaml-lines"


def test_curllm_raw_dict_pages_deserialization():
    """F07: Curllm raw dictionary containing list of page dicts must be parsed without error."""
    query = _make_query("curllm", "curllm.metric.count")
    raw_payload = {
        "value": 42,
        "pages": [
            {"url": "https://example.com/api", "digest_sha256": "c" * 64, "page": 1, "endpoint": "/api", "status_code": 200}
        ],
    }

    obs = _normalize_raw("curllm", raw_payload, query, side="right")
    assert obs["state"] == "OBSERVED"
    assert obs["value"] == {"kind": "integer", "value": "42"}
    assert len(obs["evidence"]) == 1
    assert obs["evidence"][0]["digest_sha256"] == "c" * 64


def test_deta_raw_dict_services_deserialization():
    """F07: Deta raw dictionary containing list of service dicts must be parsed without error."""
    query = _make_query("deta", "deta.services.count")
    raw_payload = {
        "status": "OK",
        "service_count": 2,
        "services": [
            {"name": "web", "service_type": "frontend", "ports": ["80"], "manifest_path": "compose.yml", "start_line": 1, "end_line": 5},
            {"name": "db", "service_type": "database", "ports": ["5432"], "manifest_path": "compose.yml", "start_line": 6, "end_line": 10},
        ],
        "ports": ["80", "5432"],
    }

    obs = _normalize_raw("deta", raw_payload, query, side="left")
    assert obs["state"] == "OBSERVED"
    assert obs["value"] == {"kind": "integer", "value": "2"}
    assert len(obs["evidence"]) == 2
