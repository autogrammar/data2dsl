# Data2DSL Examples

This directory provides simple, runnable examples demonstrating the multi-source normalization, deterministic comparison, feed formatting, and tool dispatch capabilities of `data2dsl`.

## Example Index

| Number | Example | Sources / Scope | Description |
|---|---|---|---|
| **01** | [`01-markdown-github-comparison`](01-markdown-github-comparison/) | Markdown vs GitHub Commits | Factual claim verification comparing documented commit metrics against GitHub API observations. |
| **02** | [`02-oql-telemetry-verification`](02-oql-telemetry-verification/) | OQL Spec vs Sensor Telemetry | Hardware-in-the-loop (HIL) verification comparing declared operating specs against sensor logs. |
| **03** | [`03-doctor-diagnostic-feed`](03-doctor-diagnostic-feed/) | Comparison Bundle $\to$ Doctor Agent | Transforming discrepancies into a prioritized `diagnostic-profile/v1` for triage agents. |
| **04** | [`04-koru-remediation-feed`](04-koru-remediation-feed/) | Comparison Bundle $\to$ Koru Feed | Generating machine-actionable `remediation-intent/v1` payloads for closed-loop self-healing. |
| **05** | [`05-mcp-tool-dispatch`](05-mcp-tool-dispatch/) | JSON-RPC 2.0 / MCP | Invoking `data2dsl_compare` over Model Context Protocol (MCP). |
| **06** | [`06-closed-loop-self-healing`](06-closed-loop-self-healing/) | Subactor Envelope & Closed Loop | Complete 5-stage closed loop (`DETECT` -> `PLAN` -> `EXECUTE` -> `VERIFY` -> `HEAL`) with envelope validation. |

## Running Examples with CLI

```bash
# Example 01: Compare two observations
python src/data2dsl_cli.py compare -l obs_left.json -r obs_right.json -q query.json

# Example 03: Export Doctor Agent Diagnostic Profile
python src/data2dsl_cli.py feed-doctor -b comparison_bundle.json -o diagnostic_profile.json

# Example 04: Export Koru Remediation Intent
python src/data2dsl_cli.py feed-koru -b comparison_bundle.json -o remediation_intent.json
```
