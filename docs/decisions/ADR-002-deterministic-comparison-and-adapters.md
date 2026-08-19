# ADR-002: Deterministic Comparison Engine and Source Adapters

- **Status:** Accepted
- **Date:** 2026-08-19
- **Decision owner:** `data2dsl` ticket-009
- **Related tickets:** ticket-004, ticket-007, ticket-008

## Context and Decision Question

How does `data2dsl` acquire, normalize, and deterministically compare observations across disparate sources (e.g. Markdown documents, GitHub API, code analyzers) while maintaining complete cryptographic evidence provenance and avoiding reasoning or LLM entanglement?

## Decision

`data2dsl` adopts an evidence-first, three-stage factual comparison architecture:

1. **Source Adapters (`src/data2dsl_adapters.py`):**
   - Thin, read-only adapters for external tools (`subactor/diagit` for GitHub commit metrics, `semcod/mdflow` for Markdown structural facts, `code2logic`/`code2schema` for code analysis).
   - Normalize source outputs into `autogrammar.data2dsl/observation/v0` envelopes with explicit `subject`, `metric`, `window`, and `state` (`OBSERVED`, `UNEVALUABLE`).
   - Every observation includes non-empty `evidence` records carrying `digest_sha256`, `source_revision`, `media_type`, `extractor`, and structured `location`.

2. **Deterministic Comparator (`src/data2dsl_comparator.py`):**
   - Strictly effect-free and deterministic.
   - Evaluates comparison policy against canonical scalar/set values.
   - Emits exactly one of five outcomes: `MATCH`, `CONFLICT`, `MISSING_LEFT`, `MISSING_RIGHT`, or `UNEVALUABLE`.
   - Produces typed deltas (e.g. `right - left` for integers, symmetric difference sets for string-sets).
   - Aggregates and lexicographically sorts all evidence references.

3. **Reasoning Boundary:**
   - `data2dsl` owns only factual acquisition, normalization, and difference computation.
   - Downstream consumers (such as `semcod/todo2code` or policy engines) retain full ownership of higher-level reasoning, diagnostics, and mutations.

## Consequences

- **Determinism:** Given identical queries and source inputs, `data2dsl` outputs are bit-for-bit reproducible and mathematically verifiable.
- **Fail-Closed Validation:** All bundles pass deterministic JSON Schema and semantic rules without host network access.
- **Modularity:** New data sources are integrated by adding lightweight adapters without modifying comparator core logic or upstream contracts.
