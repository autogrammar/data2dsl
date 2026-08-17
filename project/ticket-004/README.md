# Ticket 004: Define data comparison contract v0

- **ID**: ticket-004
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-17

## Goal and scope

Define the smallest local, experimental `data2dsl` comparison contract v0 for
the golden case: compare a `work-summary.md` claim with GitHub activity for the
same repository, actor, metric and half-open UTC time window.

The contract must compose the existing `wellmanifest/dsl` query, observation
and result profiles by immutable reference. It adds only data2dsl-owned domain
semantics: canonical scalar/set values, evidence locators, comparability,
outcomes and typed deltas. It remains descriptive and effect-free.

Out of scope: changing `subactor/twin`, `wellmanifest/dsl` or another
repository; implementing source adapters, GitHub acquisition, an LLM layer or
an enforcing runtime; adding a runtime dependency; publishing a stable API.

## Acceptance criteria

- [x] AC-01: A closed JSON Schema defines query, observation and comparison
  result documents for scalar and string-set values.
- [x] AC-02: The contract pins and maps to the current immutable
  `wellmanifest/dsl` reusable profiles instead of copying their schema.
- [x] AC-03: Outcomes cover `MATCH`, `CONFLICT`, `MISSING_LEFT`,
  `MISSING_RIGHT` and `UNEVALUABLE`, separately from observation state.
- [x] AC-04: Evidence preserves locator, immutable source revision, media
  type, SHA-256, extractor identity/version and optional location.
- [x] AC-05: Golden conflict and match fixtures use identical subject, metric
  and window keys and pass deterministic validation.
- [x] AC-06: Invalid cross-key, ordering, digest and outcome/delta combinations
  are rejected by self-tests.
- [x] AC-07: The pinned `wellmanifest/dsl` checker accepts the local DSL
  manifest and the data2dsl governance gate passes.

## Result

The experimental contract lives in `src/data2dsl_contract_v0`. It composes
the immutable Wellmanifest query, observation and result profiles, defines a
closed data2dsl comparison bundle, and proves all five outcomes plus five
negative invariants without accessing a source network or changing another
repository.

The contract is integrated on the default branch at
`3c747c1b1d79426196fd4bb0b5dc42360d88a066` through GitHub PR 4.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)
