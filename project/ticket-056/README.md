# Ticket 056: Markdown Report Formatting for CLI and Batch

- **ID**: ticket-056
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-08-27
- **Receipt**: Implemented format_markdown_report and added --format flag to compare and batch CLI subcommands; 84/84 pytest tests passing and GOV-PASS.

## Goal and scope

Implement Markdown Report Formatting for CLI and Batch operations:
1. Implement `format_markdown_report(report_or_bundle)` in `src/data2dsl_batch.py` rendering clear tables for metrics, outcomes, deltas, and evidence hashes.
2. Add `--format` argument (`json` [default] | `markdown`) to `data2dsl compare` and `data2dsl batch` subcommands in `src/data2dsl_cli.py`.
3. Add unit and CLI tests in `tests/test_batch_compare.py`.
4. Verify all tests pass cleanly and deterministic governance gate passes (`GOV-PASS`).

## Acceptance criteria

- [x] AC-01: `format_markdown_report` generates compliant Markdown tables summarizing batch and single comparison results.
- [x] AC-02: `data2dsl batch --format markdown` and `data2dsl compare --format markdown` output readable Markdown.
- [x] AC-03: Unit and CLI tests pass in `tests/test_batch_compare.py`.
- [x] AC-04: Full pytest test suite and governance check pass (`GOV-PASS`).

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
