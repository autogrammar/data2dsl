# Ticket 055: Query Template Generator and Tooling

- **ID**: ticket-055
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-08-27
- **Receipt**: Implemented generate_query_template and CLI subcommand generate-query; 83/83 pytest tests passing and GOV-PASS.

## Goal and scope

Implement Query Template Generator and CLI integration:
1. Implement `src/data2dsl_generator.py` with `generate_query_template()` generating canonical `autogrammar.data2dsl/query/v0` templates based on source adapter kind, metric ID, and comparison policy.
2. Expose CLI subcommand `data2dsl generate-query --source <kind> --metric <id> [--value-kind <kind>] [--equality <eq>] [--output <file>]`.
3. Add comprehensive unit tests in `tests/test_generator.py`.
4. Verify all tests pass cleanly and deterministic governance gate passes (`GOV-PASS`).

## Acceptance criteria

- [x] AC-01: `generate_query_template()` produces compliant query objects for all 10 supported source adapter types.
- [x] AC-02: `data2dsl generate-query` CLI command outputs valid JSON templates with exit code 0.
- [x] AC-03: Unit and CLI tests pass in `tests/test_generator.py`.
- [x] AC-04: Full pytest test suite and governance check pass (`GOV-PASS`).

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
