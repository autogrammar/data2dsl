# Ticket 070: Fix runnable examples 01-08 and synchronize README documentation (F14)

- **ID**: ticket-070
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: VALIDATION
- **Created**: 2026-08-28

## Goal and scope

Fix audit finding F14:
1. Ensure all examples 01 through 08 in `examples/` have syntactically valid and contract-compliant inputs and expected bundles:
   - Example 01 & 02: Valid comparison bundles adhering strictly to `autogrammar.data2dsl/comparison-bundle/v0`.
   - Example 05: Valid MCP request payload with proper query window semantics.
   - Example 07: Accurate CLI commands using `--left-source-type`/`--right-source-type`.
   - Example 08: Complete observations with valid `target_uri` and locations.
2. Synchronize main repository `README.md` to reflect actual implemented features and tool endpoints.
3. Add automated integrity test `tests/test_examples_integrity.py`.

SESSION_EXECUTION_AUTHORIZATION recorded from user prompt.

## Acceptance criteria

- [x] AC-01: Scope is approved (SESSION_EXECUTION_AUTHORIZATION recorded).
- [x] AC-02: All example schemas and sample data in `examples/01*` - `examples/08*` pass validation.
- [x] AC-03: `README.md` accurately documents MCP tools, adapters, CLI commands and capabilities without obsolete claims.
- [x] AC-04: `tests/test_examples_integrity.py` validates all examples successfully.
- [x] AC-05: Full pytest suite passes (127/127) and `governance-check.bat` reports GOV-PASS.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
