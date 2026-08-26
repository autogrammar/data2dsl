"""Unit tests for OqlTelemetryAdapter (oqlos integration)."""

from typing import Any
import pytest

from data2dsl_adapters import (
    OqlScenarioSpecResponse,
    OqlTelemetryLogResponse,
    OqlTelemetryAdapter,
    SCHEMA_OBSERVATION,
)
from data2dsl_comparator import DeterministicComparator


@pytest.fixture
def base_query() -> dict[str, Any]:
    return {
        "query_id": "query:oql:test",
        "subject": {"repository": "https://github.com/oqlos/sensor-scenarios", "device": "sensor-node-01"},
        "metric": {"name": "device.sensor.sample_rate", "property": "sample_rate", "value_kind": "float"},
        "window": {"start": "2026-08-20T00:00:00Z", "end": "2026-08-26T00:00:00Z"},
    }


def test_oql_spec_sample_rate_float(base_query: dict[str, Any]) -> None:
    adapter = OqlTelemetryAdapter()
    spec = OqlScenarioSpecResponse(
        status="OK",
        scenario_id="scenario-sample-rate-01",
        path="scenarios/imu_capture.oql.json",
        sample_rate_hz=100.0,
    )
    obs = adapter.normalize(base_query, spec, side="left")
    assert obs["schema"] == SCHEMA_OBSERVATION
    assert obs["state"] == "OBSERVED"
    assert obs["side"] == "left"
    assert obs["value"] == {"kind": "float", "value": "100.00"}
    assert len(obs["evidence"]) == 1
    assert obs["evidence"][0]["extractor"]["id"] == "oqlos.telemetry"


def test_oql_telemetry_sample_rate_float(base_query: dict[str, Any]) -> None:
    adapter = OqlTelemetryAdapter()
    telem = OqlTelemetryLogResponse(
        status="OK",
        log_id="telem-log-01",
        path="logs/imu_20260825.jsonl",
        avg_sample_rate_hz=99.85,
    )
    obs = adapter.normalize(base_query, telem, side="right")
    assert obs["schema"] == SCHEMA_OBSERVATION
    assert obs["state"] == "OBSERVED"
    assert obs["side"] == "right"
    assert obs["value"] == {"kind": "float", "value": "99.85"}
    assert len(obs["evidence"]) == 1


def test_oql_spec_temperature_and_telemetry_comparison() -> None:
    query = {
        "query_id": "query:oql:thermal",
        "subject": {"repository": "https://github.com/oqlos/thermal-tests", "device": "power-module"},
        "metric": {"name": "device.thermal.max_celsius", "property": "celsius", "value_kind": "float"},
        "window": {"start": "2026-08-20T00:00:00Z", "end": "2026-08-26T00:00:00Z"},
        "comparison": {"equality": "exact"},
    }
    adapter = OqlTelemetryAdapter()
    spec = OqlScenarioSpecResponse(
        status="OK",
        scenario_id="spec-thermal-01",
        path="scenarios/thermal.oql.json",
        max_temperature_celsius=75.0,
    )
    telem = OqlTelemetryLogResponse(
        status="OK",
        log_id="telem-thermal-01",
        path="logs/thermal.jsonl",
        peak_temperature_celsius=82.5,
    )
    left_obs = adapter.normalize(query, spec, side="left")
    right_obs = adapter.normalize(query, telem, side="right")

    assert left_obs["value"] == {"kind": "float", "value": "75.00"}
    assert right_obs["value"] == {"kind": "float", "value": "82.50"}

    comparator = DeterministicComparator()
    bundle = comparator.compare(query, left_obs, right_obs)
    result = bundle["result"]
    assert result["outcome"] == "CONFLICT"
    assert result["delta"] == {"kind": "float", "value": "7.5"}


def test_oql_gpio_pins_string_set() -> None:
    query = {
        "query_id": "query:oql:gpio",
        "subject": {"repository": "https://github.com/oqlos/pinout", "device": "stm32-core"},
        "metric": {"name": "device.gpio.active_pins", "property": "pins", "value_kind": "string-set"},
        "window": {"start": "2026-08-20T00:00:00Z", "end": "2026-08-26T00:00:00Z"},
        "comparison": {"equality": "exact-set"},
    }
    adapter = OqlTelemetryAdapter()
    spec = OqlScenarioSpecResponse(
        status="OK",
        scenario_id="spec-pins-01",
        path="scenarios/pinout.oql.json",
        active_pins=["PA0", "PA1", "PB4"],
    )
    telem = OqlTelemetryLogResponse(
        status="OK",
        log_id="telem-pins-01",
        path="logs/pins.jsonl",
        active_pins=["PA0", "PA1", "PB4"],
    )
    left_obs = adapter.normalize(query, spec, side="left")
    right_obs = adapter.normalize(query, telem, side="right")

    assert left_obs["value"] == {"kind": "string-set", "items": ["PA0", "PA1", "PB4"]}
    assert right_obs["value"] == {"kind": "string-set", "items": ["PA0", "PA1", "PB4"]}

    comparator = DeterministicComparator()
    bundle = comparator.compare(query, left_obs, right_obs)
    result = bundle["result"]
    assert result["outcome"] == "MATCH"


def test_oql_unevaluable_handling(base_query: dict[str, Any]) -> None:
    adapter = OqlTelemetryAdapter()
    error_spec = OqlScenarioSpecResponse(
        status="ERROR",
        scenario_id="invalid-spec",
        path="scenarios/missing.oql.json",
        error_message="Scenario file not found",
    )
    obs = adapter.normalize(base_query, error_spec, side="left")
    assert obs["state"] == "UNEVALUABLE"
    assert obs["value"] is None
    assert len(obs["evidence"]) == 1
    assert "error" in obs["evidence"][0]["evidence_id"]


def test_oql_unsupported_type_raises(base_query: dict[str, Any]) -> None:
    adapter = OqlTelemetryAdapter()
    with pytest.raises(ValueError, match="Unsupported response type"):
        adapter.normalize(base_query, {"invalid": "object"})  # type: ignore
