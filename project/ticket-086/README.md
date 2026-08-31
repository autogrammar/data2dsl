# Ticket 086: Audit P1.2 feeds: Doctor and remediation fallback defaults and discovery typing

- **ID**: ticket-086
- **Owner**: gemini (SESSION_EXECUTION_AUTHORIZATION)
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-31
- **Workstream**: application

## Goal and scope

Enhance feeds and typing:
- Supply fallback subject/metric structures when `observations` are empty in `data2dsl_doctor.py` and `data2dsl_remediation.py`
- Avoid schema errors on bare `{"outcome": "MATCH"}` outputs
- Annotate `entity_node` in `data2dsl_discovery.py` for mypy strict compliance

## Acceptance criteria

- [x] AC-01: SESSION_EXECUTION_AUTHORIZATION recorded
- [x] AC-02: Feed tests pass
- [x] AC-03: Governance check passes

## Participants

- Human participant: USER (session authorization)
- Agent participant: [ai-gemini.md](ai-gemini.md)
