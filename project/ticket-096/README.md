# Ticket 096: Ignore generated runtime and analysis artifacts

- **ID**: ticket-096
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
Add ignore rules for generated runtime state (`.planfile/`, `.koru/`,
`.planfile_analysis/`), code2llm scan artifacts under `project/`, and
`*.egg-info/` byproducts. These files mutate continuously during autonomous
lane operation and previously forced `GOV-WORK-START-001` pending-delta blocks
on every allocation.

## Outcome

- `.gitignore` extended with runtime/analysis ignore rules.
- Delivery: working tree stays clean; allocations unblocked.
