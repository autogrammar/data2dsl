# Ticket 024: Promote comparison contract to stable 0.1.0 in dsl-manifest

- **ID**: ticket-024
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-08-20

## Goal and scope

Promote `src/data2dsl_contract_v0/dsl-manifest.json` contract version from `0.1.0-dev`
to `0.1.0` and lifecycle status from `experimental` to `stable`, reflecting complete
implementation of normalized source adapters, deterministic comparison, and consumer export.

## Acceptance criteria

- [x] AC-01: `dsl-manifest.json` version is promoted to `0.1.0` and status is set to `stable`.
- [x] AC-02: `python src/data2dsl_contract_v0/validate.py --self-test` passes.
- [x] AC-03: The deterministic governance gate passes.
- [x] AC-04: The full test suite passes.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
