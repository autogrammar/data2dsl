# Ticket 046: OQL Telemetry Source Adapter for Scenario Metrics

- **ID**: ticket-046
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-26
- **Closed**: 2026-08-26
- **Receipt**: Implemented OqlTelemetryAdapter and verified with 55 unit tests (100% pass) and GOV-PASS.

## Goal and scope

Implement the OQL Telemetry Source Adapter (`OqlTelemetryAdapter`) for normalizing embedded scenario metrics and telemetry logs into `data2dsl` `Observation` objects with `EvidenceRef`:
1. Define `OqlScenarioSpecResponse`, `OqlTelemetryLogResponse`, and `OqlTelemetryAdapter` in `src/data2dsl_adapters.py`.
2. Support metric normalization for sample rate (`float`/`integer`), thermal ceilings (`float`), active pinouts/buses (`string-set`), and throughput (`integer`/`float`).
3. Add comprehensive unit tests in `tests/test_oql_adapter.py`.
4. Verify governance gate and 100% pytest pass rate.

## Acceptance criteria

- [x] AC-01: `OqlTelemetryAdapter` normalizes OQL scenario specifications and observed telemetry logs into compliant `autogrammar.data2dsl/observation/v0` objects.
- [x] AC-02: Support `float`, `integer`, and `string-set` metric kinds with deterministic hash evidence.
- [x] AC-03: Full unit test coverage in `tests/test_oql_adapter.py` passing without errors.
- [x] AC-04: Existing 49 tests + new tests pass cleanly with pytest (55 total passing).
- [x] AC-05: Deterministic governance gate passes (`GOV-PASS`).

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
