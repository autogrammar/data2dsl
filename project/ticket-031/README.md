# Ticket 031: Add pytest PYTHONPATH config and clean unused imports

- **ID**: ticket-031
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-08-21

## Goal and scope

Add `tests/conftest.py` so that `pytest` automatically resolves the `src/`
package directory without requiring a manual `PYTHONPATH` environment
variable, and remove unused imports across `src/` and `tests/` flagged by `ruff`.

No behavioral changes to comparator, contract, or CLI.

## Acceptance criteria

- [x] AC-01: `tests/conftest.py` configures `sys.path` for `src/`.
- [x] AC-02: `python -m pytest tests/ -q` passes without manual `PYTHONPATH`.
- [x] AC-03: `python -m ruff check src/ tests/` reports zero errors.
- [x] AC-04: The deterministic governance gate passes.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
