# Ticket 057: Batch Example 08 and Root Documentation Synchronization

- **ID**: ticket-057
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-08-27
- **Receipt**: Created examples/08-batch-multi-query, updated examples/README.md and root README.md; 84/84 pytest tests passing and GOV-PASS.

## Goal and scope

Synchronize examples and documentation:
1. Create `examples/08-batch-multi-query/` featuring complete runnable fixtures (`queries.json`, `left-observations.json`, `right-observations.json`, `README.md`).
2. Update `examples/README.md` with index of all 8 example suites.
3. Update root `README.md` with comprehensive documentation of CLI commands (`compare`, `batch`, `generate-query`, `validate-envelope`, `simulate-healing`), 10 source adapters, and Subactor integration.
4. Verify all tests pass cleanly and deterministic governance gate passes (`GOV-PASS`).

## Acceptance criteria

- [x] AC-01: `examples/08-batch-multi-query/` contains runnable test fixtures and execution instructions.
- [x] AC-02: `examples/README.md` and root `README.md` document all current features, CLI options, and architecture.
- [x] AC-03: Full pytest test suite and governance check pass (`GOV-PASS`).

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
