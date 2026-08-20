# Ticket 018: Release preparation: bump VERSION to 0.1.0 and configure pyproject.toml

- **ID**: ticket-018
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-08-20

## Goal and scope

Bump the project VERSION file from `0.0.0` to `0.1.0` reflecting the completed
Phase 0 through Phase 4 implementation (source adapters, deterministic comparator,
CLI, and reasoning consumer integration).
Provide a declarative `pyproject.toml` definition according to PEP 621 / standard
packaging with `jsonschema>=4.26.0` dependency and CLI entry point.

## Acceptance criteria

- [x] AC-01: `VERSION` is set to `0.1.0`.
- [x] AC-02: `pyproject.toml` is created with package metadata, dependencies, and `data2dsl` CLI script entrypoint.
- [x] AC-03: The deterministic governance gate passes.
- [x] AC-04: The full test suite passes.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
