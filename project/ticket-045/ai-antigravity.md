# Agent Plan: Ticket 045 - Documentation & ADR-005 for Autonomous Agent Integration

## Context

Following the implementation of `DiagnosticProfileFormatter` (ticket-043) and `RemediationIntentFormatter` (ticket-044), ticket-045 formalizes the architectural decision record (ADR-005) and updates project documentation:
- ADR-005 capturing the integration of `data2dsl` with `subactor/doctor-agent` and `semcod/koru`.
- Capability map update in `docs/CAPABILITY_MAP.md` covering formatting feeds and feedback loops.
- Updating `CHANGELOG.md` and `README.md` to reflect 49 unit tests, new CLI commands, and ADR-005.

## Strategy

1. Author `docs/decisions/ADR-005-autonomous-agent-feedback-feeds.md`.
2. Update `docs/CAPABILITY_MAP.md` table and Mermaid composition graph.
3. Update `CHANGELOG.md` and `README.md`.
4. Update `project/TICKETS.md` and `TODO.md`.
5. Run full test suite and governance checks.
