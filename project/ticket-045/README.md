# Ticket 045: Documentation and ADR-005 for Autonomous Agent Integration (doctor-agent, koru)

- **ID**: ticket-045
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-25
- **Closed**: 2026-08-25
- **Receipt**: Implemented and validated locally.

## Goal and scope

Document architectural decision and update capability map for autonomous agent feedback feeds (`subactor/doctor-agent` and `semcod/koru`):
1. Author `docs/decisions/ADR-005-autonomous-agent-feedback-feeds.md`.
2. Update `docs/CAPABILITY_MAP.md` with Doctor Diagnostic Profile Formatter and Koru Remediation Intent Formatter entries and Mermaid composition graph.
3. Update `CHANGELOG.md` and `README.md` with ticket 043-045 accomplishments (feeds, CLI commands, test suites, ADR-005).
4. Run full test suite (`pytest`) and governance gate (`governance-check.bat`).

## Acceptance criteria

- [x] AC-01: `docs/decisions/ADR-005-autonomous-agent-feedback-feeds.md` is authored and conforms to ADR standards.
- [x] AC-02: `docs/CAPABILITY_MAP.md` reflects autonomous agent feedback capabilities and updated mermaid graph.
- [x] AC-03: `CHANGELOG.md` and `README.md` are updated with current state (doctor/remediation feeds, 49 tests, ADR-005).
- [x] AC-04: Full pytest test suite (49 tests) passes.
- [x] AC-05: The deterministic governance gate passes (`GOV-PASS`).

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
