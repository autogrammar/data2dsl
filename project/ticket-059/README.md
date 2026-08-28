# Ticket 059: Fix comparison contract schema and query generator (F02)

- **ID**: ticket-059
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-28

## Goal and scope

Fix audit finding F02: the comparison contract schema only allows source kinds
`markdown` and `github`, while 8 additional adapters emit other kinds and
location types. The query generator produces metric versions, equality policies,
and time periods that are rejected by the contract validator.

SESSION_EXECUTION_AUTHORIZATION recorded from user approval of implementation
plan in conversation 78d87a8b-d52c-4b44-b8f5-077656700b95.

Changes are limited to:
- `src/data2dsl_contract_v0/comparison.schema.json` — extend source kinds,
  location types
- `src/data2dsl_generator.py` — fix metric version, policy, period
- `tests/test_generator.py` — add acceptance test: generated templates pass
  validation

No new dependencies, external coordination, or secret access required.

## Acceptance criteria

- [x] AC-01: Scope is approved (SESSION_EXECUTION_AUTHORIZATION recorded).
- [x] AC-02: Schema accepts all 10 adapter source kinds and their location types.
- [x] AC-03: Generator emits valid metric version (`v1`), valid equality policy,
  and dynamic time period.
- [x] AC-04: `generate_query_template()` output for every adapter passes
  `validate_document()`.
- [x] AC-05: All existing tests still pass (91/91). New acceptance test added.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
