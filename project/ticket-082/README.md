# Ticket 082: Audit P1 fixes — comparability, adapters, batch, feeds

- **ID**: ticket-082
- **Owner**: gemini (SESSION_EXECUTION_AUTHORIZATION)
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-31
- **Workstream**: application

## Goal and scope

Resolve all 6 P1 blockers identified in the code audit of 2026-08-28 (commit 5eb2e32):

1. **P1.2** — Comparability validation: extend `_is_compatible()` to check side, unit, version, semantics
2. **P1.3** — Batch deduplication: detect duplicate observations, error on ambiguity
3. **P1.4** — Adapter correctness: OQL buses, Code2Schema entities, error status, zero handling, telemetry windows
4. **P1.5** — Exact matching: actor word boundary, SUMD exact key match
5. **P1.6** — Evidence integrity: sanitize path separators in evidence IDs
6. **P1.2 ext** — Doctor/Remediation: fallback defaults, output validation

## Acceptance criteria

- [x] AC-01: SESSION_EXECUTION_AUTHORIZATION recorded
- [ ] AC-02: All 6 audit P1 items resolved with passing tests
- [ ] AC-03: No regression in existing 145 tests
- [ ] AC-04: ruff clean, mypy clean
- [ ] AC-05: New tests cover each fixed issue

## Participants

- Human participant: USER (session authorization)
- Agent participant: [ai-gemini.md](ai-gemini.md)
