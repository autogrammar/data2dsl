# TODO

## Phase 0

- [x] Allocate and link [`ticket-001`](project/ticket-001/README.md).
- [x] Record bounded intent, risks, and acceptance criteria.
- [x] Inventory candidate capabilities with concrete evidence.
- [x] Publish [`docs/CAPABILITY_MAP.md`](docs/CAPABILITY_MAP.md) with a composition graph.
- [x] Run the deterministic governance gate.
- [x] Build and run the pinned Docker bootstrap without a host fallback.
- [x] Create public `semcod/data2dsl` after explicit external-coordination
  authority and repository visibility were supplied.

No functional implementation is authorized in Phase 0.

## Phase 1A: contract decision

- [x] Decide compatibility of `subactor/twin` `Observation` and `EvidenceRef`
  for `data2dsl` in [`ticket-002`](project/ticket-002/README.md).
- [x] Publish the pinned evidence and consequences as a decision document.

No implementation or changes to external repositories are authorized by this
ticket.

## Phase 1B: comparison contract v0

- [x] Define the local experimental query/observation/result contract in
  [`ticket-004`](project/ticket-004/README.md).
- [x] Pin and compose the existing `wellmanifest/dsl` reusable profiles.
- [x] Validate golden conflict/match fixtures and negative invariants.

All writes remain inside `data2dsl`; neighboring repositories are read-only
contract sources and validation tools.

## Project communication

- [x] Explain the concrete data2dsl product vision, boundaries, golden case and
  roadmap in the root README under [`ticket-003`](project/ticket-003/README.md).
- [x] Generate [`project/README.md`](project/README.md) with the repository-owned
  ticket-index generator under [`ticket-005`](project/ticket-005/README.md).

## Repository governance

- [x] Publish ticket 005 through the protected Validator App boundary and
  record its closure in [`ticket-006`](project/ticket-006/README.md).
- [x] Publish tickets 007, 008, and 009 through the protected Validator App boundary and
  record their closure in [`ticket-010`](project/ticket-010/README.md).
- [x] Publish tickets 010 and 011 through the protected Validator App boundary and
  record their closure in [`ticket-012`](project/ticket-012/README.md).

## Phase 2A: GitHub metrics acquisition (`subactor/diagit` extension & adapter)

- [x] Link and define [`ticket-007`](project/ticket-007/README.md) for GitHub metric source adapter.
- [x] Implement `data2dsl` read-only source adapter for extended `diagit` metrics in [`src/data2dsl_adapters.py`](src/data2dsl_adapters.py).
- [x] Unit test adapter with mock responses and `EvidenceRef` provenance envelope in [`tests/test_golden_case_e2e.py`](tests/test_golden_case_e2e.py).
- [x] Propose and merge upstream read-only provider extension in `subactor/diagit` repository (PR [subactor/diagit#16](https://github.com/subactor/diagit/pull/16)).

## Phase 2B: Golden-case end-to-end implementation (`work-summary.md` vs GitHub)

- [x] Implement explicit mapping from Markdown facts to `data2dsl` metric keys in [`src/data2dsl_adapters.py`](src/data2dsl_adapters.py).
- [x] Implement deterministic comparator with typed deltas in [`src/data2dsl_comparator.py`](src/data2dsl_comparator.py).
- [x] Verify `MATCH`, `CONFLICT`, `MISSING_LEFT`, `MISSING_RIGHT`, and `UNEVALUABLE` outcomes with integrity digests in [`tests/test_golden_case_e2e.py`](tests/test_golden_case_e2e.py).



## Phase 3: Git factual seam extraction & multi-source fact adapters

- [x] Evaluate extraction of minimal factual Git seam from `semcod/todo2code` (retained in todo2code until second consumer requires it per [`docs/CAPABILITY_MAP.md`](docs/CAPABILITY_MAP.md#L30)).
- [x] Provide optional fact adapters for code analyzers (`code2logic`, `code2schema`) in [`src/data2dsl_adapters.py`](src/data2dsl_adapters.py).


## Phase 4: Reasoning consumer integration (`todo2code`)

- [ ] Feed structured `data2dsl` factual outcomes and deltas into `todo2code`.
- [ ] Maintain strict separation of concerns: `data2dsl` provides facts and deltas; `todo2code` handles reasoning and policy decisions.

