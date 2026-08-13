# Ticket 002: Twin observation compatibility decision

- **ID**: ticket-002
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-08-13

## Goal and scope

Produce one evidence-backed compatibility decision for using the current
`subactor/twin` `Observation` and `EvidenceRef` contracts in `data2dsl`.
Inspect the pinned code, protobuf schema, normative standard, reference profile
and tests. The result must select exactly one verdict: `REUSE AS-IS`, `EXTEND`
or `REJECT`, and state the consequences for `data2dsl`.

Out of scope: product implementation, final data-query DSL, edits to
`subactor/twin`, `wellmanifest/dsl` or any other repository, dependency
changes, and external coordination.

## Acceptance criteria

- [ ] AC-01: The decision pins the inspected `subactor/twin` revision.
- [ ] AC-02: Evidence covers protobuf, normative contract, validator code,
  reference profile and relevant tests.
- [ ] AC-03: Field-level fit and gaps for both `Observation` and `EvidenceRef`
  are explicit.
- [ ] AC-04: Exactly one verdict among `REUSE AS-IS`, `EXTEND`, and `REJECT` is
  selected with rationale.
- [ ] AC-05: Consequences and prohibited assumptions for `data2dsl` are stated.
- [ ] AC-06: No other repository is modified and the governance gate passes.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)
