# Ticket 021: Pin Docker base image to immutable SHA-256 digest

- **ID**: ticket-021
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-08-20

## Goal and scope

Update `Dockerfile` to pin `python:3.12-alpine` to an immutable SHA-256 digest,
ensuring hermetic and reproducible container builds conformant with `GOV-DOCKER-002`.

## Acceptance criteria

- [x] AC-01: `Dockerfile` uses an immutable `python:3.12-alpine@sha256:...` base reference.
- [x] AC-02: The deterministic governance gate passes.
- [x] AC-03: The test suite passes.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
