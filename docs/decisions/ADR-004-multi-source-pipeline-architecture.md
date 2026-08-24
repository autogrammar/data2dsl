# ADR-004: Multi-Source Verification Pipeline Architecture

- **Status:** Accepted
- **Date:** 2026-08-24
- **Decision owner:** `data2dsl` ticket-040
- **Related tickets:** ticket-019, ticket-022, ticket-034, ticket-037, ticket-038, ticket-039, ticket-040

## Context and Decision Question

As `data2dsl` expands from single-pair comparisons (`work-summary.md` vs GitHub commits) to multi-source evidence acquisition across code analyzers (`code2logic`, `code2schema`), task queues (`semcod/planfile`), topology analyzers (`semcod/deta`), contractual bounds (`subactor/intent-contract-dsl`), and quality loop checkers (`semcod/pyqual`), how should these disparate pipelines be orchestrated and exposed to autonomous agents?

## Decision

`data2dsl` adopts an open, decoupled, adapter-centric verification architecture with three integration tiers:

1. **Normalized Source Adapters (`autogrammar.data2dsl/observation/v0`):**
   - Each external tool or domain repository is wrapped in a dedicated, stateless source adapter (`src/data2dsl_adapters.py`).
   - Every adapter normalizes domain payloads into a uniform observation envelope with immutable SHA-256 evidence digests, exact source line/endpoint locations, and extractor metadata.
   - Currently supported adapters:
     - **`WorkSummaryMarkdownAdapter`** (`semcod/mdflow`): Markdown claims.
     - **`GitHubDiagitAdapter`** (`subactor/diagit`): GitHub API / Diagit commit metrics.
     - **`Code2LogicAdapter`** (`semcod/code2logic`): CFG/DFG call flows and complexity.
     - **`Code2SchemaAdapter`** (`semcod/code2schema`): Entity models and CQRS schemas.
     - **`CurllmAdapter`** (`semcod/curllm`): Browser BQL facts.
     - **`PlanfileAdapter`** (`semcod/planfile`): SDLC task queues and ticket statuses.
     - **`DetaAdapter`** (`semcod/deta`): Infrastructure topologies, services, and ports.
     - **`IntentContractAdapter`** (`subactor/intent-contract-dsl`): Parties, obligations, and deliverables.

2. **Deterministic Multi-Type Comparison Engine:**
   - `DeterministicComparator` compares observations without heuristics or LLM evaluation.
   - Supported scalar and set types: `integer`, `string`, `string-set`, `float`, `percentage`.
   - Produces canonical comparison bundles with typed deltas and sorted evidence references.

3. **Multi-Protocol Agent & Pipeline Interoperability:**
   - **`Data2DslSkill`** (`wellmanifest.skills/v1`): Programmatic Python API for internal agents.
   - **`urirun` Connector** (`if-uri/urirun`): Exposes `data2dsl://host/compare/run` and `data2dsl://host/selftest/run` for URI-driven workflow orchestration.
   - **Model Context Protocol (MCP)**: Implements JSON-RPC 2.0 STDIO protocol for native agent tool discovery in Cursor, Windsurf, and Claude Desktop.

## Consequences

- **Extensibility:** New data sources can be integrated simply by adding an adapter without modifying comparator logic.
- **Agent Interoperability:** Any LLM agent with MCP or URI support can verify code claims deterministically.
- **Auditability:** Every comparison decision is backed by cryptographic SHA-256 evidence and line-precise provenance.
