# Ticket 097: Reduce CC in adapter normalizers

- **ID**: ticket-097
- **Owner**: agent
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-09-18

## Goal and scope

Reduce cyclomatic complexity to <=15 (regix `cc_max`) in the adapter
normalizers flagged by the health findings:

- `oql.py`: `normalize_spec` + `normalize_telemetry` (CC 38/38)
- `intent.py`: `normalize` (CC 29)
- `deta.py`: `normalize` (CC 28)
- `planfile.py`: `normalize` (CC 19)
- `sumd.py`: `extract_table_metric` (CC 22)

Approach: shared observation/evidence/value helpers extracted into
`data2dsl_adapter_parts/common.py` (`observation_envelope`,
`evidence_entry`, `error_observation`, `unsupported_observation`,
`numeric_value`, `temperature_value`, `set_value`) plus per-module
metric dispatch and evidence builders. Public signatures and the
`observation/v0` envelope shape are unchanged.

`src/data2dsl_batch.py` (`compare_batch` CC 45, `format_markdown_report`
CC 21) is outside this ticket's `allowedPaths` and remains for a
follow-up slice.

## Acceptance criteria

- [x] AC-01: `lizard -C 15 src/data2dsl_adapter_parts/` reports no warnings.
- [x] AC-02: `python -m pytest -q` passes (158 tests).
- [x] AC-03: `./project/governance-check.sh` GOV-PASS.

## Changelog

- Extracted shared helpers into `common.py`; refactored the five flagged
  functions to table-driven dispatch + per-record evidence builders.
- Restored `SUMDAdapter.normalize` verbatim (not flagged; kept as-is).
