# Research: `oqlos/*` Scenario Outcomes and Sensor Telemetry Adapter

- **Date:** 2026-08-24
- **Related:** ADR-004, ticket-041
- **Status:** Research Note

## 1. Background

The `oqlos/*` ecosystem manages embedded hardware scenarios, device configurations, and real-time telemetry streams. A critical requirement in hardware-in-the-loop (HIL) verification is comparing **declared hardware specifications** (e.g. expected operating frequency, temperature ceiling, packet throughput) against **observed telemetry data**.

## 2. Proposed `OqlTelemetryAdapter` Architecture

An adapter conforming to `data2dsl_adapters.py` can normalize OQL scenario runs:

```
[OQL Scenario Spec / Manifest]  ──┐
                                  ├──► data2dsl ──► [Telemetry Verification Bundle]
[Observed Sensor Telemetry Log] ──┘
```

### Observation Normalization:
- **Left Observation (Specification)**:
  - Metric: `device.sensor.sample_rate`, `device.thermal.max_celsius`, `device.gpio.active_pins`
  - Value: Float, integer, or string-set bounds.
  - Evidence: Pointer to `.oql` scenario file and line numbers.
- **Right Observation (Telemetry)**:
  - Extracted average / p99 / set of observed values from recorded log.
  - Evidence: Timestamped binary/JSON log digest SHA-256.

## 3. Supported Comparisons

- **Threshold Compliance (`float`/`percentage`)**: Deterministic check whether telemetry exceeds allowable spec ranges.
- **Pin / Bus State Alignment (`string-set`)**: Verify that active I2C/SPI pins match declared device pinouts.

## 4. Conclusion

The existing `DeterministicComparator` in `data2dsl` with `float`, `percentage`, and `string-set` support already possesses all required comparison primitives. Only a thin `OqlTelemetryAdapter` is needed when `oqlos` integration is formally prioritized.
