# Ticket 015: Phase 4: reasoning consumer integration feed for todo2code

- **ID**: ticket-015
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-08-19

## Goal and scope

Implement the reasoning consumer integration feed for `todo2code` and other decision engines. Converts validated `data2dsl` comparison bundles into structured factual payloads (`ConsumerFactFeed` and CLI `feed-consumer`) preserving complete cryptographic evidence provenance while strictly maintaining separation of concerns (`data2dsl` provides facts and deltas; `todo2code` performs reasoning and policy).

## Acceptance criteria

- [x] AC-01: `ConsumerFactFeed` implemented in [`src/data2dsl_consumer.py`](../../src/data2dsl_consumer.py).
- [x] AC-02: CLI subcommand `feed-consumer` supported in [`src/data2dsl_cli.py`](../../src/data2dsl_cli.py).
- [x] AC-03: Complete unit and integration test suite passing in [`tests/test_consumer.py`](../../tests/test_consumer.py).
- [x] AC-04: Strict separation of concerns preserved (no subjective/policy logic in `data2dsl`).
- [x] AC-05: The deterministic governance gate passes.

## Result

Phase 4 completed: consumer fact feed module and CLI subcommand implemented, tested (13/13 tests pass), and verified against the deterministic governance gate.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
