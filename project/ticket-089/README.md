# Ticket 089: Split data2dsl_adapters god module

- **ID**: ticket-089
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-09-01

## Goal and scope

Split `src/data2dsl_adapters.py` (~1796 lines, 25 classes) into focused
submodules by adapter family while preserving the public `data2dsl_adapters`
import surface (facade re-exports).

Addresses Koru planfile ticket **STARTER-061**.

## Acceptance criteria

- [x] AC-01: Each adapter family lives in `data2dsl_adapters_<family>.py`.
- [x] AC-02: `data2dsl_adapters.py` remains a stable facade with `__all__`.
- [x] AC-03: `pyproject.toml` lists every new standalone module.
- [x] AC-04: Full pytest suite passes (145 tests).
- [ ] AC-05: Governance pass and merge to `main`.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-cursor-auto.md](ai-cursor-auto.md)
