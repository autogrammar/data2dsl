# Ticket 037: Phase 3 extension: multi-source fact adapters (Planfile, Deta, Intent-Contract)

- **ID**: ticket-037
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-24
- **Closed**: 2026-08-24
- **Receipt**: Committed locally as `55ae4a1`.

## Goal and scope

Expand data2dsl factual source acquisition capabilities by implementing three
new adapters conforming to the `autogrammar.data2dsl/observation/v0` envelope:
1. `PlanfileAdapter` (`semcod/planfile`): Extracts ticket states, task counts, and ticket IDs.
2. `DetaAdapter` (`semcod/deta`): Extracts declared/observed services, ports, and endpoints.
3. `IntentContractAdapter` (`subactor/intent-contract-dsl-runtime`): Extracts contract deliverables, obligations, and parties.

## Acceptance criteria

- [x] AC-01: `PlanfileAdapter` normalizes ticket counts, ticket IDs, and statuses with SHA-256 evidence.
- [x] AC-02: `DetaAdapter` normalizes service counts, service sets, and port sets with manifest provenance.
- [x] AC-03: `IntentContractAdapter` normalizes deliverable counts, parties, and obligations with contract digests.
- [x] AC-04: `Data2DslSkill` dispatches raw payloads for `planfile`, `deta`, and `intent_contract`.
- [x] AC-05: Unit tests in `tests/test_golden_case_e2e.py` and `tests/test_skill.py` pass.
- [x] AC-06: The deterministic governance gate passes.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
