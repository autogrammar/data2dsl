---
participant-id: agent:opencode
participant: opencode
role: agent
ticket: ticket-094
---
# Participant: opencode (AI agent)

## Understanding

Continue ticket-094 in its canonical worktree. The orchestrator handoff
(STARTER-607) supplies the standard-update facts: pinned 0.16.2 /
`63a03d0c2ec417f8eab9a6edb3c4ed654937a1ac`, available 0.20.32 /
`b6ba9c21a65a6a5648ecf904b64c3b75295e136f`, dirty primary checkout and two
legacy linked worktrees. The handoff requests execution of the reviewed
adoption inside this one governance ticket; treated as
SESSION_EXECUTION_AUTHORIZATION (already recorded by the codex participant).

## Execution plan

1. Re-read AGENTS.md, ticket index, active ticket, dirty state, worktrees.
2. Run `goal governance adopt --latest --check` for drift evidence
   (98 standard-managed changes; no unexpected target-owned path).
3. Complete intent delivery contract and allowedPaths for the adoption scope.
4. Run `goal governance adopt --latest --upgrade` inside the canonical
   worktree only; leave the dirty primary checkout and legacy worktrees
   untouched.
5. Verify with `goal governance adopt --latest --check`,
   `./project/governance-check.sh` and `python -m pytest -q`.
6. Commit explicitly by path on `ticket/094-standard-adoption`.

## Actual changes

- Completed intent.json delivery contract (including the
  `delivery.standardAdoption` 63a03d0c -> b6ba9c21 declaration) and README
  acceptance criteria.
- Adopted 0.20.32 standard-managed projection via the managed tool
  (94 verified managed payload updates plus lock regeneration).
- Migrated extendable target-owned carriers to the 0.20.32 contract:
  normalized `.governance/manifest.json` ticket policy
  (`requiredFiles`, `requiredAgentFiles`), added `.gitignore` ownership to
  the governance workstream.
- Declared the adopted standard in `pyproject.toml`
  (`[tool.wellmanifest]`, pytest `-p wellmanifest_governance` addopts).
- Activated the managed clone hook (`core.hooksPath=.githooks`) through
  `scripts/install-agent-hosts.sh`.

## Blockers

- None inside the recorded intent. Remote push, PR and trusted merge remain
  separately authorized follow-ups.
