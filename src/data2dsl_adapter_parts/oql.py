"""Oql source adapters for data2dsl observation normalization."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence


from data2dsl_adapter_parts.common import (
    DEFAULT_OQL_EXTRACTOR,
    SCHEMA_OBSERVATION,
    compute_sha256,
    error_observation,
    evidence_entry,
    numeric_value,
    observation_envelope,
    set_value,
    temperature_value,
    unsupported_observation,
)

@dataclass(frozen=True)
class OqlScenarioSpecResponse:
    """Response structure representing declared specification from an OQL scenario."""

    status: str  # "OK", "UNAVAILABLE", "ERROR"
    scenario_id: str
    path: str
    start_line: int = 1
    end_line: int = 1
    sample_rate_hz: float | int | None = None
    max_temperature_celsius: float | None = None
    frequency_mhz: float | int | None = None
    packet_throughput: float | int | None = None
    active_pins: Sequence[str] = field(default_factory=tuple)
    buses: Sequence[str] = field(default_factory=tuple)
    source_revision: str | None = None
    error_message: str | None = None


@dataclass(frozen=True)
class OqlTelemetryLogResponse:
    """Response structure representing observed sensor/hardware telemetry logs."""

    status: str  # "OK", "UNAVAILABLE", "ERROR"
    log_id: str
    path: str
    start_line: int = 1
    end_line: int = 1
    avg_sample_rate_hz: float | int | None = None
    peak_temperature_celsius: float | None = None
    observed_frequency_mhz: float | int | None = None
    avg_packet_throughput: float | int | None = None
    active_pins: Sequence[str] = field(default_factory=tuple)
    active_buses: Sequence[str] = field(default_factory=tuple)
    timestamp_start: str | None = None
    timestamp_end: str | None = None
    source_revision: str | None = None
    error_message: str | None = None



# (id keywords, property keywords, raw key, converter name) — first match wins.
_METRIC_RULES = (
    (("sample_rate",), ("sample_rate",), "sample_rate", "num-int"),
    (("temperature", "thermal"), ("celsius",), "temperature", "temp"),
    (("frequency",), ("frequency_mhz",), "frequency", "num-int"),
    (("throughput",), ("packet_throughput",), "throughput", "num-float"),
    (("pin", "gpio"), ("pins",), "pins", "set"),
    (("bus",), ("buses",), "buses", "set"),
)

_METRIC_CONVERTERS = {
    "num-int": lambda raw_val, val_kind: numeric_value(raw_val, val_kind, "integer"),
    "num-float": lambda raw_val, val_kind: numeric_value(raw_val, val_kind, "float"),
    "temp": temperature_value,
    "set": set_value,
}


def _metric_value(metric: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any] | None:
    val_kind = metric.get("value_kind", "float")
    metric_id = (metric.get("id") or metric.get("name") or "").lower()
    metric_prop = metric.get("property", "").lower()
    for id_keys, prop_keys, raw_key, conv in _METRIC_RULES:
        if any(k in metric_id for k in id_keys) or any(k in metric_prop for k in prop_keys):
            return _METRIC_CONVERTERS[conv](raw.get(raw_key), val_kind)
    return None


class _OqlNormalizer:
    """Shared normalization flow for OQL spec and telemetry responses."""

    def __init__(
        self,
        extractor: dict[str, str],
        prefix: str,
        location_kind: str,
        default_target: str,
        raw_getter,
        record_id_getter,
    ) -> None:
        self._extractor = extractor
        self._prefix = prefix
        self._location_kind = location_kind
        self._default_target = default_target
        self._raw_getter = raw_getter
        self._record_id_getter = record_id_getter

    def normalize(
        self,
        query: dict[str, Any],
        response: Any,
        side: str,
        observation_id: str | None,
    ) -> dict[str, Any]:
        target_uri = query["subject"].get("repository", self._default_target)
        if response.status != "OK" or response.error_message:
            return error_observation(
                query, prefix=self._prefix, side=side,
                observation_id=observation_id, target_uri=target_uri,
                path=response.path, status=response.status,
                error_message=response.error_message, extractor=self._extractor,
                location_kind=self._location_kind,
            )
        val_obj = _metric_value(query["metric"], self._raw_getter(response))
        if val_obj is None:
            return unsupported_observation(
                query, prefix=self._prefix, side=side,
                observation_id=observation_id, target_uri=target_uri,
                path=response.path, source_revision=response.source_revision,
                extractor=self._extractor, location_kind=self._location_kind,
            )
        return self._observed(query, response, val_obj, side, observation_id, target_uri)

    def _observed(self, query, response, val_obj, side, observation_id, target_uri):
        val_repr = (
            ",".join(sorted(str(i) for i in val_obj["items"]))
            if val_obj.get("kind") == "string-set"
            else str(val_obj.get("value", ""))
        )
        record_id = self._record_id_getter(response)
        digest = compute_sha256(f"{record_id}:{response.path}:{val_repr}")
        src_rev = response.source_revision or f"sha256:{digest}"
        obs_id = observation_id or f"observation:{self._prefix}:{digest[:8]}"
        evidence = [
            evidence_entry(
                evidence_id=f"evidence:{self._prefix}:{record_id}:{digest[:8]}",
                target_uri=target_uri, path=response.path,
                source_revision=src_rev, digest=digest,
                extractor=self._extractor, location_kind=self._location_kind,
                start_line=response.start_line, end_line=response.end_line,
            )
        ]
        return observation_envelope(query, obs_id, side, "OBSERVED", val_obj, evidence)


def _spec_raw(response: OqlScenarioSpecResponse) -> dict[str, Any]:
    return {
        "sample_rate": response.sample_rate_hz,
        "temperature": response.max_temperature_celsius,
        "frequency": response.frequency_mhz,
        "throughput": response.packet_throughput,
        "pins": response.active_pins,
        "buses": response.buses,
    }


def _telemetry_raw(response: OqlTelemetryLogResponse) -> dict[str, Any]:
    return {
        "sample_rate": response.avg_sample_rate_hz,
        "temperature": response.peak_temperature_celsius,
        "frequency": response.observed_frequency_mhz,
        "throughput": response.avg_packet_throughput,
        "pins": response.active_pins,
        "buses": getattr(response, "active_buses", getattr(response, "buses", ())),
    }


class OqlTelemetryAdapter:
    """Adapter for converting OQL scenario specs and telemetry logs into data2dsl observations."""

    def __init__(self, extractor: dict[str, str] | None = None) -> None:
        self._extractor = extractor or DEFAULT_OQL_EXTRACTOR

    def normalize(
        self,
        query: dict[str, Any],
        response: OqlScenarioSpecResponse | OqlTelemetryLogResponse,
        side: str = "left",
        observation_id: str | None = None,
    ) -> dict[str, Any]:
        """Normalize an OQL spec or telemetry response into a data2dsl observation envelope."""
        if isinstance(response, OqlScenarioSpecResponse):
            return self.normalize_spec(query, response, side=side, observation_id=observation_id)
        elif isinstance(response, OqlTelemetryLogResponse):
            return self.normalize_telemetry(query, response, side=side, observation_id=observation_id)
        raise ValueError(f"Unsupported response type for OqlTelemetryAdapter: {type(response)}")

    def normalize_spec(
        self,
        query: dict[str, Any],
        response: OqlScenarioSpecResponse,
        side: str = "left",
        observation_id: str | None = None,
    ) -> dict[str, Any]:
        """Normalize an OQL scenario specification into a data2dsl observation."""
        normalizer = _OqlNormalizer(
            self._extractor, "oql_spec", "oql-scenario",
            "file://local/oql-scenarios", _spec_raw, lambda r: r.scenario_id,
        )
        return normalizer.normalize(query, response, side, observation_id)

    def normalize_telemetry(
        self,
        query: dict[str, Any],
        response: OqlTelemetryLogResponse,
        side: str = "right",
        observation_id: str | None = None,
    ) -> dict[str, Any]:
        """Normalize an OQL sensor/hardware telemetry log into a data2dsl observation."""
        normalizer = _OqlNormalizer(
            self._extractor, "oql_telemetry", "oql-telemetry-log",
            "file://local/oql-telemetry", _telemetry_raw, lambda r: r.log_id,
        )
        return normalizer.normalize(query, response, side, observation_id)
