"""Oql source adapters for data2dsl observation normalization."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence


from data2dsl_adapter_parts.common import DEFAULT_OQL_EXTRACTOR, SCHEMA_OBSERVATION, compute_sha256

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
        query_id = query["query_id"]
        subject = query["subject"]
        metric = query["metric"]
        window = query["window"]
        target_uri = subject.get("repository", "file://local/oql-scenarios")

        if response.status != "OK" or response.error_message:
            obs_id = observation_id or f"observation:oql_spec:unevaluable:{side}"
            err_text = response.error_message or f"error:{response.status}"
            err_digest = compute_sha256(err_text)
            return {
                "schema": SCHEMA_OBSERVATION,
                "observation_id": obs_id,
                "query_id": query_id,
                "side": side,
                "subject": subject,
                "metric": metric,
                "window": window,
                "state": "UNEVALUABLE",
                "value": None,
                "evidence": [
                    {
                        "evidence_id": f"evidence:oql_spec:error:{side}",
                        "target_uri": target_uri,
                        "source_uri": f"{target_uri}/{response.path}",
                        "source_revision": f"sha256:{err_digest}",
                        "media_type": "application/json",
                        "digest_sha256": err_digest,
                        "extractor": self._extractor,
                        "location": {
                            "kind": "oql-scenario",
                            "path": response.path,
                            "start_line": 1,
                            "end_line": 1,
                        },
                    }
                ],
            }

        val_kind = metric.get("value_kind", "float")
        metric_id = (metric.get("id") or metric.get("name") or "").lower()
        metric_prop = metric.get("property", "").lower()

        val_obj: dict[str, Any] | None
        if "sample_rate" in metric_id or "sample_rate" in metric_prop:
            raw_val = response.sample_rate_hz
            if raw_val is None:
                val_obj = None
            elif val_kind == "integer":
                val_obj = {"kind": "integer", "value": str(int(raw_val))}
            else:
                val_obj = {"kind": "float", "value": f"{float(raw_val):.2f}"}
        elif "temperature" in metric_id or "thermal" in metric_id or "celsius" in metric_prop:
            raw_val = response.max_temperature_celsius
            if raw_val is None:
                val_obj = None
            elif val_kind == "percentage":
                val_obj = {"kind": "percentage", "value": f"{float(raw_val):.2f}%"}
            else:
                val_obj = {"kind": "float", "value": f"{float(raw_val):.2f}"}
        elif "frequency" in metric_id or "frequency_mhz" in metric_prop:
            raw_val = response.frequency_mhz
            if raw_val is None:
                val_obj = None
            elif val_kind == "integer":
                val_obj = {"kind": "integer", "value": str(int(raw_val))}
            else:
                val_obj = {"kind": "float", "value": f"{float(raw_val):.2f}"}
        elif "throughput" in metric_id or "packet_throughput" in metric_prop:
            raw_val = response.packet_throughput
            if raw_val is None:
                val_obj = None
            elif val_kind == "float":
                val_obj = {"kind": "float", "value": f"{float(raw_val):.2f}"}
            else:
                val_obj = {"kind": "integer", "value": str(int(raw_val))}
        elif "pin" in metric_id or "gpio" in metric_id or "pins" in metric_prop:
            pins_sorted = sorted(list(response.active_pins))
            if val_kind == "integer":
                val_obj = {"kind": "integer", "value": str(len(pins_sorted))}
            else:
                val_obj = {"kind": "string-set", "items": pins_sorted}
        elif "bus" in metric_id or "buses" in metric_prop:
            buses_sorted = sorted(list(response.buses))
            if val_kind == "integer":
                val_obj = {"kind": "integer", "value": str(len(buses_sorted))}
            else:
                val_obj = {"kind": "string-set", "items": buses_sorted}
        else:
            val_obj = None

        if val_obj is None:
            obs_id = observation_id or f"observation:oql_spec:unevaluable:{side}"
            return {
                "schema": SCHEMA_OBSERVATION,
                "observation_id": obs_id,
                "query_id": query_id,
                "side": side,
                "subject": subject,
                "metric": metric,
                "window": window,
                "state": "UNEVALUABLE",
                "value": None,
                "evidence": [
                    {
                        "evidence_id": f"evidence:oql_spec:unsupported:{side}",
                        "target_uri": target_uri,
                        "source_uri": f"{target_uri}/{response.path}",
                        "source_revision": response.source_revision or f"sha256:{compute_sha256(response.path)}",
                        "media_type": "application/json",
                        "digest_sha256": compute_sha256(response.path),
                        "extractor": self._extractor,
                        "location": {
                            "kind": "oql-scenario",
                            "path": response.path,
                            "start_line": 1,
                            "end_line": 1,
                        },
                    }
                ],
            }

        val_repr = ",".join(sorted(str(i) for i in val_obj["items"])) if val_obj.get("kind") == "string-set" else str(val_obj.get("value", ""))
        digest = compute_sha256(f"{response.scenario_id}:{response.path}:{val_repr}")
        src_rev = response.source_revision or f"sha256:{digest}"
        obs_id = observation_id or f"observation:oql_spec:{digest[:8]}"

        evidence_list = [
            {
                "evidence_id": f"evidence:oql_spec:{response.scenario_id}:{digest[:8]}",
                "target_uri": target_uri,
                "source_uri": f"{target_uri}/{response.path}",
                "source_revision": src_rev,
                "media_type": "application/json",
                "digest_sha256": digest,
                "extractor": self._extractor,
                "location": {
                    "kind": "oql-scenario",
                    "path": response.path,
                    "start_line": response.start_line,
                    "end_line": response.end_line,
                },
            }
        ]

        return {
            "schema": SCHEMA_OBSERVATION,
            "observation_id": obs_id,
            "query_id": query_id,
            "side": side,
            "subject": subject,
            "metric": metric,
            "window": window,
            "state": "OBSERVED",
            "value": val_obj,
            "evidence": evidence_list,
        }

    def normalize_telemetry(
        self,
        query: dict[str, Any],
        response: OqlTelemetryLogResponse,
        side: str = "right",
        observation_id: str | None = None,
    ) -> dict[str, Any]:
        """Normalize an OQL sensor/hardware telemetry log into a data2dsl observation."""
        query_id = query["query_id"]
        subject = query["subject"]
        metric = query["metric"]
        window = query["window"]
        target_uri = subject.get("repository", "file://local/oql-telemetry")

        if response.status != "OK" or response.error_message:
            obs_id = observation_id or f"observation:oql_telemetry:unevaluable:{side}"
            err_text = response.error_message or f"error:{response.status}"
            err_digest = compute_sha256(err_text)
            return {
                "schema": SCHEMA_OBSERVATION,
                "observation_id": obs_id,
                "query_id": query_id,
                "side": side,
                "subject": subject,
                "metric": metric,
                "window": window,
                "state": "UNEVALUABLE",
                "value": None,
                "evidence": [
                    {
                        "evidence_id": f"evidence:oql_telemetry:error:{side}",
                        "target_uri": target_uri,
                        "source_uri": f"{target_uri}/{response.path}",
                        "source_revision": f"sha256:{err_digest}",
                        "media_type": "application/json",
                        "digest_sha256": err_digest,
                        "extractor": self._extractor,
                        "location": {
                            "kind": "oql-telemetry-log",
                            "path": response.path,
                            "start_line": 1,
                            "end_line": 1,
                        },
                    }
                ],
            }

        val_kind = metric.get("value_kind", "float")
        metric_id = (metric.get("id") or metric.get("name") or "").lower()
        metric_prop = metric.get("property", "").lower()

        val_obj: dict[str, Any] | None
        if "sample_rate" in metric_id or "sample_rate" in metric_prop:
            raw_val = response.avg_sample_rate_hz
            if raw_val is None:
                val_obj = None
            elif val_kind == "integer":
                val_obj = {"kind": "integer", "value": str(int(raw_val))}
            else:
                val_obj = {"kind": "float", "value": f"{float(raw_val):.2f}"}
        elif "temperature" in metric_id or "thermal" in metric_id or "celsius" in metric_prop:
            raw_val = response.peak_temperature_celsius
            if raw_val is None:
                val_obj = None
            elif val_kind == "percentage":
                val_obj = {"kind": "percentage", "value": f"{float(raw_val):.2f}%"}
            else:
                val_obj = {"kind": "float", "value": f"{float(raw_val):.2f}"}
        elif "frequency" in metric_id or "frequency_mhz" in metric_prop:
            raw_val = response.observed_frequency_mhz
            if raw_val is None:
                val_obj = None
            elif val_kind == "integer":
                val_obj = {"kind": "integer", "value": str(int(raw_val))}
            else:
                val_obj = {"kind": "float", "value": f"{float(raw_val):.2f}"}
        elif "throughput" in metric_id or "packet_throughput" in metric_prop:
            raw_val = response.avg_packet_throughput
            if raw_val is None:
                val_obj = None
            elif val_kind == "float":
                val_obj = {"kind": "float", "value": f"{float(raw_val):.2f}"}
            else:
                val_obj = {"kind": "integer", "value": str(int(raw_val))}
        elif "pin" in metric_id or "gpio" in metric_id or "pins" in metric_prop:
            pins_sorted = sorted(list(response.active_pins))
            if val_kind == "integer":
                val_obj = {"kind": "integer", "value": str(len(pins_sorted))}
            else:
                val_obj = {"kind": "string-set", "items": pins_sorted}
        elif "bus" in metric_id or "buses" in metric_prop:
            buses_sorted = sorted(list(getattr(response, "active_buses", getattr(response, "buses", ()))))
            if val_kind == "integer":
                val_obj = {"kind": "integer", "value": str(len(buses_sorted))}
            else:
                val_obj = {"kind": "string-set", "items": buses_sorted}
        else:
            val_obj = None

        if val_obj is None:
            obs_id = observation_id or f"observation:oql_telemetry:unevaluable:{side}"
            return {
                "schema": SCHEMA_OBSERVATION,
                "observation_id": obs_id,
                "query_id": query_id,
                "side": side,
                "subject": subject,
                "metric": metric,
                "window": window,
                "state": "UNEVALUABLE",
                "value": None,
                "evidence": [
                    {
                        "evidence_id": f"evidence:oql_telemetry:unsupported:{side}",
                        "target_uri": target_uri,
                        "source_uri": f"{target_uri}/{response.path}",
                        "source_revision": response.source_revision or f"sha256:{compute_sha256(response.path)}",
                        "media_type": "application/json",
                        "digest_sha256": compute_sha256(response.path),
                        "extractor": self._extractor,
                        "location": {
                            "kind": "oql-telemetry-log",
                            "path": response.path,
                            "start_line": 1,
                            "end_line": 1,
                        },
                    }
                ],
            }

        val_repr = ",".join(sorted(str(i) for i in val_obj["items"])) if val_obj.get("kind") == "string-set" else str(val_obj.get("value", ""))
        digest = compute_sha256(f"{response.log_id}:{response.path}:{val_repr}")
        src_rev = response.source_revision or f"sha256:{digest}"
        obs_id = observation_id or f"observation:oql_telemetry:{digest[:8]}"

        evidence_list = [
            {
                "evidence_id": f"evidence:oql_telemetry:{response.log_id}:{digest[:8]}",
                "target_uri": target_uri,
                "source_uri": f"{target_uri}/{response.path}",
                "source_revision": src_rev,
                "media_type": "application/json",
                "digest_sha256": digest,
                "extractor": self._extractor,
                "location": {
                    "kind": "oql-telemetry-log",
                    "path": response.path,
                    "start_line": response.start_line,
                    "end_line": response.end_line,
                },
            }
        ]

        return {
            "schema": SCHEMA_OBSERVATION,
            "observation_id": obs_id,
            "query_id": query_id,
            "side": side,
            "subject": subject,
            "metric": metric,
            "window": window,
            "state": "OBSERVED",
            "value": val_obj,
            "evidence": evidence_list,
        }


# ---------------------------------------------------------------------------
# SUMD (Structured Unified Markdown Document) Adapter
# ---------------------------------------------------------------------------


