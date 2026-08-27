# Ticket Changelog (ticket-056)

## [0.1.0] - 2026-08-27

- Initial governance scaffold created.
- Implemented `format_markdown_report` in `src/data2dsl_batch.py`.
- Added `--format` (json | markdown) argument to `compare` and `batch` subcommands in `src/data2dsl_cli.py`.
- Added test suite in `tests/test_batch_compare.py` (84/84 tests passing).
- Validated deterministic governance check (`GOV-PASS`).
