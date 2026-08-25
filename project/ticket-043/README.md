# Ticket 043: Diagnostic Profile Feed for doctor-agent and semcod/koru triage

- **ID**: ticket-043
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-25
- **Closed**: 2026-08-25
- **Receipt**: Implemented and validated locally.

## Goal and scope

Implement Diagnostic Profile Feed generation from `data2dsl` comparison bundles to provide actionable, cryptographically verifiable discrepancy profiles for `subactor/doctor-agent` and `semcod/koru`:
1. Implement `src/data2dsl_doctor.py` with `DiagnosticProfileFormatter` and `format_diagnostic_profile()`.
2. Support prioritized symptom extraction, typed deltas (percentage, float, integer, string-set), evidence chains with SHA-256 digests, and severity summary metrics.
3. Expose via CLI command `feed-doctor` in `src/data2dsl_cli.py`.
4. Provide comprehensive unit tests in `tests/test_doctor_feed.py`.

## Acceptance criteria

- [x] AC-01: `src/data2dsl_doctor.py` formats comparison results into structured diagnostic profiles conforming to research specifications.
- [x] AC-02: Discrepancy symptoms are prioritized by delta magnitude and classified with deterministic severities (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFO`).
- [x] AC-03: CLI command `feed-doctor` is exposed in `src/data2dsl_cli.py`.
- [x] AC-04: Test suite `tests/test_doctor_feed.py` passes with full coverage.
- [x] AC-05: The deterministic governance gate passes.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
