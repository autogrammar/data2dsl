# Ticket 001: Phase 0 capability inventory

- **ID**: ticket-001
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
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

- [ ] AC-01: Published immutable governance is adopted with a valid lock.
- [ ] AC-02: Repository bootstrap includes Docker configuration and no product implementation.
- [ ] AC-03: `docs/CAPABILITY_MAP.md` records input, output, coupling, evidence, status, and integration for every required capability class.
- [ ] AC-04: Every decision is supported by current file, API, CLI, package, or test evidence; unknowns remain explicit.
- [ ] AC-05: The composition graph prefers reuse, then extraction, then extension, and identifies genuine missing capability only when proven.
- [ ] AC-06: The deterministic governance gate is run and its result is recorded.
- [ ] AC-07: Docker validation is run, or the unavailable engine is reported as a blocker without host-runtime substitution.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)
