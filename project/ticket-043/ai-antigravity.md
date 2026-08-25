# Agent plan: ticket-043

- **Agent**: ai-antigravity
- **Date**: 2026-08-25
- **Ticket**: ticket-043

## Implementation Plan

1. Implement `DiagnosticProfileFormatter` in `src/data2dsl_doctor.py`:
   - Process single bundles or lists of comparison bundles.
   - Calculate delta magnitudes, severities (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFO`), and sort symptoms by priority.
   - Extract `left_evidence`, `right_evidence`, `missing_keys`, `evidence_chain` with SHA-256 integrity digests.
   - Generate summary breakdown of symptoms by severity.
2. Update `src/data2dsl_cli.py`:
   - Add subparser `feed-doctor` taking `--bundle` / `--output`.
3. Author unit tests in `tests/test_doctor_feed.py`.
4. Run tests and verify governance.
