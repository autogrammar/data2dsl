# ADR-003: Natural Language Query Front-End and `semcod/nlp2dsl` Integration

- **Status:** Accepted
- **Date:** 2026-08-20
- **Decision owner:** `data2dsl` ticket-022
- **Related tickets:** ticket-001, ticket-004, ticket-009, ticket-015, ticket-022, ticket-034
- **Technical notes:** [`docs/nlp2dsl-integration-notes.md`](../nlp2dsl-integration-notes.md)

## Context and Decision Question

Users and autonomous agent coordinators frequently formulate comparison intents in natural language (e.g., *"Compare commit claims in work-summary.md against actual GitHub commit counts for week 2026-08-10"*).

How should `data2dsl` support natural language query compilation without compromising its core architectural invariant: **zero runtime LLM dependencies, deterministic effect-free execution, and mathematically verifiable provenance**?

## Decision

`data2dsl` decides to decouple natural language query understanding from the comparison core by delegating natural language compilation to **`semcod/nlp2dsl` (`nlp2cmd-intent`)**:

1. **Outer-Boundary Translation (`semcod/nlp2dsl`):**
   - The upstream `semcod/nlp2dsl` package's `IntentPipeline` / `IntentIR` will be extended with the `autogrammar.data2dsl` comparison query vocabulary (`subject`, `metric`, `window`, `left_source`, `right_source`, `comparison`).
   - The output of the NLP compiler is always a strictly validated, canonical `autogrammar.data2dsl/query/v0` JSON AST.

2. **Core Boundary Invariant:**
   - `data2dsl` itself receives **only** canonical JSON AST query objects conforming to `src/data2dsl_contract_v0/comparison.schema.json`.
   - `data2dsl` **never** embeds prompt engineering, neural weights, LLM API calls, or heuristic parsing within its core comparison engine or source adapters.

3. **Error Routing:**
   - Ambiguous or malformed natural language input is rejected at the `nlp2dsl` boundary before reaching `data2dsl`.
   - If an unexecutable query reaches `data2dsl`, the comparator deterministically returns `UNEVALUABLE` with structured diagnostic evidence.

## Consequences

- **Determinism:** `data2dsl` remains 100% deterministic, offline-capable, and reproducible.
- **Zero Heavy Dependencies:** `data2dsl` core maintains zero LLM SDK runtime dependencies, requiring only `jsonschema`.
- **Modularity:** Upstream query compilers (`nlp2dsl`, CLI flags, web UI, agent tools) can evolve independently without altering comparison contracts or verification suites.
