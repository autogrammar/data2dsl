# Ticket 100: Split large modules batch/cli/discovery/skill into cohesive submodules

- **ID**: ticket-100
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

Split cohesive parts out of the four large flat modules while keeping the
original module names as backward-compatible facades:

- `data2dsl_batch` -> markdown rendering helpers extracted to `data2dsl_batch_report`
  (`format_markdown_report` re-exported from `data2dsl_batch`).
- `data2dsl_cli` -> command handlers extracted to `data2dsl_cli_commands`
  (`_COMMAND_HANDLERS` dispatch imported by `data2dsl_cli`).
- `data2dsl_discovery` -> graph builder internals extracted to
  `data2dsl_discovery_graph`; `discover_data_network` and `DiscoveryError`
  remain importable from `data2dsl_discovery`.
- `data2dsl_skill` -> MCP stdio transport (`handle_mcp_message`, `main_mcp`)
  extracted to `data2dsl_skill_mcp` with lazy skill import (no cycle);
  normalizer dispatch already lives in `data2dsl_skill_norms` (ticket-099).

Wheel `py-modules` declarations for the new modules landed via companion
integration ticket-101 (shared contract path owned by integration workstream).

Verified: `./project/governance-check.sh` GOV-PASS, `python -m pytest -q`
158 passed, `lizard -C 15 src/` zero warnings.

## SESSION_EXECUTION_AUTHORIZATION

User requested autonomous execution of all queued tickets; recorded per AGENTS rule 4.
