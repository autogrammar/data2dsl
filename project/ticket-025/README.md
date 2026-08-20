# Ticket 025: Implement data2dsl agent skill and tool interface

- **ID**: ticket-025
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-08-20

## Goal and scope

Implement `src/data2dsl_skill.py` providing a standardized programmatic skill / MCP tool
interface for AI agents conforming to the `wellmanifest/skills` specification.
The skill exposes `compare_observations(query_or_path, left_path, right_path, ...)` and
`self_test()` with structured output dictionaries and standard error diagnostics.

## Acceptance criteria

- [x] AC-01: `src/data2dsl_skill.py` provides `Data2DslSkill` with standardized tool definitions and invocation methods.
- [x] AC-02: Unit tests in `tests/test_cli.py` verify skill execution and error handling.
- [x] AC-03: The deterministic governance gate passes.
- [x] AC-04: The full test suite passes.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
