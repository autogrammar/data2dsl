# ADR-006: OQL Telemetry Source and Hardware-in-the-Loop Normalization

- **Status:** Accepted
- **Date:** 2026-08-26
- **Decision owner:** `data2dsl` ticket-049
- **Related tickets:** ticket-041, ticket-046, ticket-047, ticket-048, ticket-049

## Context and Decision Question

The `oqlos/*` ecosystem manages embedded hardware scenarios, device configurations, and real-time sensor telemetry streams. In hardware-in-the-loop (HIL) automated testing and digital-twin calibration, verification requires comparing **declared scenario specifications** (expected operating frequency, thermal ceilings, required GPIO pinouts, and packet throughput) against **observed hardware telemetry logs**.

Prior to `ticket-046`, `data2dsl` normalized software facts (Git commits, Markdown claims, AST graphs, Docker topologies, Planfile tasks, Intent contracts), but lacked a dedicated hardware scenario and telemetry source adapter.

How should `data2dsl` normalize OQL scenario manifests and hardware telemetry streams into deterministic `autogrammar.data2dsl/observation/v0` records without taking direct runtime dependencies on embedded hardware toolchains?

## Decision

`data2dsl` introduces `OqlTelemetryAdapter` with the canonical extractor identity `oqlos.telemetry` (version `0.1.0`):

1. **Dual Response Modeling (`src/data2dsl_adapters.py`):**
   - **`OqlScenarioSpecResponse` (Left/Specification Observation):**
     - Captures declared scenario bounds: `sample_rate_hz`, `max_temperature_celsius`, `frequency_mhz`, `packet_throughput`, `active_pins`, and `buses`.
     - Evidence points to the scenario definition file (`.oql.json` / manifest) with start and end line ranges.
   - **`OqlTelemetryLogResponse` (Right/Telemetry Observation):**
     - Captures measured run data: `avg_sample_rate_hz`, `peak_temperature_celsius`, `observed_frequency_mhz`, `avg_packet_throughput`, `active_pins`, and `active_buses`.
     - Evidence points to timestamped telemetry logs with binary/JSON SHA-256 payload digests.

2. **Metric Normalization & Typed Deltas:**
   - **Scalar & Floating Point Metrics (`float`, `integer`):**
     - Sample rates, clock frequencies, and throughput map to `float` or `integer` value objects.
     - Thermal limits map to `float` (degrees Celsius) or `percentage` relative to operational maximums.
   - **Set-Based Pinout & Bus Verification (`string-set`):**
     - Active GPIO pin lists (`["PA0", "PA1", "PB4"]`) and communication buses are normalized to sorted string-sets, allowing the `DeterministicComparator` to compute exact added/removed pin deltas.

3. **Skill & Model Context Protocol (MCP) Integration (`src/data2dsl_skill.py`):**
   - `_normalize_raw` routes `oql`, `oqlos`, `oql_telemetry`, and `oql_spec` source kinds directly to `OqlTelemetryAdapter`.
   - MCP tools (`data2dsl_compare`) accept raw OQL dictionaries for autonomous test runner integration.

4. **Fault & Unavailable Handling:**
   - Missing scenario files or truncated telemetry streams transition cleanly to `state: "UNEVALUABLE"` with error evidence digests, preventing false positive comparisons.

## Consequences

- **Pure Functional Boundary:** `data2dsl` remains zero-dependency and effect-free. It does not communicate directly with hardware interfaces or JTAG/serial probes; acquisition is handled upstream by `oqlos/*` CLI or runners.
- **Deterministic HIL Comparison:** Automated hardware qualification suites can assert exact scalar threshold compliance and discrete pin state parity using cryptographic evidence chains.
- **Uniform Multi-Source Integration:** Telemetry comparisons generate the standard `autogrammar.data2dsl/result/v0` bundles, enabling automated routing into `doctor-agent` diagnostic feeds and `koru` remediation intents.
