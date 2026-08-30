"""Tests for Data2DslSkill agent tool interface."""

from __future__ import annotations

import json
import pytest
from data2dsl_adapters import (
    Code2LogicMetricResponse,
    Code2SchemaMetricResponse,
    CurllmMetricResponse,
    CurllmPageEvidence,
)
from data2dsl_skill import Data2DslSkill, handle_mcp_message


@pytest.fixture
def base_query():
    return {
        "schema": "autogrammar.data2dsl/query/v0",
        "query_id": "skill-query-001",
        "subject": {
            "repository": "https://github.com/autogrammar/data2dsl",
            "actor": "antigravity",
        },
        "metric": {
            "id": "code.commit.count",
            "version": "1.0.0",
            "value_kind": "integer",
            "unit": "commits",
        },
        "window": {
            "start": "2026-08-10T00:00:00Z",
            "end": "2026-08-17T00:00:00Z",
            "semantics": "time-window-exact",
        },
        "left_source": {"id": "markdown-work-summary", "kind": "markdown-claim"},
        "right_source": {"id": "github-diagit-metrics", "kind": "github-metrics"},
        "comparison": {
            "equality": "exact",
            "delta_direction": "right-minus-left",
            "missing_is_zero": False,
        },
    }


def test_skill_tool_definitions():
    tools = Data2DslSkill.get_tool_definitions()
    assert len(tools) == 5
    tool_names = {t["name"] for t in tools}
    assert "data2dsl_compare" in tool_names
    assert "data2dsl_self_test" in tool_names
    assert "data2dsl_validate_envelope" in tool_names
    assert "data2dsl_simulate_healing" in tool_names
    assert "data2dsl_discover_data" in tool_names
    assert "data2dsl_self_test" in tool_names


def test_discover_data_builds_queryable_redacted_registry_graph():
    sources = [
        {
            "uri": "artifact://subactor/platform/config/artifact-registry.json/r1",
            "document": {
                "schema": "subactor.artifact-registry/v1",
                "artifacts": {
                    "supervisor": {
                        "canonical_uri": "artifact://subactor/supervisor/config.json/r2",
                        "schema_ref": "https://subactor.dev/schemas/supervisor.json",
                        "api_token": "must-not-leak",
                        "accessToken": "must-also-not-leak",
                        "callback_url": "https://example.invalid/callback?apiKey=hidden",
                    }
                },
            },
        },
        {
            "uri": "planfile://tickets/query/founder-work-status",
            "document": {
                "schema": "subactor.pull-request-controller-cycle/v1",
                "repositories": {
                    "subactor/supervisor": {
                        "strategy_ref": "strategy://subactor/repair/v1"
                    }
                },
            },
        },
    ]
    result = Data2DslSkill.execute_discover_data(sources, query="supervisor")
    assert result["status"] == "OK"
    graph = result["graph"]
    assert graph["schema"] == "autogrammar.data2dsl/data-network/v0"
    assert graph["summary"]["source_count"] == 2
    assert graph["summary"]["redacted_field_count"] == 3
    assert graph["nodes"] == sorted(graph["nodes"], key=lambda node: node["id"])
    assert "must-not-leak" not in json.dumps(graph)
    assert "must-also-not-leak" not in json.dumps(graph)
    assert "apiKey=hidden" not in json.dumps(graph)
    assert any(node["kind"] == "entity" for node in graph["nodes"])
    assert any(edge["relation"] == "references" for edge in graph["edges"])


def test_discover_data_is_deterministic_and_bounded():
    sources = [{"uri": "repo://subactor/registry", "document": {"entries": {"a": {"uri": "knowledge://subactor/a/v1"}}}}]
    left = Data2DslSkill.execute_discover_data(sources)
    right = Data2DslSkill.execute_discover_data(sources)
    assert left == right
    rejected = Data2DslSkill.execute_discover_data(sources * 33)
    assert rejected["status"] == "ERROR"
    assert rejected["error_code"] == "DISCOVERY_INVALID"

    duplicate = Data2DslSkill.execute_discover_data(sources * 2)
    assert duplicate["status"] == "ERROR"
    assert "source_uri_duplicate" in duplicate["message"]


def test_discover_data_is_callable_over_mcp():
    response = handle_mcp_message({
        "jsonrpc": "2.0",
        "id": 73,
        "method": "tools/call",
        "params": {
            "name": "data2dsl_discover_data",
            "arguments": {
                "sources": [{
                    "uri": "repo://subactor/supervisor",
                    "document": {"routes": {"repair": {"uri": "strategy://repair/v1"}}},
                }],
                "query": "repair",
            },
        },
    })
    assert response is not None
    payload = json.loads(response["result"]["content"][0]["text"])
    assert payload["status"] == "OK"
    assert payload["graph"]["summary"]["node_count"] >= 2


def test_discover_data_selects_bounded_operational_bottlenecks_from_list_records():
    sources = [{
        "uri": "artifact://subactor/pr-controller/last-cycle/r1",
        "document": {
            "pull_requests": [
                {
                    "repository": "maskservice/update",
                    "pull_request": 38,
                    "action": "repair_failed",
                    "child_state": "failed",
                    "child_error": "repository_not_allowlisted",
                    "head": "must-not-be-an-attribute",
                    "api_token": "sk-secret-secret-secret-secret",
                },
                {
                    "repository": "subactor/core",
                    "pull_request": 252,
                    "action": "repair_in_progress",
                    "child_state": "ready",
                },
            ]
        },
    }]
    result = Data2DslSkill.execute_discover_data(
        sources, query=["failed", "usage_limit", "blocked"]
    )
    assert result["status"] == "OK"
    graph = result["graph"]
    entities = [node for node in graph["nodes"] if node["kind"] == "entity"]
    assert len(entities) == 1
    assert entities[0]["label"] == "repository:maskservice/update"
    assert entities[0]["attributes"] == {
        "action": "repair_failed",
        "child_error": "repository_not_allowlisted",
        "child_state": "failed",
        "pull_request": 38,
        "repository": "maskservice/update",
    }
    serialized = json.dumps(graph)
    assert "must-not-be-an-attribute" not in serialized
    assert "sk-secret-secret-secret-secret" not in serialized
    assert "subactor/core" not in serialized


@pytest.mark.parametrize(
    "query",
    [["ok"] * 17, [""], ["x" * 81], [1], {"term": "failed"}],
)
def test_discover_data_rejects_invalid_bottleneck_queries(query):
    result = Data2DslSkill.execute_discover_data(
        [{"uri": "repo://subactor/core", "document": {"repositories": []}}],
        query=query,
    )
    assert result["status"] == "ERROR"
    assert result["error_code"] == "DISCOVERY_INVALID"


def test_discover_data_drops_secret_shaped_and_unbounded_operational_values():
    source = {
        "uri": "repo://subactor/coding-agent",
        "document": {"providers": {"codex": {
            "status": "sk-secret-secret-secret-secret",
            "queue_depth": 2**80,
            "provider": "codex",
        }}},
    }
    result = Data2DslSkill.execute_discover_data([source], query="codex")
    assert result["status"] == "OK"
    entity = next(node for node in result["graph"]["nodes"] if node["kind"] == "entity")
    assert entity["attributes"] == {"provider": "codex"}
    assert "sk-secret-secret-secret-secret" not in json.dumps(result)


def test_skill_self_test():
    res = Data2DslSkill.self_test()
    assert res["status"] == "PASS"
    assert res["skill"] == "autogrammar.data2dsl"
    assert res["version"] == "0.1.0"


def test_skill_execute_compare_raw_markdown_and_github_match(base_query):
    md_content = "# Summary\n\n- @antigravity commits: 10 in 2026-08-10..2026-08-17\n"
    res = Data2DslSkill.execute_compare(
        query=base_query,
        left_raw={"markdown_content": md_content, "path": "work-summary.md"},
        left_source_type="markdown",
        right_raw={"commit_count": 10},
        right_source_type="github",
    )
    assert res["status"] == "OK"
    assert res["result"]["outcome"] == "MATCH"
    assert res["result"]["delta"] is None


def test_skill_execute_compare_raw_markdown_and_github_conflict(base_query):
    md_content = "# Summary\n\n- @antigravity commits: 12 in 2026-08-10..2026-08-17\n"
    res = Data2DslSkill.execute_compare(
        query=base_query,
        left_raw={"markdown_content": md_content, "path": "work-summary.md"},
        left_source_type="markdown",
        right_raw={"commit_count": 10},
        right_source_type="github",
    )
    assert res["status"] == "OK"
    assert res["result"]["outcome"] == "CONFLICT"
    assert res["result"]["delta"]["kind"] == "integer"
    assert res["result"]["delta"]["value"] == "-2"


def test_skill_execute_compare_raw_curllm(base_query):
    ev = CurllmPageEvidence(
        url="https://github.com/autogrammar/data2dsl/pulse",
        digest_sha256="abc123def456",
    )
    resp = CurllmMetricResponse(status="OK", value=8, pages=(ev,))

    res = Data2DslSkill.execute_compare(
        query=base_query,
        left_raw={"response": resp},
        left_source_type="curllm",
        right_raw={"response": resp},
        right_source_type="curllm",
    )
    assert res["status"] == "OK"
    assert res["result"]["outcome"] == "MATCH"


def test_skill_execute_compare_raw_curllm_unevaluable(base_query):
    ev = CurllmPageEvidence(
        url="https://github.com/autogrammar/data2dsl/pulse",
        digest_sha256="abc123def456",
    )
    resp = CurllmMetricResponse(status="OK", value=8, pages=(ev,))
    err_resp = CurllmMetricResponse(status="ERROR", value=None, error_message="Page not reachable")

    res = Data2DslSkill.execute_compare(
        query=base_query,
        left_raw={"response": resp},
        left_source_type="curllm",
        right_raw={"response": err_resp},
        right_source_type="curllm",
    )
    assert res["status"] == "OK"
    assert res["result"]["outcome"] == "UNEVALUABLE"


def test_skill_execute_compare_raw_code2logic(base_query):
    resp = Code2LogicMetricResponse(status="OK", value=15)
    res = Data2DslSkill.execute_compare(
        query=base_query,
        left_raw={"response": resp},
        left_source_type="code2logic",
        right_raw={"value": 15},
        right_source_type="code2logic",
    )
    assert res["status"] == "OK"
    assert res["result"]["outcome"] == "MATCH"


def test_skill_execute_compare_raw_code2schema(base_query):
    schema_query = dict(base_query)
    schema_query["metric"] = {
        "id": "schema.entities",
        "version": "1.0.0",
        "value_kind": "string-set",
        "unit": "entities",
    }
    resp1 = Code2SchemaMetricResponse(status="OK", entities=["User", "Account"])
    resp2 = Code2SchemaMetricResponse(status="OK", entities=["User", "Account", "Order"])

    res = Data2DslSkill.execute_compare(
        query=schema_query,
        left_raw={"response": resp1},
        left_source_type="code2schema",
        right_raw={"response": resp2},
        right_source_type="code2schema",
    )
    assert res["status"] == "OK"
    assert res["result"]["outcome"] == "CONFLICT"
    assert res["result"]["delta"]["kind"] == "string-set"
    assert res["result"]["delta"]["added"] == ["Order"]
    assert res["result"]["delta"]["removed"] == []


def test_skill_execute_compare_missing_inputs(base_query):
    res_no_left = Data2DslSkill.execute_compare(
        query=base_query,
        right_raw={"commit_count": 10},
        right_source_type="github",
    )
    assert res_no_left["status"] == "ERROR"
    assert res_no_left["error_code"] == "MISSING_LEFT_OBSERVATION"

    res_no_right = Data2DslSkill.execute_compare(
        query=base_query,
        left_raw={"commit_count": 10},
        left_source_type="github",
    )
    assert res_no_right["status"] == "ERROR"
    assert res_no_right["error_code"] == "MISSING_RIGHT_OBSERVATION"


def test_skill_execute_compare_unknown_adapter_type(base_query):
    res = Data2DslSkill.execute_compare(
        query=base_query,
        left_raw={"val": 10},
        left_source_type="unsupported_source",
        right_raw={"commit_count": 10},
        right_source_type="github",
    )
    assert res["status"] == "ERROR"
    assert res["error_code"] == "COMPARISON_EXCEPTION"
    assert "Unknown source adapter kind" in res["message"]


def test_skill_execute_compare_raw_planfile(base_query):
    res = Data2DslSkill.execute_compare(
        query=base_query,
        left_raw={"count": 5},
        left_source_type="planfile",
        right_raw={"count": 7},
        right_source_type="planfile",
    )
    assert res["status"] == "OK"
    assert res["result"]["outcome"] == "CONFLICT"
    assert res["result"]["delta"]["kind"] == "integer"
    assert res["result"]["delta"]["value"] == "2"


def test_skill_execute_compare_raw_deta(base_query):
    res = Data2DslSkill.execute_compare(
        query=base_query,
        left_raw={"service_count": 3},
        left_source_type="deta",
        right_raw={"value": 3},
        right_source_type="deta",
    )
    assert res["status"] == "OK"
    assert res["result"]["outcome"] == "MATCH"


def test_skill_execute_compare_raw_intent_contract(base_query):
    contract_query = dict(base_query)
    contract_query["metric"] = {
        "id": "contract.deliverables",
        "version": "1.0.0",
        "value_kind": "string-set",
        "property": "deliverables",
    }
    res = Data2DslSkill.execute_compare(
        query=contract_query,
        left_raw={"deliverables": ["doc.pdf", "app.py"]},
        left_source_type="intent_contract",
        right_raw={"deliverables": ["doc.pdf", "app.py"]},
        right_source_type="intent-contract",
    )
    assert res["status"] == "OK"
    assert res["result"]["outcome"] == "MATCH"


def test_urirun_bindings(base_query):
    from data2dsl_skill import urirun_bindings

    bindings = urirun_bindings()
    assert bindings["scheme"] == "data2dsl"
    assert "data2dsl://host/compare/run" in bindings["routes"]
    assert "data2dsl://host/selftest/run" in bindings["routes"]

    # Test selftest route
    selftest_res = bindings["handler"]("data2dsl://host/selftest/run", {})
    assert selftest_res["status"] == "PASS"

    # Test compare route
    compare_res = bindings["handler"](
        "data2dsl://host/compare/run",
        {
            "query": base_query,
            "left_raw": {"commit_count": 10},
            "left_source_type": "github",
            "right_raw": {"commit_count": 10},
            "right_source_type": "github",
        },
    )
    assert compare_res["status"] == "OK"
    assert compare_res["result"]["outcome"] == "MATCH"


def test_handle_mcp_message_protocol(base_query):
    import json
    from data2dsl_skill import handle_mcp_message

    # Test initialize
    init_req = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
    init_resp = handle_mcp_message(init_req)
    assert init_resp["result"]["serverInfo"]["name"] == "data2dsl"
    assert init_resp["result"]["protocolVersion"] == "2024-11-05"

    # Test tools/list
    list_req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
    list_resp = handle_mcp_message(list_req)
    tool_names = [t["name"] for t in list_resp["result"]["tools"]]
    assert "data2dsl_compare" in tool_names
    assert "data2dsl_self_test" in tool_names

    # Test tools/call data2dsl_self_test
    call_test_req = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {"name": "data2dsl_self_test", "arguments": {}},
    }
    call_test_resp = handle_mcp_message(call_test_req)
    content = json.loads(call_test_resp["result"]["content"][0]["text"])
    assert content["status"] == "PASS"

    # Test tools/call data2dsl_compare
    call_comp_req = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "data2dsl_compare",
            "arguments": {
                "query": base_query,
                "left_raw": {"commit_count": 5},
                "left_source_type": "github",
                "right_raw": {"commit_count": 5},
                "right_source_type": "github",
            },
        },
    }
    call_comp_resp = handle_mcp_message(call_comp_req)
    comp_content = json.loads(call_comp_resp["result"]["content"][0]["text"])
    assert comp_content["status"] == "OK"
    assert comp_content["result"]["outcome"] == "MATCH"

    # Test unknown method
    unknown_req = {"jsonrpc": "2.0", "id": 5, "method": "unknown/method"}
    unknown_resp = handle_mcp_message(unknown_req)
    assert "error" in unknown_resp
    assert unknown_resp["error"]["code"] == -32601


def test_skill_execute_compare_raw_oql(base_query):
    oql_query = dict(base_query)
    oql_query["metric"] = {
        "id": "device.sensor.sample_rate",
        "version": "1.0.0",
        "value_kind": "float",
        "property": "sample_rate",
    }
    res = Data2DslSkill.execute_compare(
        query=oql_query,
        left_raw={"sample_rate": 100.0, "kind": "spec"},
        left_source_type="oql",
        right_raw={"sample_rate": 100.0, "kind": "telemetry"},
        right_source_type="oqlos",
    )
    assert res["status"] == "OK"
    assert res["result"]["outcome"] == "MATCH"


def test_mcp_oql_compare(base_query):
    oql_query = dict(base_query)
    oql_query["metric"] = {
        "id": "device.thermal.max_celsius",
        "version": "1.0.0",
        "value_kind": "float",
        "property": "celsius",
    }
    req = {
        "jsonrpc": "2.0",
        "id": 10,
        "method": "tools/call",
        "params": {
            "name": "data2dsl_compare",
            "arguments": {
                "query": oql_query,
                "left_raw": {"temperature": 75.0, "kind": "spec"},
                "left_source_type": "oql_spec",
                "right_raw": {"temperature": 82.5, "kind": "telemetry"},
                "right_source_type": "oql_telemetry",
            },
        },
    }
    resp = handle_mcp_message(req)
    content = json.loads(resp["result"]["content"][0]["text"])
    assert content["status"] == "OK"
    assert content["result"]["outcome"] == "CONFLICT"
    assert content["result"]["delta"] == {"kind": "float", "value": "7.5"}


def test_skill_execute_compare_raw_sumd(base_query):
    sumd_query = dict(base_query)
    sumd_query["metric"] = {
        "id": "tasks_completed",
        "version": "1.0.0",
        "value_kind": "integer",
        "unit": "tasks",
    }
    sumd_markdown = "| metric | value |\n| tasks_completed | 10 |\n"
    res = Data2DslSkill.execute_compare(
        query=sumd_query,
        left_raw={"markdown_content": sumd_markdown},
        left_source_type="sumd",
        right_raw={"markdown_content": sumd_markdown},
        right_source_type="sumd",
    )
    assert res["status"] == "OK"
    assert res["result"]["outcome"] == "MATCH"


def test_mcp_validate_envelope():
    envelope_text = (
        "ROLE: supervisor\n"
        "GOAL: Fix discrepancy\n"
        "SCOPE: test scope\n"
        "ACCEPTANCE: all match\n"
        "AUTHORITY: observe, plan\n"
        "LIMITS: no secrets\n"
        "REPORT: ticket-052\n"
    )
    req = {
        "jsonrpc": "2.0",
        "id": 11,
        "method": "tools/call",
        "params": {
            "name": "data2dsl_validate_envelope",
            "arguments": {
                "envelope": envelope_text,
            },
        },
    }
    resp = handle_mcp_message(req)
    assert resp is not None
    content = json.loads(resp["result"]["content"][0]["text"])
    assert content["status"] == "OK"
    assert content["envelope"]["valid"] is True
    assert content["envelope"]["role"] == "supervisor"


def test_mcp_simulate_healing(base_query):
    left = {
        "schema": "autogrammar.data2dsl/observation/v0",
        "observation_id": "obs:1",
        "side": "left",
        "subject": base_query["subject"],
        "metric": base_query["metric"],
        "window": base_query["window"],
        "state": "OBSERVED",
        "value": {"kind": "integer", "value": "10"},
        "evidence": [{"evidence_id": "ev:1", "digest_sha256": "1111", "source_uri": "uri:1", "source_revision": "sha256:1111"}],
    }
    right = {
        "schema": "autogrammar.data2dsl/observation/v0",
        "observation_id": "obs:2",
        "side": "right",
        "subject": base_query["subject"],
        "metric": base_query["metric"],
        "window": base_query["window"],
        "state": "OBSERVED",
        "value": {"kind": "integer", "value": "8"},
        "evidence": [{"evidence_id": "ev:2", "digest_sha256": "2222", "source_uri": "uri:2", "source_revision": "sha256:2222"}],
    }

    req = {
        "jsonrpc": "2.0",
        "id": 12,
        "method": "tools/call",
        "params": {
            "name": "data2dsl_simulate_healing",
            "arguments": {
                "query": base_query,
                "left_observation": left,
                "right_observation": right,
            },
        },
    }
    resp = handle_mcp_message(req)
    assert resp is not None
    content = json.loads(resp["result"]["content"][0]["text"])
    assert content["status"] == "OK"
    assert content["healing_result"]["status"] == "HEALED"
    assert content["healing_result"]["closed_loop_verification"]["is_clean"] is True


def test_urirun_bindings_subactor():
    from data2dsl_skill import urirun_bindings

    bindings = urirun_bindings()
    assert "data2dsl://host/subactor/validate" in bindings["routes"]
    assert "data2dsl://host/healing/simulate" in bindings["routes"]

    # Test route validate
    envelope_text = (
        "ROLE: supervisor\n"
        "GOAL: Fix discrepancy\n"
        "SCOPE: test scope\n"
        "ACCEPTANCE: all match\n"
        "AUTHORITY: observe, plan\n"
        "LIMITS: no secrets\n"
        "REPORT: ticket-052\n"
    )
    val_res = bindings["handler"]("data2dsl://host/subactor/validate", {"envelope": envelope_text})
    assert val_res["status"] == "OK"
    assert val_res["envelope"]["valid"] is True
