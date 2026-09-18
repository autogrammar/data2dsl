# ticket-095 — Bootstrap regix/wup/testql on-change gates

- **Status**: BLOCKED
- **Maps planfile**: STARTER-022 (regix), STARTER-023 (testql), STARTER-024 (wup)

## Goal
Add `regix.yaml`, `wup.yaml`, `testql-scenarios/` at the repository root —
the koru on-change gate stack, adapted to the data2dsl `src/` layout.

## Blocker (GOV-WORKSTREAM-003 deadlock)
1. `koru-scan` `missing_gate` requires the marker at **project root**
   (`(project/"regix.yaml").exists()` in `koru/scan.py`) — nested placement
   under `infra/` or `examples/` would not satisfy the scan.
2. No workstream in `.governance/manifest.json` owns root `*.yaml` gate
   configs (`infrastructure` owns only `Dockerfile*`, `compose*`, `infra/**`,
   `.github/**`).
3. Adding ownership is a `.governance/manifest.json` change → `governance`
   workstream → reserved by in-flight `ticket-094` (0.20.32 adoption,
   branch pushed, unmerged). Allocator refused a second governance ticket.

## Resolution path
1. Wait for ticket-094 merge (or its explicit closure).
2. Governance ticket: add `regix.yaml`, `wup.yaml`, `testql-scenarios/**`
   to `infrastructure.ownedPaths` (or a new `quality` workstream).
3. Reopen this ticket (IN_PROGRESS), commit the already-drafted configs
   on branch `ticket/095-on-change-gates`, merge.

## Drafted (unmerged, branch `ticket/095-on-change-gates`)
- `regix.yaml` — CC15/MI20/cov50 gates over `src/**`
- `wup.yaml` — 3-layer watcher over `src/**`, quick CLI smoke → full scenario
- `testql-scenarios/generated-cli-smoke.testql.toon.yaml`
