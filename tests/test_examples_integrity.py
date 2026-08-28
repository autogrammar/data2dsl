"""Tests verifying integrity and contract validity of all examples 01 through 08 (F14)."""

import json
from pathlib import Path
from data2dsl_batch import BatchMultiQueryComparator
from data2dsl_contract_v0.validate import validate_document
from data2dsl_skill import handle_mcp_message


EXAMPLES_DIR = Path(__file__).parent.parent / "examples"


def test_example_01_bundle_validity():
    """F14: Example 01 bundle conforms to comparison-bundle schema."""
    p = EXAMPLES_DIR / "01-markdown-github-comparison" / "expected-bundle.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    validate_document(data)


def test_example_02_bundle_validity():
    """F14: Example 02 bundle conforms to comparison-bundle schema."""
    p = EXAMPLES_DIR / "02-oql-telemetry-verification" / "expected-bundle.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    validate_document(data)


def test_example_05_mcp_request_dispatch():
    """F14: Example 05 MCP request executes successfully without missing required fields error."""
    p = EXAMPLES_DIR / "05-mcp-tool-dispatch" / "mcp-request.json"
    req = json.loads(p.read_text(encoding="utf-8"))
    resp = handle_mcp_message(req)
    assert resp is not None
    assert "result" in resp
    content = resp["result"]["content"][0]["text"]
    result_data = json.loads(content)
    assert result_data["status"] == "OK"
    assert result_data["result"]["outcome"] == "MATCH"


def test_example_08_batch_multi_query_execution():
    """F14: Example 08 batch queries and observations execute and validate successfully."""
    q_path = EXAMPLES_DIR / "08-batch-multi-query" / "queries.json"
    l_path = EXAMPLES_DIR / "08-batch-multi-query" / "left-observations.json"
    r_path = EXAMPLES_DIR / "08-batch-multi-query" / "right-observations.json"

    queries = json.loads(q_path.read_text(encoding="utf-8"))
    left_obs = json.loads(l_path.read_text(encoding="utf-8"))
    right_obs = json.loads(r_path.read_text(encoding="utf-8"))

    batch_comp = BatchMultiQueryComparator()
    report = batch_comp.compare_batch(queries, left_obs, right_obs)
    assert report.summary.total_queries == 2
    assert report.summary.matches == 2
    assert report.summary.is_clean

    # Validate each produced comparison bundle against contract
    for b in report.bundles:
        validate_document(b)
