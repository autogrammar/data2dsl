# Ticket 094: Adopt wellmanifest/new-project 0.20.32 governance standard

- **ID**: ticket-094
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: EDIT
- **Created**: 2026-09-17

## Goal and scope

Adopt the wellmanifest/new-project standard update from pinned 0.16.2
(revision `63a03d0c2ec417f8eab9a6edb3c4ed654937a1ac`) to available 0.20.32
(revision `b6ba9c21a65a6a5648ecf904b64c3b75295e136f`) inside this governance
adoption ticket and its canonical worktree
`.worktrees/ticket-094--standard-adoption` (branch `ticket/094-standard-adoption`,
base `47966a773286a14fcbc5dd689382c14f5cad7a4a`).

The adoption is performed by the managed adoption tool
(`goal governance adopt --latest --upgrade`) and replaces reviewed
standard-managed drift only. Unknown local work (dirty files and untracked
koru/planfile artifacts in the primary checkout, legacy worktrees registered
outside this checkout under the clone parent) is left untouched.

## Acceptance criteria

- [x] AC-01: Scope is approved by a human owner (orchestrator handoff
  STARTER-607 requests execution of this reviewed adoption; recorded as
  SESSION_EXECUTION_AUTHORIZATION).
- [x] AC-02: `goal governance adopt --latest --check` reports no remaining
  standard-managed drift after the upgrade, `./project/governance-check.sh`
  passes and the test suite passes on the ticket branch.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)
- Agent participant: [ai-opencode.md](ai-opencode.md)

## Evidence

- Pre-adoption check: 98 standard-managed changes required
  (version-mismatch 0.16.2 -> 0.20.32, revision-mismatch).
- Ticket allocated through `./project/new-ticket.sh`
  (clone high-water reservation: 94).
