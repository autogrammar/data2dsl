# Ticket 011: CLI interface and JSON bundle exporter for consumer tools

- **ID**: ticket-011
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-19

## Goal and scope

Implement a public CLI interface and JSON bundle exporter in `src/data2dsl_cli.py` and `src/__main__.py` allowing external consumers (such as `semcod/todo2code` or CI pipelines) to execute comparisons, run golden-case evaluations, and validate bundles from the command line.

## Acceptance criteria

- [x] AC-01: `src/data2dsl_cli.py` implements `compare`, `compare-golden`, `validate`, and `--self-test` subcommands.
- [x] AC-02: Executable as `python -m data2dsl` or via direct script execution.
- [x] AC-03: `tests/test_cli.py` validates CLI execution and output bundle conformance.
- [x] AC-04: The deterministic governance gate passes.

## Result

Implemented CLI entrypoint and tests. All 10 tests pass, and bundles conform to contract v0 schemas.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
