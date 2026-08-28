# Ticket 061: Fix markdown actor claim parsing and metric.id mapping across adapters (F04, F05)

- **ID**: ticket-061
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-28

## Goal and scope

Fix audit findings F04 and F05:
1. `MarkdownClaimExtractor.extract_commit_claim` (line 235) was matching any line containing `"commit"` due to an OR condition, incorrectly assigning Bob's commits to Alice when Bob was listed first. Require exact actor matching.
2. In Deta, IntentContract, and OQL adapters, metric fields were queried using `metric.get("name")` / `metric.get("property")`, which are not part of canonical `query/v0` metrics (only `metric.id` exists), causing metric matching to fail and convert measurements to `0.0` or empty sets (resulting in false MATCH outcomes).
3. Distinguish missing measurements from valid `0.0` values; return `UNEVALUABLE` for unknown/unsupported metrics rather than silent fallback to `0.0`.

SESSION_EXECUTION_AUTHORIZATION recorded from user prompt.

## Acceptance criteria

- [x] AC-01: Scope is approved (SESSION_EXECUTION_AUTHORIZATION recorded).
- [x] AC-02: `extract_commit_claim` strictly extracts claims for the queried actor and does not match other actors' lines.
- [x] AC-03: Deta, IntentContract, and OQL adapters extract metrics based on `metric.get("id")`.
- [x] AC-04: Unknown metrics produce `UNEVALUABLE` observations instead of silent `0.0` values.
- [x] AC-05: Unit tests in `tests/test_adapters_f04_f05.py` verify actor isolation in multi-actor markdown and correct metric.id mapping.
- [x] AC-06: Full pytest suite passes (104/104) and `governance-check.bat` reports GOV-PASS.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
