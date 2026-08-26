# 04-koru-remediation-feed

Demonstrates generating machine-actionable `new-project.remediation-intent/v1` manifests consumed by `semcod/koru` for closed-loop self-healing (`DETECT → PLAN → EXECUTE → VERIFY → HEAL`).

## Fixtures

- `bundle.json`: A comparison bundle containing discrepancy data.
- `expected-remediation-intent.json`: Structured remediation plan with action items (`synchronize_metric`), status `PROPOSED`, and pinned evidence hashes.

## Running via CLI and Python API

```bash
# Via CLI
python src/data2dsl_cli.py feed-koru -b bundle.json -o remediation_intent.json
```

```python
# Via Python API
from data2dsl_remediation import format_remediation_intent

intent = format_remediation_intent(bundle)
assert intent["status"] == "PROPOSED"
assert len(intent["actions"]) == 1
assert intent["actions"][0]["action_type"] == "synchronize_metric"
```
