# Ticket 021: Pin Docker base image to immutable SHA-256 digest

- **ID**: ticket-021
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-20

## Goal and scope

Update `Dockerfile` to pin `python:3.12-alpine` to an immutable SHA-256 digest,
ensuring hermetic and reproducible container builds conformant with `GOV-DOCKER-002`.

## Acceptance criteria

- [x] AC-01: `Dockerfile` uses an immutable `python:3.12-alpine@sha256:...` base reference.
- [x] AC-02: The deterministic governance gate passes.
- [x] AC-03: The test suite passes.

## Result

Ticket 021 closed from integrated evidence:
- PR #22 approved at `ed0457b5a0d5c8a465ac869b97278bef0a7f9402` (Decision `D-021-4597`), merged as `e2fcddbc3a7abe52cc06dd46336fcc10920052f0`.
- Branch `agent/docker-pin-021` deleted upon merge.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
