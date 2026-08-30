# Ticket 079: Prevent identity fields from matching bottleneck queries

- **ID**: ticket-079
- **Owner**: founder:tom-sapletta-com
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-08-30

## Goal and scope

Repair the operational OR-query projection after live Supervisor integration
showed that terms such as `error` also matched repository identity fields.
List queries must select entity operational state, while the legacy single
string query retains its full graph metadata search behavior.

## Acceptance criteria

- [ ] AC-01: SESSION_EXECUTION_AUTHORIZATION is recorded from the Founder's
  request to repair standardization regressions directly at their source.
- [ ] AC-02: A list query cannot select an entity solely through repository,
  ticket, pull-request, label or pointer identity.
- [ ] AC-03: The same list query selects entities through bounded operational
  status/error attributes and retains their immediate graph context.
- [ ] AC-04: A legacy string query still searches full node metadata.
- [ ] AC-05: Full tests, Ruff and governance pass; live fleet + PR projection
  contains no identity-only false positives.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)
