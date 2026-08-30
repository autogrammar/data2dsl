# Ticket 079: Prevent identity fields from matching bottleneck queries

- **ID**: ticket-079
- **Owner**: founder:tom-sapletta-com
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-08-30

## Goal and scope

Repair the operational OR-query projection after live Supervisor integration
showed that terms such as `error` also matched repository identity fields.
List queries must select entity operational state, while the legacy single
string query retains its full graph metadata search behavior.

## Acceptance criteria

- [x] AC-01: SESSION_EXECUTION_AUTHORIZATION is recorded from the Founder's
  request to repair standardization regressions directly at their source.
- [x] AC-02: A list query cannot select an entity solely through repository,
  ticket, pull-request, label or pointer identity.
- [x] AC-03: The same list query selects entities through bounded operational
  status/error attributes and retains their immediate graph context.
- [x] AC-04: A legacy string query still searches full node metadata.
- [x] AC-05: Full tests, Ruff and governance pass; live fleet + PR projection
  contains no identity-only false positives.

## Validation evidence

- Regression fixture proves list terms `error` and `failed` do not select
  healthy repositories named `error_page` or `serialize-error`, while a
  legacy string query still finds `serialize-error` by identity.
- Live fleet + PR-controller canary returned 11 operational failures in a
  12-node, 11-edge graph and zero identity-only false positives.
- Complete suite: 145 passed; focused Ruff, governance and whitespace gates
  pass. The existing jsonschema deprecation warning remains unchanged.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)
