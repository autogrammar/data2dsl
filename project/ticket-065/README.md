# Ticket 065: Robust deserialization of nested dict structures in skill normalize_raw (F07)

- **ID**: ticket-065
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-28

## Goal and scope

Fix audit finding F07:
When raw data is passed into `data2dsl_skill._normalize_raw` from JSON/MCP payloads, nested collections (such as `tickets` in Planfile, `pages` in Curllm/Diagit, `services` in Deta) arrive as plain Python `dict`s rather than typed dataclasses.
Add robust deserialization in `_normalize_raw` so dicts are converted into their respective dataclasses (`PlanfileTicketEvidence`, `CurllmPageEvidence`, `DetaServiceEvidence`, `DiagitPageEvidence`) before calling adapter `normalize`.

SESSION_EXECUTION_AUTHORIZATION recorded from user prompt.

## Acceptance criteria

- [x] AC-01: Scope is approved (SESSION_EXECUTION_AUTHORIZATION recorded).
- [x] AC-02: `_normalize_raw` converts raw nested `dict`s to typed evidence dataclasses for Planfile, Curllm, Deta, and GitHub.
- [x] AC-03: MCP tool execution and direct skill calls with nested JSON payloads succeed without `AttributeError`.
- [x] AC-04: Unit tests in `tests/test_skill_raw_deserialization.py` verify deserialization of dict payloads.
- [x] AC-05: Full pytest suite passes (115/115) and `governance-check.bat` reports GOV-PASS.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
