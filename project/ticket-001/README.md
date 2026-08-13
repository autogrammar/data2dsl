# Ticket 001: Phase 0 capability inventory

- **ID**: ticket-001
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-13

## Goal and scope

Complete Phase 0 of the reuse-first `data2dsl` specification without adding
functional product code. Adopt immutable governance, establish the repository
bootstrap, inspect candidate capabilities in `semcod/*`, `subactor/*`, and
`wellmanifest/*`, inspect reusable seams embedded in `todo2code`, and publish
an evidence-backed capability map with a provisional composition graph.

Out of scope: final DSL design, extraction, refactoring, new parsers, new
GitHub clients, runtime dependencies, and golden-case implementation.

## Acceptance criteria

- [x] AC-01: Published immutable governance is adopted with a valid lock.
- [x] AC-02: Repository bootstrap includes Docker configuration and no product implementation.
- [x] AC-03: `docs/CAPABILITY_MAP.md` records input, output, coupling, evidence, status, and integration for every required capability class.
- [x] AC-04: Every decision is supported by current file, API, CLI, package, or test evidence; unknowns remain explicit.
- [x] AC-05: The composition graph prefers reuse, then extraction, then extension, and identifies genuine missing capability only when proven.
- [x] AC-06: The deterministic governance gate is run and its result is recorded.
- [x] AC-07: Docker validation is run, or the unavailable engine is reported as a blocker without host-runtime substitution.

## Phase result

All Phase 0 acceptance criteria pass. The user explicitly authorized creation
and publication of the public `semcod/data2dsl` GitHub repository on
2026-08-13. No product code, final DSL, extraction or refactor was introduced.
The published default branch contains the exact Phase 0 result at commit
`067b76b67802b17084c1209a5e96121dec5b8a2f`; this governance-only update closes
the completed ticket.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)
