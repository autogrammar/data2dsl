# Phase 0 capability map

Date: 2026-08-13
Scope: discovery and governance only; no product implementation or final DSL.

## Decision rules

The inventory uses current repository contents as evidence and prefers, in
order: `REUSE`, `EXTRACT`, `EXTEND`, then `MISSING`. `CANDIDATE` means that a
component is relevant but its stability or fit is not yet sufficient for an
integration decision. `REJECTED` means that the inspected component does not
provide the claimed generic capability; it is not a judgment on that product's
own domain.

The scan covered the current top-level repositories under `semcod/*` (78 Git
repositories), `subactor/*` (60), and `wellmanifest/*` (15). Repository
metadata and READMEs were used for broad candidate discovery. A candidate was
classified only after checking its current package/CLI surface, implementation
and tests. Paths below are organization-relative and revisions make the
evidence reproducible. README-only or roadmap-only claims are not treated as
implemented capability.

## Capability inventory

| Capability | Repo | File / CLI / API | Input | Output | Coupling | Evidence | Status | Integration |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Immutable project governance | `wellmanifest/new-project` | public Goal `governance adopt`; adopted `.governance/manifest.json` and lock | published tag and immutable revision | governed repository carrier and deterministic gate | governance-only; no product runtime | published `v0.16.2`, peeled revision `63a03d0c2ec417f8eab9a6edb3c4ed654937a1ac`; local adoption lock | **REUSE** | Keep as development governance; never import into product runtime. |
| Markdown structural acquisition | `semcod/mdflow` | Python `MdFlow.parse`, `parse_text`, `parse_dir`, `scan`; CLI `mdflow` | Markdown text, file, or directory | structured document facts: headings, links, fences, tables and list items | Python >=3.11; package also declares development/tooling dependencies, but parser implementation is separable | `mdflow/__init__.py`, `mdflow/parser.py`, `tests/`; revision `f87c89ddfca7f95a29ccbb19c8d47bbb0ada6b32` | **REUSE** | Use the public parser/scan API through a thin source adapter; keep metric meaning in data2dsl mapping. |
| TODO/CHANGELOG intent extraction | `semcod/todo2code` | TS `extractMarkdownIntent` | TODO and CHANGELOG Markdown files plus `T2CConfig` | `IntentRecord[]` | deliberately limited to TODO/CHANGELOG; tied to todo2code config and Intent DSL | `src/extractors/markdown.ts`, `test/markdown.test.ts`, exports in `src/index.ts`; revision `fb05e99e50c5fd20f911423c0ffd2416a7688378` | **REUSE** | Consume only when the requested result is todo2code Intent; do not advertise as generic Markdown parsing. |
| Git factual acquisition | `semcod/todo2code` | private `runGit`, `readCommits`, `readChangedFiles`, `readStats` inside `extractGitIntent` | local Git repository and revision range | commit, changed-file, numstat and diff facts before intent mapping | private helpers are fused to `T2CConfig`, text inference and `IntentRecord` construction; npm package is `private` | `src/extractors/git.ts`, `test/git.test.ts`, `package.json`; revision `fb05e99e50c5fd20f911423c0ffd2416a7688378` | **EXTRACT** | In a later ticket, move the smallest factual Git seam to a shared TS package without semantic changes; todo2code keeps intent mapping. No TypeScript-to-Python rewrite. |
| Git-to-intent mapping | `semcod/todo2code` | public TS `extractGitIntent` | Git history plus todo2code configuration | epistemic `commit_intent_claim` records | intentionally coupled to todo2code Intent semantics and inference | `src/extractors/git.ts`, `src/index.ts`, `test/git.test.ts` | **REUSE** | todo2code remains the owner and consumer; data2dsl should not duplicate this mapping. |
| JSON/YAML/TOML/config structural extraction | `semcod/todo2code` | public TS `extractConfigurationIntent`; internal format parsers | repository configuration files | configuration-derived `IntentRecord[]` | discovery, ignore rules and output construction are todo2code-specific; YAML/TOML handling is heuristic, not a general parser promise | `src/extractors/configuration.ts`, `test/configuration.test.ts`, `src/index.ts` | **EXTRACT** | Extract only proven neutral structure-reading functions if a second consumer needs them; keep discovery and intent mapping in todo2code. Prefer standard parsers where exact semantics are required. |
| Multi-language code fact extraction | `semcod/todo2code` | public TS `extractAstIntent` | TS/JS, Python, Go, Java, Rust and PHP sources plus config | code-derived `IntentRecord[]` | cache, schema and output are todo2code-specific; package is private | `src/extractors/ast.ts`, AST tests, `src/index.ts` | **EXTRACT** | Extract stable language facts only if direct package reuse cannot be made available; retain identical TypeScript behavior and add compatibility tests later. |
| Python control/data/call-flow analysis | `semcod/code2logic` | Python API and `code2logic` CLI | Python project/source | CFG, DFG and call-graph analysis | Python-only; its own analysis model and dependencies | `code2logic/__init__.py`, CLI entry in `pyproject.toml`, `tests/`; revision `ba93489b56f51af31206671a1f55ab860bb725c2` | **REUSE** | Optional language-specific analyzer adapter; do not generalize its Python contract. |
| Python semantic/CQRS/schema analysis | `semcod/code2schema` | Python `extract_project`, `analyze`; CLI | Python project/source | semantic entities, API/CQRS/schema and graph representations | Python-specific; DFG is roadmap, not current evidence | package exports, `pyproject.toml`, `tests/`; revision `5a34e88ad962815247007c904b172ee9d7d6d175` | **REUSE** | Optional semantic-schema adapter when those outputs are requested. |
| Natural language to structured intent | `semcod/nlp2dsl` (`nlp2cmd-intent`) | Python `analyze_query`, `IntentPipeline`; `IntentIR` | natural-language query | `nlp2cmd.intent_ir.v1` plus optional execution plan | current vocabulary and target kinds are command/intent oriented, not a proven source/metric/time-window data query contract | `packages/nlp2cmd-intent/src/nlp2cmd_intent/input.py`, `facade.py`, `packages/pact-ir/src/pact_ir/intent.py`, `test_analyze_query.py`; revision `80fb9081462cbd54164a027c3a5a6b0db5cdc7be` | **EXTEND** | Extend the existing IR vocabulary through its owning repo after the data-query profile is agreed; do not create a parallel NLP parser. |
| Intent-graph comparison | `semcod/todo2code` | public TS `diffIntentGraphs` | two validated todo2code `IntentGraph` values | stable intent-graph diff | specific to todo2code graph schema, not arbitrary observations | `src/graph/diff.ts`, graph diff tests, `src/index.ts` | **REUSE** | Use unchanged for IntentGraph comparisons only. |
| Workspace intent trend | `semcod/todo2code` | public `compareWorkspaceIntent` | base Git worktree and current workspace | coverage/reality/diagnostic trend | executes the full todo2code pipeline and optional LLM deadlines | `src/comparison/workspace.ts`, workspace comparison tests | **REUSE** | Keep as a todo2code consumer-layer analysis; not the data2dsl generic comparator. |
| Generic arbitrary-observation regression engine | `semcod/rebuild`, `semcod/regres` | database/code-evolution snapshots; `regres.defscan` and doctor orchestration | database/code revisions or source definitions | domain snapshots, timelines, similarity and diagnostics | tied to database evolution, code definitions, pages and Git history | `rebuild/application/services/db_snapshot_manager.py`, `rebuild/domain/timeline.py`, `regres/defscan.py`, `regres/doctor_orchestrator.py`, corresponding tests; revisions `b4588ef2190249d030ed2d28ee9f0f57c39072a2`, `79c37e762039d86e00a76fc8d5437216c9f890e5` | **REJECTED** | Reuse these products only in their domains. They do not remove the need for neutral comparability and metric-diff logic. |
| GitHub repository topology acquisition | `subactor/diagit` | Python `GitHubProvider`, `GitHubCliProvider` using `gh` GraphQL | GitHub organization/repository identity | repository snapshot with default branch, archived flag, branches, open PRs and findings | GitHub CLI/auth boundary; protobuf snapshot model; does not return commit metrics | `src/diagit/infrastructure/github.py`, `tests/test_remote_control.py`; revision `f4fdfd958b21904c0e26ec6ffa98841644ee9117` | **REUSE** | Reuse provider/auth/pagination boundary for supported topology facts. |
| GitHub commit/metric acquisition | `subactor/diagit` | no current provider operation for commit counts/actors/time windows | repository, metric, actor and time range | normalized metric observation with evidence | closest existing provider lacks the required query; `subactor/github-com` is an Actions orchestrator/mock, not a backend client | Diagit provider and tests above; `subactor/github-com/README.md`, mock GraphQL tests at revision `bc1b98c31f662bb31036bdcbb2b6df1bba568378` | **EXTEND** | Add the smallest read-only, paginated operation to Diagit's provider contract in a separate approved ticket; do not create a second GitHub client. |
| Observation and evidence envelope | `subactor/twin` | protobuf `subactor.twin.v1.Observation`, `EvidenceRef`; standard validator/generator | metric, target URI, value, time, status and evidence refs | typed protobuf observation/evidence envelope | digital-twin aggregate semantics; package `0.1.0.dev0`; standard/profile is still under review | `proto/twin/v1/twin.proto`, `spec/TWIN_STANDARD.md`, `profiles/generic-twin.json`, `src/twin_standard.py`, tests; revision `6e53bc33a219d6a99b480e3203d40352ff63ce5f` | **CANDIDATE** | Run a compatibility decision with the standard owner before defining a data2dsl envelope. Reuse if generic values and provenance fit without weakening twin invariants. |
| DSL manifest conformance | `wellmanifest/dsl` | dependency-free `src/dsl_check.py`; `wellmanifest.dsl/manifest/v1` JSON Schema | DSL manifest/bundle | deterministic conformance diagnostics | standard is a pre-stable normative draft; domain profiles are not yet delivered | `spec/DSL_STANDARD.md`, `schemas/dsl-manifest.schema.json`, `src/dsl_check.py`, self-test, `TODO.md`; revision `550e5f441c709e15f2679c1af151352d1eba2f1e` | **REUSE** | Use the checker for manifest conformance once a profile exists; pin the revision. Do not treat the draft as the data model itself. |
| Shared data-query/result DSL profile | `wellmanifest/dsl` | planned domain profile; no current schema | source/metric/window query and comparison result | portable query/result contract | profile is explicitly pending in TODO; base standard does not define observation comparison semantics | `TODO.md`, `spec/DSL_STANDARD.md`, `schemas/dsl-manifest.schema.json` | **MISSING** | Propose the minimal profile to the owning standard in a later governance ticket. Until accepted, keep any experiment provisional and local. |
| Browser/web acquisition | `semcod/curllm` | browser automation, BQL parser/executor and CLI | browser/web query | browser-derived data/automation result | browser and LLM/BQL domain, not a neutral data-query planner | BQL/parser/executor modules, tests, `pyproject.toml`; revision `b9d2b570f3ca0efaef8c97014382f10104dc9752` | **REUSE** | Source adapter `CurllmAdapter` implemented in `src/data2dsl_adapters.py`. |
| SDLC Task queue acquisition | `semcod/planfile` | YAML task queue, ticket metadata | planfile task/ticket list | normalized ticket counts, task IDs and status observations | planfile project schema | `planfile.yaml`, parser/tests | **REUSE** | Source adapter `PlanfileAdapter` implemented in `src/data2dsl_adapters.py`. |
| Infrastructure topology acquisition | `semcod/deta` | Docker compose / OpenAPI manifests | infrastructure topology description | normalized service counts, port sets, endpoint lists | container/infra YAML/JSON | `deta.build_topology()`, compose parser | **REUSE** | Source adapter `DetaAdapter` implemented in `src/data2dsl_adapters.py`. |
| Intent contract bounds acquisition | `subactor/intent-contract-dsl` | Intent contract JSON DSL | contract definitions | normalized parties, deliverables, and obligations | subactor contract schema | `intent-contract.dsl.json` | **REUSE** | Source adapter `IntentContractAdapter` implemented in `src/data2dsl_adapters.py`. |
| OQL scenario & sensor telemetry acquisition | `oqlos/*` / `data2dsl` | `OqlTelemetryAdapter` in `src/data2dsl_adapters.py` | OQL scenario manifests and sensor telemetry logs | normalized sample rates, thermal ceilings, throughput, and active pinouts | embedded/sensor scenario domain | `src/data2dsl_adapters.py`, `tests/test_oql_adapter.py` | **IMPLEMENTED** | Normalized observations with `oqlos.telemetry` extractor and cryptographic SHA-256 evidence. |
| URI workflow routing | `if-uri/urirun` | `connector.manifest.json`, `urirun.bindings` | `data2dsl://` URI commands | execution results with typed envelopes | if-uri connector specification | `src/connector.manifest.json`, `src/data2dsl_skill.py` | **REUSE** | Implemented `urirun_bindings` for `data2dsl://host/compare/run` and `data2dsl://host/selftest/run`. |
| Model Context Protocol (MCP) | `semcod/mcp` | MCP JSON-RPC 2.0 STDIO protocol | tool call requests (`data2dsl_compare`, `data2dsl_self_test`) | tool call results with text contents | MCP 2024-11-05 spec | `src/data2dsl_skill.py` (`handle_mcp_message`, `main_mcp`) | **REUSE** | Native IDE MCP tool discovery and execution. |
| SUMD structured-document parsing | `semcod/sumd` | Python `parse`, `parse_file` | SUMD-conformant Markdown | SUMD descriptor model and validation | SUMD-specific, not arbitrary Markdown | package exports, parser/tests; revision `672c699db6110b678260ccd729617e0b5772a6f0` | **REUSE** | Use only when the declared source format is SUMD; otherwise use mdflow. |
| Generic comparability and metric diff | `data2dsl` | `DeterministicComparator` in `src/data2dsl_comparator.py` | two normalized observations plus comparison policy | `MATCH`, `CONFLICT`, `MISSING_LEFT`, `MISSING_RIGHT`, `UNEVALUABLE`, deltas (`integer`, `float`, `percentage`, `string-set`) and evidence | deterministic comparator | `src/data2dsl_comparator.py`, `tests/` | **IMPLEMENTED** | Supported scalar and set types: `integer`, `string`, `string-set`, `float`, `percentage`. |
| Golden-case work-summary mapping | `data2dsl` | `WorkSummaryMarkdownAdapter` + `GitHubDiagitAdapter` | structured Markdown claims and GitHub metric observations | aligned metric keys, actors, windows and provenance | product glue | `src/data2dsl_adapters.py`, tests | **IMPLEMENTED** | Complete golden-case flow with SHA-256 evidence chains. |
| Reasoning and conclusion layer | `semcod/todo2code` | diagnostics/conclusion and optional LLM pipeline | factual IntentGraph/diff/evidence | diagnoses and conclusions | consumer policy and epistemic intent model | `src/graph/linker.ts`, diagnostics/conclusion modules and tests | **REUSE** | Keep outside data2dsl. data2dsl returns facts, deltas and evidence; todo2code remains a consumer. |
| Doctor Diagnostic Profile Formatter | `subactor/doctor-agent` / `data2dsl` | `DiagnosticProfileFormatter` in `src/data2dsl_doctor.py`, CLI `feed-doctor` | comparison bundle | prioritized symptoms, severity classification (`CRITICAL`..`INFO`), SHA-256 evidence | diagnostic triage feed | `src/data2dsl_doctor.py`, `tests/test_doctor_feed.py` | **IMPLEMENTED** | Transforms comparison discrepancies into prioritized diagnostic profiles for doctor-agent. |
| Koru Remediation Intent Formatter | `semcod/koru` / `data2dsl` | `RemediationIntentFormatter` in `src/data2dsl_remediation.py`, CLI `feed-koru` | comparison bundle | structured `remediation-intent/v1` actions (`synchronize_metric`, `restore_missing_entries`, `resolve_conflict`) | closed-loop remediation feed | `src/data2dsl_remediation.py`, `tests/test_remediation_feed.py` | **IMPLEMENTED** | Maps deltas and conflicts to machine-actionable repair intents for koru closed-loop self-healing. |

## Extraction boundaries

`EXTRACT` is intentionally narrow. It authorizes no Phase 0 code movement.
Later extraction must preserve the existing language and behavior, move the
smallest neutral factual seam, keep todo2code's semantic mapping in todo2code,
and prove 1:1 compatibility with fixtures from the original tests. The first
candidate is Git factual acquisition; configuration and AST facts follow only
if an actual second consumer demonstrates that a shared package is better than
calling the existing public API.

## Genuine gaps and ownership

The missing pieces are narrower than a new framework:

1. A shared data query/result profile has no implemented owner artifact yet.
   `wellmanifest/dsl` is the proper standards route; `subactor/twin` is a
   concrete compatibility candidate for observations and evidence.
2. Deterministic comparability and metric diff across two neutral observations
   is supplied by `data2dsl_comparator.py`.
3. GitHub commit metrics extend Diagit's established provider and auth
   boundary.
4. The golden-case Markdown-to-metric mapping is implemented in `WorkSummaryMarkdownAdapter`.
5. Autonomous agent feeds are provided by `data2dsl_doctor.py` (`doctor-agent` triage) and `data2dsl_remediation.py` (`koru` self-healing).

## Composition graph

```mermaid
flowchart LR
    Q["User / Agent / MCP / urirun Query"] --> R["data2dsl Routing & Normalization"]

    R --> M["mdflow / WorkSummaryMarkdownAdapter"]
    R --> H["GitHub / DiagitCommitMetricResponse"]
    R --> L["code2logic CFG/DFG Adapter"]
    R --> S["code2schema CQRS Adapter"]
    R --> B["curllm Browser BQL Adapter"]
    R --> P["planfile Task Queue Adapter"]
    R --> D["deta Infra Topology Adapter"]
    R --> I["subactor IntentContract Adapter"]
    R --> OQL["oqlos OQL Telemetry Adapter"]

    M --> O["Normalized Observations (observation/v0)"]
    H --> O
    L --> O
    S --> O
    B --> O
    P --> O
    D --> O
    I --> O
    OQL --> O

    O --> C["DeterministicComparator (int/float/pct/set)"]
    C --> F["Comparison Bundle (result/v0 + SHA-256 Evidence)"]

    F --> X["todo2code / pyqual (Reasoning Fact Feed)"]
    F --> DOC["doctor-agent (Diagnostic Profile Feed)"]
    F --> KORU["semcod/koru (Remediation Intent Feed)"]
```

## Current state conclusion

The product serves as a lightweight, evidence-preserving composition and
normalization layer. All 9 source adapters normalize domain facts into
verifiable observations, the deterministic comparator supports integer,
float, percentage, string, and set comparisons with full cryptographic
provenance, and specialized feeds project discrepancies into consumer feeds
for `todo2code`, `doctor-agent`, and `koru` closed-loop self-healing.

