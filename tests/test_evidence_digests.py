"""Tests verifying cryptographic distinction of evidence digests across adapters (F06)."""

from data2dsl_adapters import (
    OqlTelemetryAdapter,
    OqlScenarioSpecResponse,
    OqlTelemetryLogResponse,
    DetaAdapter,
    DetaTopologyResponse,
    IntentContractAdapter,
    IntentContractResponse,
)


def _base_query(metric_id: str, value_kind: str, equality: str):
    return {
        "schema": "autogrammar.data2dsl/query/v0",
        "query_id": "query:test:digest",
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
        "left_source": {"id": "source:a", "kind": "oql"},
        "right_source": {"id": "source:b", "kind": "oql"},
        "comparison": {
            "equality": equality,
            "delta_direction": "right-minus-left",
            "missing_is_zero": False,
        },
    }


def test_oql_spec_pins_digest_uniqueness():
    """F06: Changing active_pins in OQL spec must yield different evidence digests."""
    adapter = OqlTelemetryAdapter()
    query = _base_query("oql.pins", "string-set", "string-set-exact")

    spec_a = OqlScenarioSpecResponse(status="OK", scenario_id="scen-1", path="spec.json", active_pins=("PA1", "PA2"))
    spec_b = OqlScenarioSpecResponse(status="OK", scenario_id="scen-1", path="spec.json", active_pins=("PB1", "PB2"))

    obs_a = adapter.normalize_spec(query, spec_a, side="left")
    obs_b = adapter.normalize_spec(query, spec_b, side="left")

    digest_a = obs_a["evidence"][0]["digest_sha256"]
    digest_b = obs_b["evidence"][0]["digest_sha256"]
    assert digest_a != digest_b, "Different active pins must produce different SHA-256 digests"


def test_oql_telemetry_pins_digest_uniqueness():
    """F06: Changing active_pins in OQL telemetry log must yield different evidence digests."""
    adapter = OqlTelemetryAdapter()
    query = _base_query("oql.pins", "string-set", "string-set-exact")

    log_a = OqlTelemetryLogResponse(status="OK", log_id="log-1", path="telemetry.log", active_pins=("PA1",))
    log_b = OqlTelemetryLogResponse(status="OK", log_id="log-1", path="telemetry.log", active_pins=("PB1",))

    obs_a = adapter.normalize_telemetry(query, log_a, side="right")
    obs_b = adapter.normalize_telemetry(query, log_b, side="right")

    digest_a = obs_a["evidence"][0]["digest_sha256"]
    digest_b = obs_b["evidence"][0]["digest_sha256"]
    assert digest_a != digest_b, "Different telemetry pins must produce different SHA-256 digests"


def test_deta_empty_services_digest_uniqueness():
    """F06: Deta topology without services with different ports or counts must produce different digests."""
    adapter = DetaAdapter()
    query = _base_query("infra.ports", "string-set", "string-set-exact")
    query["left_source"]["kind"] = "deta"
    query["right_source"]["kind"] = "deta"

    topo_a = DetaTopologyResponse(status="OK", manifest_path="compose.yml", service_count=2, ports=["80", "443"])
    topo_b = DetaTopologyResponse(status="OK", manifest_path="compose.yml", service_count=3, ports=["80", "8080"])

    obs_a = adapter.normalize(query, topo_a, side="left")
    obs_b = adapter.normalize(query, topo_b, side="left")

    digest_a = obs_a["evidence"][0]["digest_sha256"]
    digest_b = obs_b["evidence"][0]["digest_sha256"]
    assert digest_a != digest_b, "Different Deta ports/counts must produce different SHA-256 digests"


def test_intent_contract_digest_uniqueness():
    """F06: Intent contract changes in parties, obligations, or deliverables must produce different digests."""
    adapter = IntentContractAdapter()
    query = _base_query("intent.parties", "string-set", "string-set-exact")
    query["left_source"]["kind"] = "intent_contract"
    query["right_source"]["kind"] = "intent_contract"

    c_a = IntentContractResponse(status="OK", contract_id="c-1", parties=["alice"], deliverables=["rep.pdf"])
    c_b = IntentContractResponse(status="OK", contract_id="c-1", parties=["bob"], deliverables=["rep.pdf"])

    obs_a = adapter.normalize(query, c_a, side="left")
    obs_b = adapter.normalize(query, c_b, side="left")

    digest_a = obs_a["evidence"][0]["digest_sha256"]
    digest_b = obs_b["evidence"][0]["digest_sha256"]
    assert digest_a != digest_b, "Different contract parties must produce different SHA-256 digests"
