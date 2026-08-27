# Przykład 06: Autonomiczna pętla samonaprawcza (Closed-Loop Self-Healing E2E)

Przykład demonstruje pełny, 5-etapowy cykl samonaprawczy (`DETECT` -> `PLAN` -> `EXECUTE` -> `VERIFY` -> `HEAL`) w oparciu o delegację Subactora i feedy `data2dsl`.

## Pliki w przykładzie

- `envelope.txt`: Semantyczny envelope delegacji dla Subactora.
- `query.json`: Definicja zapytania porównawczego (`autogrammar.data2dsl/query/v0`).
- `left-observation.json`: Stan źródłowy (np. deklaracja ze specyfikacji/Markdownu).
- `right-observation.json`: Stan obserwowany z anomaliami i rozbieżnością.
- `expected-healed-result.json`: Oczekiwany wynik po wykonaniu pętli samonaprawczej.

## Uruchomienie

### 1. Walidacja envelope Subactora:
```bash
python -m data2dsl validate-envelope --envelope envelope.txt
```

### 2. Symulacja zamkniętej pętli samonaprawczej:
```bash
python -m data2dsl simulate-healing --query query.json --left left-observation.json --right right-observation.json
```
