# Ticket 008: Docker test environment for golden case validation

- **ID**: ticket-008
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-08-19

## Goal and scope

Update `Dockerfile` and `compose.yml` in the `infrastructure` workstream to support building a containerized test environment capable of executing `pytest` and `validate.py --self-test` without host fallback and with network isolation (`network_mode: none`, `read_only: true`).

Out of scope: modifying application source code or external repositories.

## Acceptance criteria

- [x] AC-01: Update `Dockerfile` to install `jsonschema` and `pytest` on `python:3.12-alpine` base.
- [x] AC-02: Configure `compose.yml` with `network_mode: none` and `read_only: true`.
- [x] AC-03: The deterministic governance gate passes.

## Result

Updated `Dockerfile` and `compose.yml`. The test container configuration runs the full test suite and contract self-test in an isolated container.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
