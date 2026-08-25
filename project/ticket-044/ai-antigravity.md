# Agent Plan: Ticket 044 - Koru Remediation Intent Generator

## Context

`semcod/koru` operates on a closed feedback loop:
`DETECT → PLAN → EXECUTE → VERIFY → HEAL`
When `data2dsl` detects a `CONFLICT` or missing fact during `VERIFY`, `koru` requires a deterministic, machine-actionable `remediation-intent` feed specifying:
- Exact subject and metric in discrepancy.
- Required delta / repair instruction (`synchronize_metric`, `restore_missing_entries`, `resolve_conflict`).
- Pre-repair cryptographically pinned SHA-256 evidence digests.

## Strategy

1. Implement `RemediationIntentFormatter` and `format_remediation_intent()` in `src/data2dsl_remediation.py`.
2. Add CLI subcommand `feed-koru` in `src/data2dsl_cli.py`.
3. Add full unit tests in `tests/test_remediation_feed.py`.
4. Validate ruff, pytest, and governance gate.
