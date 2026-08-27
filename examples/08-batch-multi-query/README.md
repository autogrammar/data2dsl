# Example 08: Batch Multi-Query Evaluation and Markdown Reporting

This example demonstrates how to evaluate a batch collection of formal queries against heterogeneous observation sets in a single deterministic execution using `data2dsl batch`.

## Files in this example

- `queries.json`: Array of query objects (`autogrammar.data2dsl/query/v0`) covering ticket completions and test coverage.
- `left-observations.json`: Observed records from internal build sources (Planfile and CI).
- `right-observations.json`: Observed records from authoritative external systems (GitHub Pull Requests and CI Audit).

## CLI Execution

### 1. JSON Report Output
```bash
python src/data2dsl_cli.py batch \
  --queries examples/08-batch-multi-query/queries.json \
  --left examples/08-batch-multi-query/left-observations.json \
  --right examples/08-batch-multi-query/right-observations.json
```

### 2. Formatted Markdown Report
```bash
python src/data2dsl_cli.py batch \
  --queries examples/08-batch-multi-query/queries.json \
  --left examples/08-batch-multi-query/left-observations.json \
  --right examples/08-batch-multi-query/right-observations.json \
  --format markdown
```

## Expected Behavior

- **Total Queries**: 2
- **Matches**: 2
- **Conflicts**: 0
- **Clean Ratio**: 100.0% (`is_clean`: true)
- **Exit code**: `0`
