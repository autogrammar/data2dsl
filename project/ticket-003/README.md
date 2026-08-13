# Ticket 003: Explain the data2dsl project

- **ID**: ticket-003
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-08-13

## Goal and scope

Rewrite the root README so a new contributor can understand the concrete
problem, users, inputs, outputs, golden case, product boundary, reuse-first
composition and staged roadmap without reconstructing the vision from Phase 0
evidence documents.

Out of scope: product implementation, final schemas or APIs, dependency
changes, edits outside data2dsl, and changes to technical decisions already
recorded in evidence documents.

## Acceptance criteria

- [x] AC-01: README explains the problem and intended users.
- [x] AC-02: README defines inputs, outputs and the golden case concretely.
- [x] AC-03: README distinguishes responsibilities and non-goals.
- [x] AC-04: README presents the reuse-first composition and staged roadmap.
- [x] AC-05: Claims remain consistent with the capability map and no product
  implementation is introduced.
- [x] AC-06: Governance passes and no other repository is modified.

## Result

The root README is now the canonical onboarding description of the planned
product. It distinguishes intended behavior from unimplemented contracts and
links detailed capability evidence rather than duplicating it.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)
