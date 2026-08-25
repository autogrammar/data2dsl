# Ticket 044: Koru Remediation Intent Generator (`src/data2dsl_remediation.py` and CLI `feed-koru`)

- **ID**: ticket-044
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-25
- **Closed**: 2026-08-25
- **Receipt**: Implemented and validated locally.

## Goal and scope

Implement `RemediationIntentFormatter` and `format_remediation_intent()` in `src/data2dsl_remediation.py` to produce structured `remediation-intent/v1` payloads for `semcod/koru` closed-loop self-healing based on `docs/research-koru-closed-loop.md`:
1. Implement `src/data2dsl_remediation.py` transforming comparison results into actionable repair manifests.
2. Support deterministic status mapping (`PROPOSED`, `SATISFIED`, `BLOCKED`), typed action items (`synchronize_metric`, `restore_missing_entries`, `resolve_conflict`), and cryptographically pinned evidence digests.
3. Expose CLI command `feed-koru` in `src/data2dsl_cli.py`.
4. Provide unit test suite in `tests/test_remediation_feed.py`.

## Acceptance criteria

- [x] AC-01: `src/data2dsl_remediation.py` transforms comparison bundles into structured `new-project.remediation-intent/v1` documents.
- [x] AC-02: Actionable items and evidence digests are deterministically formatted for `CONFLICT`, `MISSING_LEFT`, `MISSING_RIGHT`, `MATCH`, and `UNEVALUABLE`.
- [x] AC-03: CLI command `feed-koru` is implemented in `src/data2dsl_cli.py`.
- [x] AC-04: Full unit test coverage in `tests/test_remediation_feed.py`.
- [x] AC-05: The deterministic governance gate passes (`GOV-PASS`).

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
