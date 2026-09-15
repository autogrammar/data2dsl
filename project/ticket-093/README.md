# Ticket 093: Add automatic Planfile GitHub synchronization

- **ID**: ticket-093
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-09-15

## Goal and scope

To be completed from human-owned input.

## Acceptance criteria

- [ ] AC-01: Scope is approved by a human owner.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)

## Implementation scope

Add `.github/workflows/planfile-github-sync.yml` with the `semcod/planfile@v0.1.126` reusable workflow.
It runs hourly, on relevant Planfile changes, and through manual dispatch.
The caller grants only `contents: read` and `issues: write`.

## Session authorization

The user's request to update the other projects records
`SESSION_EXECUTION_AUTHORIZATION` for this bounded implementation.
