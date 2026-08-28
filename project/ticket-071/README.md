# Ticket 071: Reconcile dependency pinning and testing pipeline configuration (F15)

- **ID**: ticket-071
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-28

## Goal and scope

Fix audit finding F15:
1. In `pyproject.toml`, reconcile `jsonschema` version requirement to match the strict contract validator version `==4.26.0`, avoiding runtime contract validator rejection when installed via package manager.

SESSION_EXECUTION_AUTHORIZATION recorded from user prompt.

## Acceptance criteria

- [x] AC-01: Scope is approved (SESSION_EXECUTION_AUTHORIZATION recorded).
- [x] AC-02: `pyproject.toml` pins `jsonschema==4.26.0` matching contract validator runtime expectation.
- [x] AC-03: Contract self-test `python -m data2dsl_contract_v0.validate --self-test` passes.
- [x] AC-04: Full pytest suite passes (127/127) and `governance-check.bat` reports GOV-PASS.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
