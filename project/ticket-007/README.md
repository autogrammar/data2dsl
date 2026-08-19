# Ticket 007: Phase 2: Implement source adapters and deterministic golden-case comparator

- **ID**: ticket-007
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-19

## Goal and scope

Implement the read-only GitHub and Markdown source adapters and deterministic comparator for `data2dsl`, delivering the complete end-to-end golden case comparison: comparing statements in `work-summary.md` with actual GitHub activity for the same repository, actor, metric and half-open UTC time window.

The implementation comprises:
1. `src/data2dsl_adapters.py`: GitHub commit metric adapter for `subactor/diagit` provider responses and Markdown source adapter for extracting commit claims from `work-summary.md`.
2. `src/data2dsl_comparator.py`: Deterministic comparator computing outcomes (`MATCH`, `CONFLICT`, `MISSING_LEFT`, `MISSING_RIGHT`, `UNEVALUABLE`) and typed deltas.

Out of scope: modifying external repositories in this checkout; implementing an LLM reasoning layer or mutating runtime.

## Acceptance criteria

- [x] AC-01: Implement `src/data2dsl_adapters.py` with `GitHubDiagitAdapter`, `WorkSummaryMarkdownAdapter` and `DiagitCommitMetricResponse`.
- [x] AC-02: Normalize commit metrics and claims into `autogrammar.data2dsl/observation/v0` format with complete `EvidenceRef` provenance.
- [x] AC-03: Implement `src/data2dsl_comparator.py` with deterministic scalar/set diff logic.
- [x] AC-04: Unit and end-to-end tests in `tests/test_golden_case_e2e.py` pass and conform to the deterministic contract validator in `src/data2dsl_contract_v0/validate.py`.
- [x] AC-05: The deterministic governance gate passes.

## Result

Implemented `src/data2dsl_adapters.py` and `src/data2dsl_comparator.py`. The full end-to-end golden case comparison (`work-summary.md` vs GitHub) passes all tests and conforms 100% to the normative JSON Schema and contract validator.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
