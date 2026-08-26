# 01-markdown-github-comparison

Demonstrates factual verification of a documented Markdown commit claim against actual GitHub commit counts.

## Fixtures

- `query.json`: Data2DSL query specifying target repository and metric `code.commit.count` (`integer`).
- `work-summary.md`: Documented markdown work summary stating 5 commits.
- `github-commits.json`: Raw GitHub commits API response payload showing 5 commits.
- `expected-bundle.json`: Expected comparison bundle yielding `MATCH`.

## Running the comparison via Python API

```python
from data2dsl_adapters import WorkSummaryMarkdownAdapter, GitHubDiagitAdapter
from data2dsl_comparator import DeterministicComparator

# Normalize left and right observations
obs_left = WorkSummaryMarkdownAdapter().normalize(query, markdown_resp, side="left")
obs_right = GitHubDiagitAdapter().normalize(query, github_resp, side="right")

# Deterministic comparison
bundle = DeterministicComparator().compare(query, obs_left, obs_right)
assert bundle["result"]["outcome"] == "MATCH"
```
