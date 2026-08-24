# Ticket Changelog (ticket-039)

## [0.1.0] - 2026-08-24

- Created `src/connector.manifest.json` exposing `data2dsl` as an `if-uri` connector for `data2dsl://` routes.
- Implemented `urirun_bindings` in `src/data2dsl_skill.py` supporting `data2dsl://host/compare/run` and `data2dsl://host/selftest/run`.
- Implemented JSON-RPC 2.0 MCP server handler `handle_mcp_message` and `main_mcp` runner in `src/data2dsl_skill.py`.
- Added unit tests `test_urirun_bindings` and `test_handle_mcp_message_protocol` in `tests/test_skill.py` (35 total passing).
- Verified deterministic governance gate passes.
