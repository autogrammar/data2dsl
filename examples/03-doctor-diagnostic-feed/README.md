# 03-doctor-diagnostic-feed

Demonstrates exporting a `data2dsl` comparison bundle to a `new-project.diagnostic-profile/v1` schema document consumed by `subactor/doctor-agent` for root-cause triage.

## Fixtures

- `bundle.json`: A comparison bundle containing thermal discrepancy.
- `expected-diagnostic-profile.json`: Formatted diagnostic profile with classified symptom severity (`HIGH`), delta summary, and diagnostic notes.

## Running via CLI and Python API

```bash
# Via CLI
python src/data2dsl_cli.py feed-doctor -b bundle.json -o diagnostic_profile.json
```

```python
# Via Python API
from data2dsl_doctor import format_diagnostic_profile

profile = format_diagnostic_profile(bundle)
assert profile["severity_summary"]["high"] >= 1
```
