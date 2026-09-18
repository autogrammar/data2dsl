# Ticket 098: Reduce CC in doctor/comparator/generator/subactor/discovery

- **ID**: ticket-098
- **Owner**: agent
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-09-18

## Goal and scope

Reduce cyclomatic complexity to <=15 (regix `cc_max`) in:

- `data2dsl_doctor.py`: `_calculate_severity_and_magnitude` (CC 25),
  `format_profile` (CC 36)
- `data2dsl_comparator.py`: `_is_compatible` (CC 22)
- `data2dsl_generator.py`: `generate_query_template` (CC 17)
- `data2dsl_subactor.py`: `validate_delegation_envelope` (CC 17)
- `data2dsl_discovery.py`: `discover_data_network` (CC 22) incl. nested
  `walk` (CC 17)

Approach: threshold tables (`_CONFLICT_THRESHOLDS`), field/section check
tables, payload coercion + per-field validators, a `_GraphBuilder`
context with module-level `_walk`/`_walk_dict_entry`/`_walk_list_entry`,
and `_filter_by_query`/`_severity_summary` extraction. Public signatures
and output shapes are unchanged.

`data2dsl_batch.py`, `data2dsl_cli.py`, `data2dsl_skill.py`,
`data2dsl_remediation.py` and `data2dsl_contract_v0/validate.py`
violations remain for a follow-up slice (outside allowedPaths).

## Acceptance criteria

- [x] AC-01: `lizard -C 15` reports no warnings on the five touched files.
- [x] AC-02: `python -m pytest -q` passes (158 tests).
- [x] AC-03: `./project/governance-check.sh` GOV-PASS.

## Changelog

- doctor: threshold-table severity mapping; per-bundle symptom builder.
- comparator: section/field compatibility table.
- generator: `_default_unit`, `_resolve_equality`, `_resolve_window`.
- subactor: `_coerce_envelope_payload`, `_extract_required_fields`,
  `_check_role`, `_check_authority`.
- discovery: `_GraphBuilder`, module-level walkers, `_validated_source`,
  `_filter_by_query`.
