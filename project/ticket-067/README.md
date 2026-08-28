# Ticket 067: Resolve remediation schema collision and validate input comparison bundles (F09)

- **ID**: ticket-067
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-28

## Goal and scope

Fix audit finding F09:
1. `data2dsl_remediation.py` emitted schema identifier `new-project.remediation-intent/v1`, colliding with the local governance schema `.governance/remediation-intent.schema.json` which has a different schema structure. Update `SCHEMA_VERSION` to distinct identifier `autogrammar.data2dsl/remediation-feed/v0`.
2. Ensure input comparison bundles are strictly verified and evaluated against their observations rather than blindly trusting unvalidated outcome strings.

SESSION_EXECUTION_AUTHORIZATION recorded from user prompt.

## Acceptance criteria

- [x] AC-01: Scope is approved (SESSION_EXECUTION_AUTHORIZATION recorded).
- [x] AC-02: `RemediationIntentFormatter.SCHEMA_VERSION` is set to `autogrammar.data2dsl/remediation-feed/v0`.
- [x] AC-03: `RemediationIntentFormatter` validates and parses input comparison bundles accurately.
- [x] AC-04: Existing tests in `tests/test_remediation_feed.py` and new tests in `tests/test_remediation_f09.py` pass.
- [x] AC-05: Full pytest suite passes (119/119) and `governance-check.bat` reports GOV-PASS.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
