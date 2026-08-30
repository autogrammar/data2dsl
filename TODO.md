# TODO

## Packaging regression - ticket-074

- [x] Package the discovery runtime.
- [x] Enforce local module import closure in dependent application ticket-075.
- [x] Package and verify the declared public CLI target in ticket-076.

## Audit publication - ticket-072

- [x] Re-audit local source 5eb2e32 and retain only remaining work.
- [x] Rebuild documentation-only publication from origin/main; preserve local code commits.
- [x] Publish and merge the audit through exact-head protected Validator review.


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
- [x] **Zaktualizuj TODO.md**: Odznacz zadania z 08-20, dodaj sekcję 08-21. — ticket-029
- [x] **Napraw README.md**: `0.1.0-dev` → `0.1.0` w sekcji "Current state",
  dodaj wzmiankę o adapterze Curllm i agent skill. — ticket-029
- [x] **Zregeneruj project/README.md**: Rozszerz ticket index z 6 do 29. — ticket-029
- [x] **Zaktualizuj CHANGELOG.md**: Dodaj wpisy za tickety 017–028. — ticket-029

### Jakość i stack compliance (workstream: `application`)

- [x] **Dodaj `conftest.py`**: Skonfiguruj `pytest` z automatycznym
  `PYTHONPATH=src` bez ręcznego env. — ticket-031
- [x] **Uruchom stack checks**: `ruff`, `mypy` — baseline raport jakości kodu
  wg `.governance/stack-profiles.json`. — ticket-033

### Research (workstream: `integration`)

- [x] **Research `nlp2dsl` IntentPipeline**: Przeanalizuj mechanizm vocabulary
  extension w `semcod/nlp2dsl`, zapisz notatkę w `docs/`. — ticket-034

---

## Zadania na dziś — 2026-08-24

Analiza ekosystemu `semcod/*` (56 pakietów), `subactor/*` (75 modułów),
`autogrammar/*` (36 repo), `if-uri/`, `urirun-connectors/` (92 konektory),
`oqlos/`, `MatthiasLew/`, `wellmanifest/`.

### Do 13:00 — Governance cleanup + pierwszy adapter

#### Governance cleanup (workstream: `governance`)

- [x] **Zamknij ticket-035**: Dokończ governance closure dla ticketów 033, 034.
  Ustaw `DONE / DONE`. — ticket-036
- [x] **Synchronizuj TODO.md**: Odznacz `[x]` checkboxy w sekcji 2026-08-21
  (linie 146–162) — praca faktycznie wykonana w ticketach 029, 031, 033, 034. — ticket-036
- [x] **Uzupełnij CHANGELOG.md**: Dodaj wpisy za tickety 029–035 (conftest,
  mypy fix, nlp2dsl research, governance closures). — ticket-036
- [x] **Odśwież README.md**: Zaktualizuj sekcję "Current state" — conftest,
  stack checks, nlp2dsl integration notes. — ticket-036
- [x] **Zregeneruj project/README.md**: Ticket index powinien zawierać tickety
  do 035. — ticket-036

#### Adaptery wieloźródłowe (workstream: `application`, ticket-037)

- [x] **Adapter `planfile`** (`semcod/planfile`): Nowy adapter normalizujący
  tickety/zadania z Planfile jako obserwacje faktyczne. Pozwala porównywać stan
  planfile vs stan kodu/testów. — ticket-037
- [x] **Adapter `deta`** (`semcod/deta`): Adapter do ekstrakcji faktów
  infrastrukturalnych (Docker services, porty, endpointy) z
  `deta.build_topology()` — porównywanie deklaracji vs runtime. — ticket-037
- [x] **Adapter `intent-contract`** (`subactor/intent-contract-dsl-runtime`):
  Adapter normalizujący Intent Contracts DSL v1 — strony, obowiązki,
  deliverables. Porównywanie kontraktu vs stan realizacji. — ticket-037

### Quality gates i walidacja (workstream: `application`, ticket-038)

- [x] **Komparator `float`/`percentage`**: Rozszerz `DeterministicComparator` o
  typy `float` i `percentage` delta (potrzebne dla metryk pyqual, code2llm
  health scores). — ticket-038
- [x] **Integracja `pyqual` gate** (`semcod/pyqual`): Obsługa metryk jakości
  kodów (float/percentage) do stage'ów pyqual. — ticket-038


### Integracja z pipeline (workstream: `application`, ticket-039)

- [x] **`urirun` connector manifest** (`urirun-connectors/`): Stworzono
  `src/connector.manifest.json` i `urirun_bindings` → `data2dsl` jako
  connector URI scheme `data2dsl://host/compare/run` i `data2dsl://host/selftest/run`. — ticket-039
- [x] **MCP server endpoint** (`semcod/mcp`): Wyeksponowano `Data2DslSkill` jako
  MCP JSON-RPC 2.0 STDIO server tool (`handle_mcp_message` / `main_mcp`) — dostępny dla Cursor/Windsurf/Claude Desktop natywnie. — ticket-039

### Dokumentacja (workstream: `integration`, ticket-040)

- [x] **ADR-004: Multi-source pipeline** (`docs/decisions/`): Dokument
  decyzyjny: architektura pipeline'u wieloźródłowego z integracją
  planfile→pyqual→koru. — ticket-040
- [x] **Aktualizacja CAPABILITY_MAP.md** (`docs/`): Dodano nowe adaptery i
  integracje do tabeli i grafu kompozycji. — ticket-040

### Research (notatki w `docs/`, ticket-041)

- [x] **Research: `koru` closed-loop** (`semcod/koru`): Oceniono jak `data2dsl`
  wchodzi w pętlę detect→plan→execute→verify→heal (`docs/research-koru-closed-loop.md`). — ticket-041
- [x] **Research: `diff-dsl` overlap** (`autogrammar/diff-dsl`): Sprawdzono
  nakładanie się i granice z `diff-dsl` (`docs/research-diff-dsl-overlap.md`). — ticket-041
- [x] **Research: OQL telemetry** (`oqlos/*`): Oceniono adapter dla OQL scenario
  outcomes (`docs/research-oql-telemetry.md`). — ticket-041
- [x] **Research: `doctor-agent` feed** (`subactor/doctor-agent`): Oceniono feed
  diagnostic-profile z data2dsl do doctor-agent (`docs/research-doctor-agent-feed.md`). — ticket-041

---

## Zadania na dziś — 2026-08-25

### Diagnostic feed i integracje agentowe (workstream: `application`, ticket-043, ticket-044)

- [x] **Moduł `data2dsl_doctor.py`**: Implementacja `DiagnosticProfileFormatter` generującego profil diagnostyczny dla `subactor/doctor-agent` i `semcod/koru`. — ticket-043
- [x] **CLI `feed-doctor`**: Komenda eksportująca profil diagnostyczny z porównań. — ticket-043
- [x] **Skill `data2dsl_feed_doctor`**: Integracja z agent skill oraz urirun / MCP bindings. — ticket-043
- [x] **Testy `test_doctor_feed.py`**: Pełne pokrycie testami jednostkowymi. — ticket-043
- [x] **Moduł `data2dsl_remediation.py`**: Implementacja `RemediationIntentFormatter` generującego remediation intent dla `semcod/koru` closed-loop self-healing. — ticket-044
- [x] **CLI `feed-koru`**: Komenda eksportująca remediation intent z porównań. — ticket-044
- [x] **Testy `test_remediation_feed.py`**: Pełne pokrycie testami jednostkowymi dla remediation feed. — ticket-044

### Dokumentacja i decyzje architektoniczne (workstream: `integration`, ticket-045)

- [x] **ADR-005: Autonomous Agent Feedback Feeds**: Utworzenie dokumentu ADR-005 dla integracji z doctor-agent i koru. — ticket-045
- [x] **Aktualizacja `CAPABILITY_MAP.md`**: Rozszerzenie tabeli i grafu kompozycji o diagnostic i remediation feeds. — ticket-045
- [x] **Aktualizacja `CHANGELOG.md` i `README.md`**: Odnotowanie modułów feeds, CLI commands, 49 testów jednostkowych i ADR-005. — ticket-045

---

## Zadania na dziś — 2026-08-26

### Adaptery telemetryczne i scenariusze (workstream: `application`, ticket-046)

- [x] **Adapter `oql` (`oqlos`)**: Adapter normalizujący scenariusze i logi telemetryczne sensorów OQL do obiektów `Observation` z `EvidenceRef`. — ticket-046
- [x] **Testy jednostkowe OQL**: Zestaw testów `tests/test_oql_adapter.py` dla metryk scalarnych, termicznych i string-set pinouts. — ticket-046
- [x] **Integracja agent skill & MCP**: Obsługa źródeł OQL w `Data2DslSkill` i dyspozytorze MCP wraz z testami `tests/test_skill.py`. — ticket-048
- [x] **ADR-006: OQL Telemetry and HIL Normalization**: Utworzenie dokumentu ADR-006 dla adaptera OQL i weryfikacji sprzętowej. — ticket-049
- [x] **Dokumentacja i struktura przykładów**: Aktualizacja dokumentacji projektu i utworzenie katalogu `examples/01-..` do `examples/05-..`. — ticket-050

---

## Zadania na dziś — 2026-08-27

### Zgodność z Subactorem i pętla samonaprawcza (workstream: `application`, ticket-051)

- [x] **Moduł `data2dsl_subactor.py`**: Implementacja parsera i walidatora semantycznego envelope Subactora (`ROLE`, `GOAL`, `SCOPE`, `ACCEPTANCE`, `AUTHORITY`, `LIMITS`, `REPORT`) ze standardowymi kodami błędów `COMM-ENVELOPE-001`, `COMM-ROLE-001`, `COMM-AUTH-001`. — ticket-051
- [x] **Zamknięta pętla samonaprawcza E2E**: Implementacja `simulate_self_healing_cycle` realizującej pętlę `DETECT` -> `PLAN` -> `EXECUTE` -> `VERIFY` -> `HEAL`. — ticket-051
- [x] **Rozszerzenie CLI `data2dsl`**: Dodanie subkomend `validate-envelope` i `simulate-healing`. — ticket-051
- [x] **Testy jednostkowe i E2E**: Utworzenie zestawów testów `tests/test_subactor_envelope.py` oraz `tests/test_self_healing_e2e.py` (67/67 testów przechodzi). — ticket-051
- [x] **Przykład `examples/06-closed-loop-self-healing/`**: Ustrukturyzowany pakiet demonstracyjny pętli samonaprawczej z fixtures i dokumentacją. — ticket-051

### Narzędzia MCP Subactora i adapter SUMD (workstream: `application`, ticket-052)

- [x] **Adapter `SUMDAdapter`**: Ekstrakcja i normalizacja faktów z tabel i deskryptorów Structured Unified Markdown Document (SUMD). — ticket-052
- [x] **Narzędzia MCP Subactora**: Integracja `data2dsl_validate_envelope` i `data2dsl_simulate_healing` w `Data2DslSkill` oraz routing `urirun`. — ticket-052
- [x] **Zestaw testów jednostkowych**: Utworzenie `tests/test_sumd_adapter.py` i rozszerzenie `tests/test_skill.py` (76/76 testów przechodzi). — ticket-052

### ADR-007, mapa możliwości i przykład SUMD (workstream: `integration`, ticket-053)

- [x] **Dokument decyzji ADR-007**: Utworzenie `docs/decisions/ADR-007-subactor-conformance-and-closed-loop-self-healing.md`. — ticket-053
- [x] **Aktualizacja `CAPABILITY_MAP.md`**: Rozszerzenie inwentarza o 10 adapterów i narzędzia Subactora. — ticket-053
- [x] **Przykład `examples/07-sumd-table-comparison/`**: Utworzenie pakietu demonstracyjnego ekstrakcji z tabel SUMD. — ticket-053

### Wsadowy silnik porównawczy Multi-Query (workstream: `application`, ticket-054)

- [x] **Silnik `BatchMultiQueryComparator`**: Implementacja `src/data2dsl_batch.py` z agregacją metryk podsumowania wsadu i wskaźnika czystości. — ticket-054
- [x] **Subkomenda CLI `batch`**: Dodanie polecenia `data2dsl batch` do `src/data2dsl_cli.py`. — ticket-054
- [x] **Zestaw testów jednostkowych i CLI**: Utworzenie `tests/test_batch_compare.py` (79/79 testów przechodzi). — ticket-054

### Generator szablonów zapytań (workstream: `application`, ticket-055)

- [x] **Generator `generate_query_template`**: Implementacja w `src/data2dsl_generator.py` dla 10 adapterów i typów metryk. — ticket-055
- [x] **Subkomenda CLI `generate-query`**: Dodanie polecenia `data2dsl generate-query` do `src/data2dsl_cli.py`. — ticket-055
- [x] **Zestaw testów jednostkowych i CLI**: Utworzenie `tests/test_generator.py` (83/83 testów przechodzi). — ticket-055

### Formatowanie raportów Markdown (workstream: `application`, ticket-056)

- [x] **Funkcja `format_markdown_report`**: Implementacja w `src/data2dsl_batch.py` dla wsadowych i pojedynczych raportów. — ticket-056
- [x] **Flaga `--format` w CLI**: Dodanie opcji `markdown` / `json` do komend `compare` i `batch` w `src/data2dsl_cli.py`. — ticket-056
- [x] **Zestaw testów jednostkowych i CLI**: Rozszerzenie `tests/test_batch_compare.py` (84/84 testów przechodzi). — ticket-056

### Przykład wsadowy 08 i synchronizacja dokumentacji (workstream: `integration`, ticket-057)

- [x] **Pakiet `examples/08-batch-multi-query/`**: Utworzenie gotowego pakietu demonstracyjnego z fixtures i instrukcją. — ticket-057
- [x] **Aktualizacja `examples/README.md`**: Włączenie Przykładu 08 do indeksu przykładów. — ticket-057
- [x] **Synchronizacja głównego `README.md`**: Uzupełnienie opisów 10 adapterów, subkomend CLI, generatora i Subactora. — ticket-057
