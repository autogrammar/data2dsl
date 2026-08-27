# ADR-007: Subactor Delegation Envelope Conformance & Closed-Loop Self-Healing

- **Status:** Accepted
- **Date:** 2026-08-27
- **Decision owner:** `data2dsl` ticket-051 / ticket-052 / ticket-053
- **Related tickets:** ticket-043, ticket-044, ticket-045, ticket-051, ticket-052, ticket-053

## Context and Decision Question

The `wellmanifest/how-to-use-subactor` specification defines a normative protocol for how humans and LLM supervisors delegate goals, monitor runtime evidence, and enact bounded self-healing loops with autonomous actors.

Under this model:
1. Delegation occurs over a standardized semantic envelope (`ROLE`, `GOAL`, `SCOPE`, `ACCEPTANCE`, `AUTHORITY`, `LIMITS`, `REPORT`).
2. Self-healing operates via a closed loop:
   $$\text{DETECT} \longrightarrow \text{PLAN} \longrightarrow \text{EXECUTE} \longrightarrow \text{VERIFY} \longrightarrow \text{HEAL}$$
3. Models (SubLLM) provide advisory reasoning, while execution authority derives strictly from policy grants and immutable SHA-256 evidence digests.

How should `data2dsl` integrate with this protocol to enable deterministic envelope validation, MCP/urirun tool dispatch, and verification of closed-loop repairs?

## Decision

1. **Subactor Delegation Envelope Module (`src/data2dsl_subactor.py`):**
   - **`SubactorDelegationEnvelope`**: Structured dataclass for envelope representations across text and JSON formats.
   - **Deterministic Error Codes**:
     - `COMM-ENVELOPE-001`: Missing required field.
     - `COMM-ROLE-001`: Invalid actor role (permitted: `founder`, `supervisor`, `observer`).
     - `COMM-AUTH-001`: Invalid authority level (permitted keywords: `observe`, `plan`, `dry-run`, `apply`).
   - **`simulate_self_healing_cycle()`**: Encapsulates 5-stage verification linking `DeterministicComparator`, `DiagnosticProfileFormatter` (symptom triage), and `RemediationIntentFormatter` (actionable repair intents).

2. **SUMD Structured Document Adapter (`SUMDAdapter` in `src/data2dsl_adapters.py`):**
   - Implements factual table parsing and descriptor block extraction for SUMD (Structured Unified Markdown Document) specifications as the 10th normalized observation source.

3. **Tool Surface & MCP Protocol (`src/data2dsl_skill.py`):**
   - Exposes `data2dsl_validate_envelope` and `data2dsl_simulate_healing` via MCP JSON-RPC 2.0 and `urirun` routes (`data2dsl://host/subactor/validate`, `data2dsl://host/healing/simulate`).

## Consequences

- **Strict Protocol Conformance:** Any supervisor or agent consuming `data2dsl` can validate its delegation envelopes before taking action.
- **Auditable Self-Healing:** The closed-loop verification pipeline provides reproducible mathematical guarantees that a proposed repair truly eliminated discrepancies and satisfied acceptance criteria.
- **Seamless Tool Integration:** IDEs and LLM supervisors running on Claude, Cursor, Windsurf, or Subactor can invoke envelope validation and healing simulation natively over STDIO MCP.
