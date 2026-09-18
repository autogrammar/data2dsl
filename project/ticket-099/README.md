# Ticket 099: Reduce CC in skill/cli/batch/remediation/contract validation

- **ID**: ticket-099
- **Owner**: agent
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-09-18

## Goal and scope

Reduce cyclomatic complexity to <=15 (regix `cc_max`) in the remaining
flagged functions:

- `data2dsl_skill.py`: `_normalize_raw` (CC 47) — dispatch dict +
  per-adapter `_norm_*` handlers and evidence-list builders.
- `data2dsl_cli.py`: `main` (CC 44) — `_COMMAND_HANDLERS` dispatch,
  `_cmd_*` handlers, shared `_emit*` output helpers.
- `data2dsl_batch.py`: `compare_batch` (CC 45) — `_index_observations`,
  `_resolve_observation`, outcome counts table;
  `format_markdown_report` (CC 21) — `_batch_report_lines`,
  `_single_report_lines`, `_side_observations`, `_bundle_row`.
- `data2dsl_remediation.py`: `format_intent` (CC 44) — `_process_bundle`,
  `_conflict_action`, `_action_item`, `_overall_status`,
  `_status_summary`.
- `data2dsl_contract_v0/validate.py`: `validate_document` (CC 35) —
  `_check_schema`, `_check_query_result`, `_check_observations`,
  `_check_observation*`, `_check_result_references`, `_expected_outcome`,
  `_check_outcome`.

Public signatures, exit codes and output shapes are unchanged.

## Acceptance criteria

- [x] AC-01: `lizard -C 15 -w src/` reports zero warnings.
- [x] AC-02: `python -m pytest -q` passes (158 tests).
- [x] AC-03: `./project/governance-check.sh` GOV-PASS.
- [x] AC-04: `contract_v0` self_test passes (5 positive, 5 negative).

## Changelog

- All high-CC functions in `src/` now at or below the CC=15 gate limit.
