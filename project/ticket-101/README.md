# Ticket 101: Declare new data2dsl split modules in wheel py-modules

- **ID**: ticket-101
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-09-18

## Goal and scope

To be completed from human-owned input.

## Acceptance criteria

- [ ] AC-01: Scope is approved by a human owner.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.

## Implementation notes

Added `data2dsl_batch_report`, `data2dsl_cli_commands`, `data2dsl_discovery_graph`,
`data2dsl_skill_mcp` and the previously undeclared `data2dsl_skill_norms` to
`tool.setuptools.py-modules` so the wheel ships every local runtime import
referenced by ticket-100 module splits.

## SESSION_EXECUTION_AUTHORIZATION

User requested autonomous execution of all queued tickets; recorded per AGENTS rule 4.
