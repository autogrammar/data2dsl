# nlp2dsl IntentPipeline Integration Notes

- **Date:** 2026-08-21
- **Related:** ADR-003, ticket-022, ticket-034
- **Status:** Approved integration architecture notes (no runtime LLM dependencies in core)

## Architecture Summary

`semcod/nlp2dsl` uses a protocol-driven IR pipeline:

```
NL Query → QueryNormalizer → EntityExtractor → IntentDetector → IntentIR → PlanRouter → ExecutionPlanIR
```

Key packages in upstream `semcod/nlp2dsl`:
- `packages/pact-ir/`: Defines `IntentIR`, `EntityBag`, `TargetKind`, `ExecutionRisk`
- `packages/nlp2cmd-intent/`: `IntentPipeline`, `KeywordIntentDetector`, protocols
- `packages/nlp2cmd-planner/`: `PlanningPipeline`, `PlanRouter`, `PlanStrategy`
- `packages/dsl-contracts/`: `ActionContract` with lifecycle

## Extension Mechanisms

1. **Custom `EntityExtractor`** — protocol: `extract(query) → EntityBag`
2. **Pattern registration** — `KeywordIntentDetector.add_pattern(domain, intent, patterns)`
3. **Custom `PlanStrategy`** — protocol: `supports(intent) → bool`, `plan(intent) → ExecutionPlanIR`
4. **Plugin manifest** — `plugin.yaml` with contracts/executors
5. **Contract drafts** — `.nlp2dsl/generated/contracts/*.draft.yaml`
6. **YAML resource areas** — `nlp2dsl.yaml` dynamic loading

## Recommended data2dsl Integration

### 1. Domain Patterns

```json
{
  "data2dsl": {
    "compare_observations": [
      "porównaj", "compare", "reconcile",
      "zweryfikuj zgodność", "check consistency",
      "różnica metryk"
    ]
  }
}
```

### 2. Entity Extractor

Implement `Data2DslEntityExtractor` extracting:
- `subject` (repository, actor)
- `metric` (id, version, value_kind, unit)
- `window` (start, end, semantics)
- `left_source` / `right_source` (id, kind)
- `comparison` (equality, delta_direction, missing_is_zero)

### 3. Plan Strategy

```python
class Data2DslPlanStrategy:
    name = "data2dsl"
    def supports(self, intent: IntentIR) -> bool:
        return intent.domain == "data2dsl"
    def plan(self, intent: IntentIR) -> ExecutionPlanIR:
        # Build PlanStep with action='data2dsl_compare'
        # TargetKind.SHELL (CLI) or TargetKind.MCP (agent tool)
        ...
```

### 4. Action Contract

```yaml
name: compare_observations
category: data2dsl
required: [subject, metric, left_source, right_source, comparison]
optional:
  window: null
aliases: [porównaj obserwacje, compare observations]
```

## Boundary Invariants

- All natural language parsing and prompt interaction is confined to `semcod/nlp2dsl`.
- `autogrammar/data2dsl` remains zero-LLM, deterministic, and effect-free.
- Interaction between `nlp2dsl` and `data2dsl` is mediated strictly through `autogrammar.data2dsl/query/v0` JSON AST contracts and CLI / MCP tools (`data2dsl_compare`).
