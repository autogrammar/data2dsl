# 02-oql-telemetry-verification

Demonstrates Hardware-in-the-Loop (HIL) verification comparing declared scenario bounds against measured sensor telemetry logs.

## Fixtures

- `query.json`: Query asserting maximum allowable device temperature (`device.thermal.max_celsius`, `float`).
- `scenario-spec.json`: Declared scenario envelope (`max_temperature_celsius`: 75.0°C).
- `telemetry-log.json`: Observed sensor telemetry log (`peak_temperature_celsius`: 82.5°C).
- `expected-bundle.json`: Expected comparison bundle yielding `CONFLICT` with delta `7.5°C`.

## Running the comparison via Python API

```python
from data2dsl_adapters import OqlTelemetryAdapter, OqlScenarioSpecResponse, OqlTelemetryLogResponse
from data2dsl_comparator import DeterministicComparator

adapter = OqlTelemetryAdapter()
obs_left = adapter.normalize_spec(query, OqlScenarioSpecResponse(status="OK", max_temperature_celsius=75.0))
obs_right = adapter.normalize_telemetry(query, OqlTelemetryLogResponse(status="OK", peak_temperature_celsius=82.5))

bundle = DeterministicComparator().compare(query, obs_left, obs_right)
assert bundle["result"]["outcome"] == "CONFLICT"
assert bundle["result"]["delta"]["value"] == "7.5"
```
