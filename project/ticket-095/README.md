# ticket-095 — Bootstrap on-change regression gates

- **Status**: IN_PROGRESS

## Goal
Bootstrap the koru on-change gate stack (regix + wup + testql scenarios)
for data2dsl, satisfying planfile bootstrap tickets.

## Changes
- `regix.yaml` — CC/MI/coverage regression gates (src/** scope)
- `wup.yaml` — 3-layer on-change watcher (detect → quick smoke → full)
- `testql-scenarios/generated-cli-smoke.testql.toon.yaml` — CLI smoke scenario
