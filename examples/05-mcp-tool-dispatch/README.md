# 05-mcp-tool-dispatch

Demonstrates tool invocation using the JSON-RPC 2.0 Model Context Protocol (MCP) supported by `Data2DslSkill`.

## Fixtures

- `mcp-request.json`: Standard MCP `tools/call` message requesting `data2dsl_compare` with raw left and right payloads.
- `expected-mcp-response.json`: Expected MCP JSON-RPC response containing embedded comparison result text.

## Invocation Example in Python

```python
import json
from data2dsl_skill import handle_mcp_message

with open("mcp-request.json") as f:
    request = json.load(f)

response = handle_mcp_message(request)
content = json.loads(response["result"]["content"][0]["text"])
assert content["status"] == "OK"
assert content["result"]["outcome"] == "MATCH"
```
