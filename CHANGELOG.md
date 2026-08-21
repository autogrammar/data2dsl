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
