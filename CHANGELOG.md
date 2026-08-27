# Changelog

## Unreleased

### Governance housekeeping

- Close ticket-016 from integrated default branch evidence (ticket-017).
- Close tickets 017–019 from integrated evidence (ticket-020).
- Close tickets 021–022 from integrated evidence (ticket-023).
- Close ticket 025 from integrated evidence (ticket-026).
- Close ticket 027 from integrated evidence (ticket-028).
- Close ticket 028 and update TODO.md, README.md, CHANGELOG.md, and
  project/README.md ticket index (ticket-029).
- Close tickets 029 and 031 from integrated evidence (ticket-032).
- Close tickets 033 and 034 from integrated evidence (ticket-035).
- Sync TODO.md checkboxes for 2026-08-21, update CHANGELOG and README,
  regenerate ticket index (ticket-036).
- Implement multi-source fact adapters Planfile, Deta, and IntentContract (ticket-037).
- Add float and percentage comparison algorithms with schema definitions (ticket-038).
- Expose urirun connector manifest and MCP STDIO server endpoint (ticket-039).
- Document multi-source pipeline architecture in ADR-004 and update CAPABILITY_MAP (ticket-040).
- Author ecosystem integration research notes for koru, diff-dsl, OQL, and doctor-agent (ticket-041).
- Implement Diagnostic Profile Feed `data2dsl_doctor.py` and CLI `feed-doctor` (ticket-043).
- Implement Koru Remediation Intent Generator `data2dsl_remediation.py` and CLI `feed-koru` (ticket-044).
- Author ADR-005 on autonomous agent feedback feeds and update capability map (ticket-045).
- Implement OQL Telemetry Source Adapter for hardware scenario & sensor log normalization (ticket-046).
- Update Capability Map inventory and research notes for OQL telemetry (ticket-047).
- Integrate OQL Telemetry into Data2DslSkill and MCP dispatch (ticket-048).
- Author ADR-006 on OQL telemetry and Hardware-in-the-Loop normalization (ticket-049).
- Synchronize full project documentation and structure runnable examples in `examples/` (ticket-050).
- Implement Subactor delegation envelope validator and closed-loop self-healing E2E pipeline (ticket-051).
- Implement MCP Subactor validation/healing tools and SUMD structured document adapter (ticket-052).
- Author ADR-007 on Subactor conformance, update capability map, and add SUMD example (ticket-053).
- Implement Batch Multi-Query comparison engine and CLI subcommand (ticket-054).
- Implement Query Template Generator and CLI subcommand (ticket-055).
- Implement Markdown report formatting for CLI and batch operations (ticket-056).
- Create Batch Example 08 and synchronize root documentation (ticket-057).

### Batch example 08 & root documentation sync (ticket-057)

- Create `examples/08-batch-multi-query/` runnable example suite for multi-query batch comparison and Markdown report generation.
- Update `examples/README.md` index table with Example 08.
- Synchronize root `README.md` reflecting 10 implemented source adapters, CLI subcommands, and Subactor integration.

### Markdown report formatting (ticket-056)

- Implement `format_markdown_report` in `src/data2dsl_batch.py` rendering structured Markdown tables with status indicators and observation metrics.
- Add `--format` (json | markdown) argument to `data2dsl compare` and `data2dsl batch` CLI subcommands.
- Add test suite in `tests/test_batch_compare.py` (84/84 tests passing).

### Query template generator (ticket-055)

- Implement `generate_query_template` in `src/data2dsl_generator.py` for automated `query/v0` creation across all 10 source adapter kinds.
- Add `data2dsl generate-query` CLI subcommand.
- Add test suite in `tests/test_generator.py` (83/83 tests passing).

### Batch multi-query comparison engine (ticket-054)

- Implement `BatchMultiQueryComparator`, `BatchComparisonSummary`, and `BatchComparisonReport` in `src/data2dsl_batch.py`.
- Add `data2dsl batch` CLI command for multi-query execution with observation matching and clean ratio aggregation.
- Add test suite in `tests/test_batch_compare.py` (79/79 tests passing).

### Subactor conformance architecture & SUMD example (ticket-053)

- Author `docs/decisions/ADR-007-subactor-conformance-and-closed-loop-self-healing.md`.
- Update `docs/CAPABILITY_MAP.md` reflecting 10 implemented source adapters, feed formatters, and MCP/urirun tools.
- Add runnable example `examples/07-sumd-table-comparison/` and update `examples/README.md`.

### MCP Subactor tools & SUMD source adapter (ticket-052)

- Implement `SUMDAdapter` and `SUMDMetricResponse` in `src/data2dsl_adapters.py` for parsing structured markdown tables and descriptor blocks into `Observation` records.
- Extend `Data2DslSkill` in `src/data2dsl_skill.py` with MCP tools `data2dsl_validate_envelope` and `data2dsl_simulate_healing`.
- Add `urirun` routes for Subactor validation and healing simulation (`data2dsl://host/subactor/validate`, `data2dsl://host/healing/simulate`).
- Add comprehensive unit tests in `tests/test_sumd_adapter.py` and extend `tests/test_skill.py` (76/76 tests passing).

### Subactor delegation envelope & closed-loop self-healing (ticket-051)

- Implement `SubactorDelegationEnvelope`, text parser, and field validation (`ROLE`, `GOAL`, `SCOPE`, `ACCEPTANCE`, `AUTHORITY`, `LIMITS`, `REPORT`) in `src/data2dsl_subactor.py` conforming to `wellmanifest/how-to-use-subactor`.
- Implement `simulate_self_healing_cycle` executing 5-stage closed loop `DETECT` -> `PLAN` -> `EXECUTE` -> `VERIFY` -> `HEAL`.
- Add CLI subcommands `validate-envelope` and `simulate-healing` in `src/data2dsl_cli.py`.
- Add unit and E2E test suites in `tests/test_subactor_envelope.py` and `tests/test_self_healing_e2e.py` (67/67 tests passing).
- Add example suite `examples/06-closed-loop-self-healing/` with README and JSON fixtures.

### OQL telemetry source adapter & HIL normalization (tickets 046–049)

- Implement `DEFAULT_OQL_EXTRACTOR`, `OqlScenarioSpecResponse`, `OqlTelemetryLogResponse`, and `OqlTelemetryAdapter` in `src/data2dsl_adapters.py`.
- Support scalar (`float`, `integer`), thermal (`float`, `percentage`), and pinout/bus (`string-set`) metrics with SHA-256 evidence digests.
- Add unit test suite in `tests/test_oql_adapter.py`.
- Integrate OQL source formats (`oql`, `oqlos`, `oql_telemetry`, `oql_spec`) into `Data2DslSkill` and MCP dispatch (`src/data2dsl_skill.py`).
- Add skill unit tests and MCP JSON-RPC tests in `tests/test_skill.py`.
- Record `docs/decisions/ADR-006-oql-telemetry-hardware-normalization.md`.
- Refresh `docs/CAPABILITY_MAP.md` and `docs/research-oql-telemetry.md`.

### Runnable examples suite (ticket-050)

- Create simple, structured numbered examples in `examples/01-..` through `examples/05-..` with fixtures and READMEs.
- Add `examples/README.md` index and CLI usage instructions.

### Autonomous agent feedback feeds (tickets 043–045)

- Implement `DiagnosticProfileFormatter` and `format_diagnostic_profile()` in `src/data2dsl_doctor.py` for `subactor/doctor-agent` and triage.
- Expose `feed-doctor` CLI command and `data2dsl_feed_doctor` agent skill tool.
- Add comprehensive test suite in `tests/test_doctor_feed.py`.
- Implement `RemediationIntentFormatter` and `format_remediation_intent()` in `src/data2dsl_remediation.py` generating `remediation-intent/v1` for `semcod/koru` closed-loop self-healing.
- Expose `feed-koru` CLI command and unit tests in `tests/test_remediation_feed.py`.
- Record `docs/decisions/ADR-005-autonomous-agent-feedback-feeds.md` and refresh `docs/CAPABILITY_MAP.md`.

### Multi-source fact adapters (ticket-037)

- Implement `PlanfileAdapter` (`semcod.planfile`) for task queue metrics and ticket evidence.
- Implement `DetaAdapter` (`semcod.deta`) for infrastructure topology, services, and ports.
- Implement `IntentContractAdapter` (`subactor.intent-contract-dsl`) for parties, deliverables, and obligations.
- Expand `Data2DslSkill` with raw normalization for `planfile`, `deta`, and `intent_contract`.

### Quality gates: Float and percentage comparator (ticket-038)

- Extend `DeterministicComparator` with `float` and `percentage` comparison policies.
- Update `src/data2dsl_contract_v0/comparison.schema.json` with float/percentage value/delta schemas.
- Update `src/data2dsl_contract_v0/validate.py` conformance checks.

### Pipeline integration: urirun and MCP (ticket-039)

- Create `src/connector.manifest.json` declaring `data2dsl://` routes.
- Implement `urirun_bindings()` in `src/data2dsl_skill.py`.
- Implement JSON-RPC 2.0 MCP STDIO server handler `handle_mcp_message()` and `main_mcp()` runner.

### Architecture and capability mapping (ticket-040)

- Author `docs/decisions/ADR-004-multi-source-pipeline-architecture.md`.
- Refresh `docs/CAPABILITY_MAP.md` table and Mermaid composition graph with all 8 source adapters.

### Ecosystem research notes (ticket-041)

- Author `docs/research-koru-closed-loop.md`.
- Author `docs/research-diff-dsl-overlap.md`.
- Author `docs/research-oql-telemetry.md`.
- Author `docs/research-doctor-agent-feed.md`.


### Testing infrastructure (ticket-031)

- Add `tests/conftest.py` with automatic `sys.path` injection for `src/`.
- Clean unused imports flagged by `ruff`.

### Type safety and skill tests (ticket-033)

- Fix `mypy` type narrowing in `src/data2dsl_contract_v0/validate.py`.
- Expand `tests/test_skill.py` with comprehensive adapter coverage
  (curllm, code2logic, code2schema, missing inputs, unknown adapter).

### NLP integration research (ticket-034)

- Document `nlp2dsl` IntentPipeline integration architecture in
  `docs/nlp2dsl-integration-notes.md`.

### Browser-backed source adapter (ticket-019)

- Add `CurllmAdapter` for `semcod/curllm` BQL browser page extractions in
  `src/data2dsl_adapters.py`.
- Unit tests for valid and unevaluable Curllm observations in
  `tests/test_golden_case_e2e.py`.

### Docker compliance (ticket-021)

- Pin `python:3.12-alpine` base image to immutable SHA-256 digest in
  `Dockerfile`, resolving `GOV-DOCKER-002`.

### Architecture decisions (ticket-022)

- ADR-003: Evaluate `semcod/nlp2dsl` integration for natural language query
  compilation. Decision: delegate NLP to `nlp2dsl` outer boundary; `data2dsl`
  core remains zero-LLM, deterministic.

### Contract promotion (ticket-024)

- Promote `autogrammar.data2dsl.comparison` contract from `experimental` /
  `0.1.0-dev` to `stable` / `0.1.0` in `dsl-manifest.json`.

### Agent skill interface (ticket-025)

- Implement `Data2DslSkill` conforming to `wellmanifest.skills/v1` in
  `src/data2dsl_skill.py`.
- Expose `data2dsl_compare` and `data2dsl_self_test` tool definitions for
  MCP / JSON Schema agent discovery.
- CLI `--self-test` and tool execution tests in `tests/test_cli.py`.

### Bug fix (ticket-027)

- Fix adapter normalization in `data2dsl_skill.py` for `CurllmAdapter`,
  `Code2LogicAdapter`, and `Code2SchemaAdapter` raw input handling.

- Update TODO.md with Phase 5 task proposals for 2026-08-20.

## 0.1.0-dev (2026-08-19)

### Phase 4: Reasoning consumer integration

- Implement `ConsumerFactFeed` and `ReasoningFactPayload` in
  `src/data2dsl_consumer.py` (PR #16, ticket-015).
- Add CLI `feed-consumer` subcommand exporting comparison bundles to consumer
  fact feed JSON with canonical SHA-256 digests.
- Maintain strict separation: `data2dsl` provides facts and deltas; `todo2code`
  owns reasoning and policy decisions.

### Phase 3: Git factual seam extraction & multi-source fact adapters

- Evaluate extraction of minimal factual Git seam from `semcod/todo2code`;
  retained in `todo2code` until a second consumer requires it (ticket-013).
- Add optional fact adapters for `code2logic` (CFG/DFG/call-graph) and
  `code2schema` (entity/CQRS/API) in `src/data2dsl_adapters.py`.

### Phase 2B: Golden-case end-to-end implementation

- Implement explicit mapping from Markdown facts to `data2dsl` metric keys in
  `src/data2dsl_adapters.py` (ticket-007).
- Implement deterministic comparator with typed deltas (integer, string,
  string-set) in `src/data2dsl_comparator.py`.
- Verify `MATCH`, `CONFLICT`, `MISSING_LEFT`, `MISSING_RIGHT`, and
  `UNEVALUABLE` outcomes with integrity digests in
  `tests/test_golden_case_e2e.py`.

### Phase 2A: GitHub metrics acquisition

- Implement `data2dsl` read-only source adapter for extended `diagit` metrics
  in `src/data2dsl_adapters.py` (ticket-007).
- Unit test adapter with mock responses and `EvidenceRef` provenance envelope.
- Propose and merge upstream read-only provider extension in `subactor/diagit`
  (PR subactor/diagit#16).

### Phase 1B: Comparison contract v0

- Define the local experimental query/observation/result contract in
  `src/data2dsl_contract_v0/` (ticket-004).
- Pin and compose existing `wellmanifest/dsl` reusable profiles.
- Validate golden conflict/match fixtures and negative invariants.

### Phase 1A: Contract decision

- Decide compatibility of `subactor/twin` `Observation` and `EvidenceRef` for
  `data2dsl` (ticket-002, ADR-001). Verdict: EXTEND.
- Publish the pinned evidence and consequences as a decision document.

### Phase 0: Bootstrap

- Bootstrap governance and prepare the Phase 0 capability inventory.
- Allocate and link ticket-001; inventory 153 candidate repositories.
- Publish `docs/CAPABILITY_MAP.md` with composition graph.
- Build and run pinned Docker bootstrap.
- Create public `semcod/data2dsl` (moved to `autogrammar/data2dsl`).

### CLI interface (ticket-011)

- Add `data2dsl` CLI with `--self-test`, `compare`, `compare-golden`,
  `validate`, and `feed-consumer` subcommands.

### Architecture decisions

- ADR-001: Twin observation/evidence compatibility — verdict EXTEND.
- ADR-002: 3-stage deterministic comparison architecture — accepted.

### Governance milestones

- Ticket index generator (`project/readme.sh`) published under ticket-005.
- Publication closures: ticket-006, ticket-010, ticket-012, ticket-014,
  ticket-016.
