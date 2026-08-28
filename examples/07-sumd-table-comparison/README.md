# Example 07: SUMD Table Metric Comparison

This example demonstrates factual extraction from a **Structured Unified Markdown Document (SUMD)** table and deterministic comparison against an external baseline observation.

## Files

- `document.sumd.md`: SUMD document containing factual metrics in a standard table.
- `query.json`: Canonical `autogrammar.data2dsl/query/v0` query targeting `tasks_completed`.
- `right-observation.json`: Right-side observation representing observed system telemetry.
- `expected-result.json`: Expected comparison bundle outcome (`MATCH`).

## Execution

```bash
# Extract and compare SUMD document directly via CLI
python -m data2dsl_cli compare \
  --query examples/07-sumd-table-comparison/query.json \
  --left examples/07-sumd-table-comparison/document.sumd.md \
  --left-source-type sumd \
  --right examples/07-sumd-table-comparison/right-observation.json
```
