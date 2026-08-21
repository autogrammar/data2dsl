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
- [x] Publish tickets 012 and 013 through the protected Validator App boundary and
  record their closure in [`ticket-014`](project/ticket-014/README.md).
- [x] Publish tickets 014 and 015 through the protected Validator App boundary and
  record their closure in [`ticket-016`](project/ticket-016/README.md).

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

- [x] Feed structured `data2dsl` factual outcomes and deltas into `todo2code` in [`src/data2dsl_consumer.py`](src/data2dsl_consumer.py) and CLI `feed-consumer`.
- [x] Maintain strict separation of concerns: `data2dsl` provides facts and deltas; `todo2code` handles reasoning and policy decisions.


---

## Zadania na dziś — 2026-08-20

Proponowane na podstawie analizy repozytorium i ekosystemu
`semcod/*`, `autogrammar/*`, `subactor/*`, `wellmanifest/*`.

### Governance housekeeping (workstream: `governance`)

- [x] **Zamknij ticket-016**: Zweryfikuj integrację na `main`, ustaw
  `DONE / DONE`. Zregeneruj `project/README.md` (ticket index zatrzymany na
  ticket-006). — ticket-017
- [x] **Zaktualizuj CHANGELOG.md**: Uzupełnij wpisy za Phase 1A–4 z datami
  merge'ów PR #6–#16 (aktualnie wymieniony tylko Phase 0 bootstrap). — ticket-017
- [x] **Zaktualizuj README.md sekcja "Current state"**: Odzwierciedl faktyczny
  stan — pełna implementacja golden case, CLI, konsumer feed, testy E2E. — ticket-017

### Release preparation (workstream: `integration`)

- [x] **Bump VERSION do `0.1.0`**: Obecne `0.0.0` nie odzwierciedla stanu.
  Wymaga ticketu w workstreamie `integration` (plik `VERSION` jest owned path
  `integration`). — ticket-018
- [x] **Utwórz `pyproject.toml`**: Zdefiniuj pakiet `data2dsl` z zależnością
  `jsonschema>=4.26.0`. Wymagane przez `integration` workstream
  (`manifest.json` → `coordination.integration.requiredForPaths`). — ticket-018

### Contract stabilization (workstream: `application`)

- [x] **Promuj kontrakt z `experimental` na `stable`**: Przenieś
  `autogrammar.data2dsl.comparison` z `0.1.0-dev` do `0.1.0` w
  [`dsl-manifest.json`](src/data2dsl_contract_v0/dsl-manifest.json). Wymaga
  powiązanego upstream review w `wellmanifest/dsl`. — ticket-024
- [x] **Pin Docker base image digest**: Zamień `python:3.12-alpine` na
  `python:3.12-alpine@sha256:...` w [`Dockerfile`](Dockerfile) (rozwiązuje
  potencjalne `GOV-DOCKER-002`). — ticket-021

### Phase 5: NLP query builder & multi-source expansion (workstream: `application`)

- [x] **Zbadaj integrację `semcod/nlp2dsl`**: Oceń rozszerzenie
  `IntentPipeline` o vocabulary `data2dsl` — generowanie bounded comparison
  query z naturalnego pytania. Zapisz ADR-003. — ticket-022
- [x] **Dodaj adapter `curllm` (browser-backed source)**: Zaprojektuj thin
  adapter na `semcod/curllm` BQL do akwizycji faktów z przeglądarki jako
  trzecie źródło obserwacji. — ticket-019
- [x] **Zbadaj integrację `wellmanifest/skills`**: Oceń publikację `data2dsl`
  CLI jako governed agent skill (skill manifest + deterministic error routing).
  — ticket-025

### Priorytet na dziś

Wykonano w kolejności zależności:
1. ~~Zamknij ticket-016 (governance)~~ — ticket-017 ✓
2. ~~CHANGELOG + README update (governance)~~ — ticket-017 ✓
3. ~~VERSION bump + pyproject.toml (integration)~~ — ticket-018 ✓
4. ~~Docker digest pin (infrastructure)~~ — ticket-021 ✓
5. ~~Analiza NLP/curllm/skills (application)~~ — ticket-019, 022, 025 ✓

---

## Zadania na dziś — 2026-08-21

### Governance housekeeping (workstream: `governance`, ticket-029)

- [x] **Zamknij ticket-028**: PR #29 merged (`c0bb0db`), ustaw `DONE / DONE`.
- [ ] **Zaktualizuj TODO.md**: Odznacz zadania z 08-20, dodaj sekcję 08-21.
- [ ] **Napraw README.md**: `0.1.0-dev` → `0.1.0` w sekcji "Current state",
  dodaj wzmiankę o adapterze Curllm i agent skill.
- [ ] **Zregeneruj project/README.md**: Rozszerz ticket index z 6 do 29.
- [ ] **Zaktualizuj CHANGELOG.md**: Dodaj wpisy za tickety 017–028.

### Jakość i stack compliance (workstream: `application`)

- [ ] **Dodaj `conftest.py`**: Skonfiguruj `pytest` z automatycznym
  `PYTHONPATH=src` bez ręcznego env.
- [ ] **Uruchom stack checks**: `ruff`, `mypy` — baseline raport jakości kodu
  wg `.governance/stack-profiles.json`.

### Research (workstream: `integration`)

- [ ] **Research `nlp2dsl` IntentPipeline**: Przeanalizuj mechanizm vocabulary
  extension w `semcod/nlp2dsl`, zapisz notatkę w `docs/`.

