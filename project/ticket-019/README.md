# Ticket 019: Add Curllm browser source adapter and unit tests

- **ID**: ticket-019
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-20

## Goal and scope

Add `CurllmAdapter` and `CurllmMetricResponse` in `src/data2dsl_adapters.py` to support
browser-backed facts (e.g. from `semcod/curllm` BQL outputs) as a normalized source
observation in `data2dsl`.
Add unit tests verifying successful extraction, structured evidence generation, and
error handling (`UNEVALUABLE`) in `tests/test_golden_case_e2e.py`.

## Acceptance criteria

- [x] AC-01: `CurllmMetricResponse` and `CurllmAdapter` are implemented in `src/data2dsl_adapters.py`.
- [x] AC-02: Unit tests in `tests/test_golden_case_e2e.py` verify observation normalization and provenance.
- [x] AC-03: The deterministic governance gate passes.
- [x] AC-04: The full test suite passes.

## Result

Ticket 019 closed from integrated evidence:
- PR #20 approved at `3f592f74cf9af684968ceaa125c29e9457b1818d` (Decision `D-019-4852`), merged as `d303ea0c50617c0a459c4e4a63ab3c7a102e2a53`.
- Branch `agent/adapter-curllm-019` deleted upon merge.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
