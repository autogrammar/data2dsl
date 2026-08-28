"""Tests verifying fixes for F04 (markdown actor claim parsing) and F05 (metric.id mapping across adapters)."""

from data2dsl_adapters import (
    WorkSummaryMarkdownAdapter,
    DetaAdapter,
    DetaTopologyResponse,
    DetaServiceEvidence,
    IntentContractAdapter,
    IntentContractResponse,
    OqlTelemetryAdapter,
    OqlScenarioSpecResponse,
    OqlTelemetryLogResponse,
)


def test_markdown_actor_isolation():
    """F04: In a document with multiple actors, asking for Alice must not return Bob's count."""
    doc = "Bob: 99 commits\nAlice: 12 commits\nCharlie: 5 commits\n"
    adapter = WorkSummaryMarkdownAdapter()
    query_alice = {
        "schema": "autogrammar.data2dsl/query/v0",
        "query_id": "query:alice:commits",
        "subject": {
            "repository": "https://github.com/autogrammar/data2dsl",
            "actor": "alice",
        },
        "metric": {
            "id": "git.commit.count",
            "version": "v1",
            "value_kind": "integer",
            "unit": "commits",
        },
        "window": {
            "start": "2026-08-01T00:00:00Z",
            "end": "2026-08-27T00:00:00Z",
            "semantics": "half-open-utc",
        },
        "left_source": {"id": "source:markdown", "kind": "markdown"},
        "right_source": {"id": "source:github", "kind": "github"},
        "comparison": {
            "equality": "integer-exact",
            "delta_direction": "right-minus-left",
            "missing_is_zero": False,
        },
    }

    claim = adapter.extract_commit_claim(doc, actor="github:alice")
    assert claim is not None
    obs = adapter.normalize(query_alice, claim, side="left")
    assert obs["state"] == "OBSERVED"
    assert obs["value"]["value"] == "12", f"Expected Alice's 12 commits, got {obs['value']['value']}"
    assert obs["evidence"][0]["location"]["start_line"] == 2


def test_deta_metric_id_mapping():
    """F05: DetaAdapter must use metric.id to distinguish ports from services."""
    adapter = DetaAdapter()
    response = DetaTopologyResponse(
        status="OK",
        manifest_path="docker-compose.yml",
        services=(DetaServiceEvidence("web", "http", 8080, "docker-compose.yml"),),
        ports=(8080, 443),
    )

    query_ports = {
        "schema": "autogrammar.data2dsl/query/v0",
        "query_id": "query:deta:ports",
        "subject": {"repository": "https://github.com/autogrammar/data2dsl", "actor": "antigravity"},
        "metric": {"id": "deta.active_ports", "version": "v1", "value_kind": "string-set", "unit": "ports"},
        "window": {"start": "2026-08-01T00:00:00Z", "end": "2026-08-27T00:00:00Z", "semantics": "half-open-utc"},
        "left_source": {"id": "source:deta", "kind": "deta"},
        "right_source": {"id": "source:deta", "kind": "deta"},
        "comparison": {"equality": "string-set-exact", "delta_direction": "right-minus-left", "missing_is_zero": False},
    }

    obs_ports = adapter.normalize(query_ports, response, side="left")
    assert obs_ports["state"] == "OBSERVED"
    assert obs_ports["value"]["kind"] == "string-set"
    assert len(obs_ports["value"]["items"]) == 2


def test_intent_contract_metric_id_mapping():
    """F05: IntentContractAdapter must map canonical metric.id correctly."""
    adapter = IntentContractAdapter()
    response = IntentContractResponse(
        status="OK",
        contract_id="contract-123",
        path="intent.json",
        parties=["alice", "bob"],
        obligations=["deliver_report"],
        deliverables=["report.pdf", "code.zip"],
    )

    query_parties = {
        "schema": "autogrammar.data2dsl/query/v0",
        "query_id": "query:intent:parties",
        "subject": {"repository": "https://github.com/autogrammar/data2dsl", "actor": "antigravity"},
        "metric": {"id": "intent.contract.parties", "version": "v1", "value_kind": "string-set", "unit": "parties"},
        "window": {"start": "2026-08-01T00:00:00Z", "end": "2026-08-27T00:00:00Z", "semantics": "half-open-utc"},
        "left_source": {"id": "source:intent_contract", "kind": "intent_contract"},
        "right_source": {"id": "source:intent_contract", "kind": "intent_contract"},
        "comparison": {"equality": "string-set-exact", "delta_direction": "right-minus-left", "missing_is_zero": False},
    }

    obs = adapter.normalize(query_parties, response, side="left")
    assert obs["state"] == "OBSERVED"
    assert obs["value"]["items"] == ["alice", "bob"]


def test_oql_telemetry_no_false_zero_mapping():
    """F05: OQL adapter must map sample_rate from canonical metric.id and not return 0.0 for actual values."""
    adapter = OqlTelemetryAdapter()

    spec_resp = OqlScenarioSpecResponse(
        status="OK",
        scenario_id="scenario-hil",
        path="hil-scenario.json",
        sample_rate_hz=100.0,
        max_temperature_celsius=45.0,
        frequency_mhz=16.0,
        packet_throughput=500,
        active_pins=("PA1", "PA2"),
        buses=("SPI1",),
    )

    log_resp = OqlTelemetryLogResponse(
        status="OK",
        log_id="log-run-1",
        path="telemetry.log",
        avg_sample_rate_hz=42.0,
        peak_temperature_celsius=52.0,
        observed_frequency_mhz=16.0,
        avg_packet_throughput=480,
        active_pins=("PA1", "PA2"),
        active_buses=("SPI1",),
    )

    query = {
        "schema": "autogrammar.data2dsl/query/v0",
        "query_id": "query:oql:sample_rate",
        "subject": {"repository": "https://github.com/autogrammar/data2dsl", "actor": "antigravity"},
        "metric": {"id": "oql.sample_rate", "version": "v1", "value_kind": "float", "unit": "hz"},
        "window": {"start": "2026-08-01T00:00:00Z", "end": "2026-08-27T00:00:00Z", "semantics": "half-open-utc"},
        "left_source": {"id": "source:oql", "kind": "oql"},
        "right_source": {"id": "source:oql", "kind": "oql"},
        "comparison": {"equality": "float-exact", "delta_direction": "right-minus-left", "missing_is_zero": False},
    }

    obs_left = adapter.normalize_spec(query, spec_resp, side="left")
    obs_right = adapter.normalize_telemetry(query, log_resp, side="right")

    assert obs_left["state"] == "OBSERVED"
    assert obs_left["value"]["value"] == "100.00", f"Expected 100.00, got {obs_left['value']['value']}"

    assert obs_right["state"] == "OBSERVED"
    assert obs_right["value"]["value"] == "42.00", f"Expected 42.00, got {obs_right['value']['value']}"


def test_oql_unknown_metric_returns_unevaluable():
    """F05: Unknown metric must return UNEVALUABLE, not fallback 0.0."""
    adapter = OqlTelemetryAdapter()
    spec_resp = OqlScenarioSpecResponse(
        status="OK",
        scenario_id="scenario-hil",
        path="hil-scenario.json",
        sample_rate_hz=100.0,
    )
    query_unknown = {
        "schema": "autogrammar.data2dsl/query/v0",
        "query_id": "query:oql:unknown",
        "subject": {"repository": "https://github.com/autogrammar/data2dsl", "actor": "antigravity"},
        "metric": {"id": "oql.nonexistent_metric", "version": "v1", "value_kind": "float", "unit": "units"},
        "window": {"start": "2026-08-01T00:00:00Z", "end": "2026-08-27T00:00:00Z", "semantics": "half-open-utc"},
        "left_source": {"id": "source:oql", "kind": "oql"},
        "right_source": {"id": "source:oql", "kind": "oql"},
        "comparison": {"equality": "float-exact", "delta_direction": "right-minus-left", "missing_is_zero": False},
    }

    obs = adapter.normalize_spec(query_unknown, spec_resp, side="left")
    assert obs["state"] == "UNEVALUABLE"
    assert obs["value"] is None
