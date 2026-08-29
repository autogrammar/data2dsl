# Audyt data2dsl — tylko pozostałe prace

Aktualizacja: **2026-08-28**, ponowna kontrola lokalnego commitu **`5eb2e32c54a9858215cc770751ebc77d497e2628`**, ticket **072**.

**Repozytorium nadal nie jest gotowe w 100%.** Poniżej pozostają wyłącznie nierozwiązane problemy i brakujące kontrole. Odhaczenie F01–F15 w TODO nie zamyka ich automatycznie.

Weryfikacja lokalna: **127 testów przeszło**, ruff i self-test kontraktu przeszły; **mypy wykazał 11 błędów**. Dodatkowe próby potwierdziły opisane poniżej usterki. Nie zmieniałem kodu aplikacji. Szczegóły przebiegu kontroli znajdują się w [logu ticketu](../project/ticket-072/ai-codex-logs.txt).

> **Zakres publikacji:** dokument opisuje lokalny kod z commitu 5eb2e32, a nie stan zdalnego main. Gałąź dokumentu początkowo powstała z origin/main 1e7eddd, a następnie została zsynchronizowana z aktualnym main. Sam PR audytu zmienia wyłącznie dokumentację; część zmian aplikacji została w międzyczasie scalona odrębnym PR. Odnośniki do plików służą nawigacji; podane linie i wyniki dotyczą wersji audytowanej.

## P1 — blokady działającego i wiarygodnego wydania

### 1. Uzupełnić wheel o moduł CLI i sprawdzać instalowany artefakt

- [ ] Dodać `data2dsl_cli` do pakowanych modułów.
- [ ] Dodać test instalacji wheel poza checkoutem: `data2dsl --help`, `data2dsl --self-test`, porównanie i walidacja.

**Dowód:** [pyproject.toml](../pyproject.toml), linie 32–46. Entry point wskazuje `data2dsl_cli:main`, lecz lista `py-modules` nie zawiera tego modułu. Ponownie zbudowany wheel nadal nie zawiera `data2dsl_cli.py`; import z rozpakowanego artefaktu kończy się `ModuleNotFoundError`.

**Warunek zamknięcia:** CLI działa z samego zainstalowanego wheel, bez `PYTHONPATH=src` i bez dostępu do checkoutu.

### 2. Dokończyć wspólną walidację porównywalności i wyników

- [ ] Sprawdzać pełne `subject`, `metric` z jednostką i wersją, `window`, `query_id`, stronę obserwacji, rzeczywisty typ wartości, politykę i evidence.
- [ ] Wprowadzić obowiązkową walidację w publicznych ścieżkach Skill/MCP, batch, Doctor i Remediation.
- [ ] Uzgodnić obsługę błędnych danych i obu brakujących stron tak, aby nie emitować bundle niezgodnego z kontraktem.
- [ ] Poprawić identyfikatory dowodów Code2Logic/Code2Schema zawierające niedozwolony znak `/`.

**Dowód:** [komparator](../src/data2dsl_comparator.py), `_is_compatible`, linia 142; [Skill](../src/data2dsl_skill.py), `execute_compare`; [Doctor](../src/data2dsl_doctor.py) i [Remediation](../src/data2dsl_remediation.py).

W odrębnych próbach zmiana wyłącznie jednostki, wersji metryki, strony prawej obserwacji, jej typu wartości lub usunięcie evidence nadal dawały **`OK / MATCH`**, choć `validate_document` odrzucał wynik. Parametr `expected_side` nie jest używany. Zmiana aktora daje już `UNEVALUABLE`, ale zwracany bundle nadal zawiera sprzeczne dane i nie przechodzi walidacji.

`format_remediation_intent({"outcome": "MATCH"})` zwraca `SATISFIED` bez obserwacji i dowodów. Obie brakujące obserwacje dają pustą listę odrzucaną przez schemat. Domyślny Code2Logic emituje np. `evidence:code2logic:src/main.py:1-1`, niezgodne z formatem identyfikatora; Code2Schema ma analogiczny problem.

**Warunek zamknięcia:** żadna publiczna ścieżka nie uznaje niepoprawnych danych za zgodne; poprawne wyniki wszystkich adapterów przechodzą ten sam kontrakt.

### 3. Odrzucać niejednoznaczne obserwacje w batch

- [ ] Wykrywać duplikaty `query_id` i pełnego klucza obserwacji.
- [ ] Uwzględnić w doborze obserwacji okres, jednostkę i wersję metryki.
- [ ] Zamiast nadpisywać wcześniejsze dane, zwracać jawny błąd niejednoznaczności albo stosować wyraźnie określoną regułę wersjonowania.

**Dowód:** [data2dsl_batch.py](../src/data2dsl_batch.py), linie 87–147. Dwie prawe obserwacje tego samego zapytania, jedna zgodna i druga z wartością `999`, dają zależnie od kolejności wejścia **`CONFLICT` albo `is_clean: true`**. Słownik zachowuje ostatnią wartość.

**Warunek zamknięcia:** przestawienie kolejności sprzecznych duplikatów nie może zmieniać błędu danych w czysty raport.

### 4. Domknąć deserializację i semantykę adapterów

- [ ] Code2Schema: przekazywać `entities`, a nie nieistniejący argument `value`.
- [ ] Curllm i Code2Logic: respektować status błędu odpowiedzi, nawet gdy zawiera ona wartość.
- [ ] OQL: zamienić odwołanie do nieistniejącego `observed_buses` na właściwe pole modelu.
- [ ] OQL raw: odróżniać zero od braku danych, bez wybierania wartości przez `a or b`.
- [ ] Sprawdzać czas pochodzenia telemetrii zamiast przepisywać jej okno z query.
- [ ] Dodać testy zwykłego JSON dla każdego adaptera, obejmujące błędy dostawcy, zero, brak, magistrale i walidację końcowego bundle.

**Dowód:** [data2dsl_skill.py](../src/data2dsl_skill.py), linie 124 i 230; [data2dsl_adapters.py](../src/data2dsl_adapters.py), linia 1512.

Odtworzone wyniki:

| Przypadek | Aktualny wynik |
| --- | --- |
| Code2Schema, JSON `{"status":"OK","entities":["User"]}` | `TypeError: unexpected keyword argument 'value'` |
| Curllm/Code2Logic, `status: ERROR` i przekazana wartość | `OBSERVED` |
| OQL, `active_buses: ["i2c"]` | `AttributeError: ... no attribute 'observed_buses'` |
| OQL raw, `avg_sample_rate_hz: 0` | `UNEVALUABLE` zamiast pomiaru zero |
| Telemetria z okresem w 1999 r., query z sierpnia 2026 | `OBSERVED` z okresem przepisanym z query |

**Warunek zamknięcia:** adapter nie zmienia błędu w pomiar, zera w brak ani starej telemetrii w aktualną obserwację.

### 5. Dopasowywać aktora i metrykę dokładnie, nie jako podciąg

- [ ] W Markdown wprowadzić jednoznaczne dopasowanie identyfikatora aktora i obsługę wielu pasujących deklaracji.
- [ ] W SUMD dopasowywać pełny klucz; jawne aliasy utrzymywać w osobnej mapie.

**Dowód:** [data2dsl_adapters.py](../src/data2dsl_adapters.py), linie 235, 1632 i 1670.

Dla `malice: 99 commits\nalice: 12 commits` i pytania o `alice` parser nadal zwraca **99**. Dla tabeli z `tasks_completed_total = 99` przed `tasks_completed = 12`, pytanie o `tasks_completed` również zwraca **99**.

**Warunek zamknięcia:** podobna nazwa nie może przejąć cudzego pomiaru; niejednoznaczność musi być widoczna.

### 6. Dokończyć integralność i identyfikację dowodów

- [ ] Rozdzielić hash surowego źródła od hasha danych wyliczonych z query/metryki.
- [ ] Zachować rzeczywiste evidence stron w ścieżce CLI golden; nie przedstawiać zastępczego digestu jako hasha odpowiedzi API.
- [ ] Stosować jednoznaczną serializację struktur przed haszowaniem, np. kanoniczny JSON zamiast łączenia list przecinkami.
- [ ] Odświeżyć hashe schematu i walidatora w manifeście DSL oraz sprawdzać je automatycznie.
- [ ] Zapewnić kontekstową unikalność identyfikatorów obserwacji i evidence oraz wykrywać sprzeczne dowody o tym samym ID.

**Dowód:** [adaptery](../src/data2dsl_adapters.py), linie 140, 1150, 1385 i 1551; [CLI](../src/data2dsl_cli.py); [manifest DSL](../src/data2dsl_contract_v0/dsl-manifest.json).

GitHub nadal tworzy `dummy_digest` z wartości i okresu. OQL hashuje wynik normalizacji, nie treść logu. Dwa dopuszczone przez typ `string-set` zbiory `["a,b", "c"]` oraz `["a", "b,c"]` nadal dają ten sam digest przy tym samym identyfikatorze i ścieżce, ponieważ oba są serializowane do `a,b,c`. To nie jest kolizja SHA-256, lecz niejednoznaczność wejścia.

Ponowna kontrola bajtów `git show HEAD:...` wykazała, że zapisane w manifeście hashe `comparison.schema.json` oraz `validate.py` nie odpowiadają aktualnym plikom.

**Warunek zamknięcia:** dowód jednoznacznie wskazuje haszowaną treść, zmiana tej treści zmienia digest, a manifest jest zgodny z wydawanymi plikami.

### 7. Dokończyć działający transport MCP

- [ ] Przenieść tekst self-testu poza STDOUT protokołu albo przechwycić go wewnątrz narzędzia.
- [ ] Dodać udokumentowany, pakowany entry point serwera MCP.
- [ ] Rozróżniać błędy parsowania, argumentów i wykonania; zachowywać ID żądania i poprawne oznaczenie błędu narzędzia.
- [ ] Dodać test pełnej sesji STDIO w subprocess: inicjalizacja, discovery, self-test, porównanie i błędne wejście.

**Dowód:** [data2dsl_skill.py](../src/data2dsl_skill.py), `self_test` i `main_mcp`; [pyproject.toml](../pyproject.toml).

Przy rzeczywistym wywołaniu `main_mcp()` pierwszą linią odpowiedzi self-testu nadal jest **`CONTRACT-V0-PASS: ...`**, a dopiero następną JSON-RPC. Nie ma entry pointu MCP ani uruchomienia pętli przy wykonaniu modułu. Nowy [test zgodności MCP](../tests/test_mcp_protocol_compliance.py) sprawdza definicje narzędzi, lecz nie uruchamia STDIO.

**Warunek zamknięcia:** każda linia STDOUT serwera jest poprawnym komunikatem protokołu, a użytkownik może uruchomić serwer z zainstalowanego pakietu.

## P2 — pozostałe poprawki poprawności, dokumentacji i kontroli wydania

### 8. Określić i egzekwować precyzję liczb

- [ ] Nie zaokrąglać pomiarów w adapterze przed porównaniem bez jawnej polityki.
- [ ] Zdefiniować zakres i precyzję `float-exact`/`percentage-exact`; użyć odpowiedniej reprezentacji dziesiętnej albo odrzucać wartości poza wspieranym zakresem.
- [ ] Zapobiec konfliktom liczbowym z nieinformacyjną deltą zero.

**Dowód:** [komparator](../src/data2dsl_comparator.py), linie 120–138; [walidator](../src/data2dsl_contract_v0/validate.py), `_canonical_value` i `_expected_delta`; normalizacja OQL w [adapterach](../src/data2dsl_adapters.py).

`1.0000000000` i `1.0000000005` dają `CONFLICT` z deltą `0`. Dla typu float liczby `9007199254740992` i `9007199254740993` dają `MATCH` wskutek konwersji do binarnego float, mimo że kontrakt przyjmuje oba napisy. Pomiar OQL `0.001` jest zamieniany na `0.00`.

**Warunek zamknięcia:** reguły precyzji są jawne, wspólne dla adaptera, komparatora i walidatora, a testy obejmują ich granice.

### 9. Domknąć walidację parametrów generatora i okresu

- [ ] Naprawić domyślne okno czasu pierwszego dnia miesiąca.
- [ ] Walidować `start < end`, daty, źródła, typy i zgodność jawnej polityki z typem metryki.
- [ ] Nie nadpisywać jawnie podanej jednostki heurystyką nazwy metryki.
- [ ] Udostępnić wybór okresu w CLI generatora.

**Dowód:** [data2dsl_generator.py](../src/data2dsl_generator.py), linie 68–95; [CLI](../src/data2dsl_cli.py), komenda `generate-query`.

Przy symulowanym zegarze **2026-09-01 15:00 UTC** generator tworzy `start = end = 2026-09-01T00:00:00Z`. Wynik odrzuca własny walidator: `query window must have start before end`. CLI nadal nie udostępnia dodanych w API parametrów `window_start`/`window_end`.

**Warunek zamknięcia:** generator zwraca poprawne zapytanie albo czytelny błąd, również pierwszego dnia miesiąca.

### 10. Poprawić pozostałe instrukcje, formatowanie i deklaracje

- [ ] Przykład 02: dodać wymagane identyfikatory i ścieżki odpowiedzi oraz rzeczywiste wczytanie query.
- [ ] Przykład 07: użyć faktycznie istniejącego API/CLI do ekstrakcji SUMD; nie przekazywać pliku Markdown jako JSON obserwacji.
- [ ] Wykonywać instrukcje wszystkich przykładów w testach; samo sprawdzenie ręcznie zapisanych `expected-*.json` nie wystarcza.
- [ ] Zaktualizować README/ADR do rzeczywistego `remediation-feed/v0` i oddzielić symulację naprawy od wykonania oraz od kontroli uprawnień.
- [ ] W raportach Markdown obsłużyć nowe linie i backticki w wartościach, nie tylko znak `|`.
- [ ] Skorygować TODO i statusy governance tam, gdzie ogłoszono pełne zakończenie mimo pozostałych prac; historycznych wpisów nie traktować jako dowodu poprawności.

**Dowód:** [przykład 02](../examples/02-oql-telemetry-verification/README.md) nadal kończy się błędem brakujących `scenario_id` i `path`. W [przykładzie 07](../examples/07-sumd-table-comparison/README.md) zamieniono nieistniejący przełącznik na inny nieistniejący: `--left-source-type sumd`; parser nadal kończy się kodem **2**.

[README](../README.md) nadal deklaruje pełną zgodność Subactor i dawny format remediation. [Symulacja](../src/data2dsl_subactor.py) kopiuje wartość oczekiwaną do obserwacji, zamiast wykonywać naprawę i pozyskiwać świeży pomiar. [Formatter](../src/data2dsl_batch.py) nie koduje nowych linii i backticków. Tickety 051–057 pozostają `PLAN / PUBLICATION`; ticket 058 ma sprzeczny opis wyniku i status.

**Warunek zamknięcia:** instrukcje uruchamiają się dosłownie, a dokumentacja nie przypisuje programowi gwarancji, których nie zapewnia.

### 11. Przywrócić kontrolę typów i dodać brakujące bramki CI

- [ ] Usunąć **11 błędów mypy**: 10 przypisań `None` do zmiennej zadeklarowanej jako słownik oraz nieistniejące `observed_buses`.
- [ ] Zapisać konfigurację i zależności narzędzi jakości tak, aby dało się odtworzyć kontrole jednym udokumentowanym zestawem komend.
- [ ] Dodać workflow testów aplikacji: pytest, ruff, mypy, build i instalacja wheel, sesja MCP, przykłady, kontrakty i digests manifestu.
- [ ] Testować deklarowane wersje Pythona.
- [ ] Przed wydaniem uruchomić testy Docker i skany zależności/obrazu; zapisać wyniki, nie tylko poprawność pliku Compose.
- [ ] Uzgodnić bazę i ścieżkę publikacji lokalnych zmian z governance, bez zastępowania faktycznej bazy audytu innym SHA tylko dla uzyskania zielonej bramki.

**Dowód:** `python -m mypy --explicit-package-bases --ignore-missing-imports src` zwraca **11 errors in 1 file**. W [workflow repozytorium](../.github/workflows/new-project-governance.yml) nadal jest tylko kontrola lifecycle gałęzi, bez testów aplikacji. Testy, które przechodzą, nie obejmują kilku publicznych ścieżek opisanych powyżej.

Podczas ponownej kontroli `docker compose config --quiet` przeszedł, ale silnik `dockerDesktopLinuxEngine` był niedostępny. Wykonanie kontenera pozostaje **niezweryfikowane**, nie oznaczam go jako potwierdzonej usterki kodu. Nie sprawdzałem zewnętrznych usług CI, ustawień GitHub ani rzeczywistych konsumentów.

Końcowa kontrola lokalnego audytu `project/governance-check.bat`, również z jawną listą zmienionych plików, zwraca **`GOV-BASE-001`**: zaakceptowana baza tego lokalnego audytu to `5eb2e32`, natomiast checker preferuje `origin/main = 1e7eddd`. Lokalne `main` jest 39 commitów przed tą referencją. To blokada procesu publikacji, odrębna od błędów aplikacji. Nie zmieniałem referencji, nie cofałem zmian ani nie wykonywałem push/rebase w ramach audytu.

Publikację samego dokumentu później wydzielono na gałąź z bazy `1e7eddd`: jej kontrola governance przeszła. Nie zamyka to publikacji ani walidacji 39 lokalnych commitów kodu objętych audytem.

**Warunek zamknięcia:** lokalne kontrole i obowiązkowe CI sprawdzają instalowany produkt oraz jego publiczne interfejsy; każde pozostałe ograniczenie jest jawnie opisane.
