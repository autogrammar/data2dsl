"""Tests verifying harmony between DeterministicComparator and validate_document for float & percentage values (F11)."""

from data2dsl_comparator import DeterministicComparator
from data2dsl_contract_v0.validate import validate_document


def _create_bundle_fixture(value_kind: str, left_val: str, right_val: str):
    equality = f"{value_kind}-exact"
    unit = "percent" if value_kind == "percentage" else "hz"
    query = {
        "schema": "autogrammar.data2dsl/query/v0",
        "query_id": f"query:test:{value_kind}",
        "subject": {
            "repository": "https://github.com/autogrammar/data2dsl",
            "actor": "antigravity",
        },
        "metric": {
            "id": f"test.{value_kind}.metric",
            "version": "v1",
            "value_kind": value_kind,
            "unit": unit,
        },
        "window": {
            "start": "2026-08-01T00:00:00Z",
            "end": "2026-08-27T00:00:00Z",
            "semantics": "half-open-utc",
        },
        "left_source": {"id": "source:oql", "kind": "oql"},
        "right_source": {"id": "source:oql", "kind": "oql"},
        "comparison": {
            "equality": equality,
            "delta_direction": "right-minus-left",
            "missing_is_zero": False,
        },
    }

    left_obs = {
        "schema": "autogrammar.data2dsl/observation/v0",
        "observation_id": "obs:left:1",
        "query_id": query["query_id"],
        "side": "left",
        "subject": dict(query["subject"]),
        "metric": dict(query["metric"]),
        "window": dict(query["window"]),
        "state": "OBSERVED",
        "value": {"kind": value_kind, "value": left_val},
        "evidence": [
            {
                "evidence_id": "ev:left:1",
                "target_uri": "https://github.com/autogrammar/data2dsl",
                "source_uri": "https://github.com/autogrammar/data2dsl",
                "source_revision": "sha256:" + "a" * 64,
                "media_type": "application/json",
                "digest_sha256": "a" * 64,
                "extractor": {"id": "test", "version": "1.0.0"},
                "location": {"kind": "oql-scenario", "path": "spec.json", "start_line": 1, "end_line": 1},
            }
        ],
    }

    right_obs = {
        "schema": "autogrammar.data2dsl/observation/v0",
        "observation_id": "obs:right:1",
        "query_id": query["query_id"],
        "side": "right",
        "subject": dict(query["subject"]),
        "metric": dict(query["metric"]),
        "window": dict(query["window"]),
        "state": "OBSERVED",
        "value": {"kind": value_kind, "value": right_val},
        "evidence": [
            {
                "evidence_id": "ev:right:1",
                "target_uri": "https://github.com/autogrammar/data2dsl",
                "source_uri": "https://github.com/autogrammar/data2dsl",
                "source_revision": "sha256:" + "b" * 64,
                "media_type": "application/json",
                "digest_sha256": "b" * 64,
                "extractor": {"id": "test", "version": "1.0.0"},
                "location": {"kind": "oql-telemetry-log", "path": "log.json", "start_line": 1, "end_line": 1},
            }
        ],
    }

    return query, left_obs, right_obs


def test_float_exact_match_passes_contract_validation():
    query, left_obs, right_obs = _create_bundle_fixture("float", "12.50", "12.5")
    comp = DeterministicComparator()
    bundle = comp.compare(query, left_obs, right_obs)
    assert bundle["result"]["outcome"] == "MATCH"
    assert bundle["result"]["delta"] is None
    validate_document(bundle)


def test_float_exact_conflict_passes_contract_validation():
    query, left_obs, right_obs = _create_bundle_fixture("float", "12.50", "14.25")
    comp = DeterministicComparator()
    bundle = comp.compare(query, left_obs, right_obs)
    assert bundle["result"]["outcome"] == "CONFLICT"
    assert bundle["result"]["delta"] == {"kind": "float", "value": "1.75"}
    validate_document(bundle)


def test_percentage_exact_match_passes_contract_validation():
    query, left_obs, right_obs = _create_bundle_fixture("percentage", "98.5%", "98.50%")
    comp = DeterministicComparator()
    bundle = comp.compare(query, left_obs, right_obs)
    assert bundle["result"]["outcome"] == "MATCH"
    assert bundle["result"]["delta"] is None
    validate_document(bundle)


def test_percentage_exact_conflict_passes_contract_validation():
    query, left_obs, right_obs = _create_bundle_fixture("percentage", "98.5%", "95.0%")
    comp = DeterministicComparator()
    bundle = comp.compare(query, left_obs, right_obs)
    assert bundle["result"]["outcome"] == "CONFLICT"
    assert bundle["result"]["delta"] == {"kind": "percentage", "value": "-3.5%"}
    validate_document(bundle)
