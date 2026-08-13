# data2dsl

`data2dsl` is a planned reuse-first composition layer for turning existing
data-source capabilities into comparable, evidence-bearing observations.

The project is currently in Phase 0: governance bootstrap and capability
inventory. No functional implementation or final architecture is approved.

## Phase 0 outcome

- verify reusable capabilities in `semcod/*`, `subactor/*`, and
  `wellmanifest/*`;
- inspect reusable seams currently embedded in `semcod/todo2code`;
- record evidence and decisions in `CAPABILITY_MAP.md`;
- propose a composition graph without implementing product features.

## Architectural invariant

Reuse first. Extract second. Extend third. Implement new only as a last resort.

`data2dsl` must remain a small composition, routing, mapping, normalization,
and comparison-glue layer rather than becoming a replacement monolith for
`todo2code`.

## Governance

This repository adopts an immutable published revision of
`wellmanifest/new-project`. Multi-step work is ticket-governed and bounded by
the active ticket's `intent.json`.
