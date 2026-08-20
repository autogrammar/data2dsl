"""Comprehensive unit and end-to-end golden case tests."""

from __future__ import annotations

from typing import Any
import pytest

from data2dsl_adapters import (
    CurllmAdapter,
    CurllmMetricResponse,
    CurllmPageEvidence,
    DiagitCommitMetricResponse,
    DiagitPageEvidence,
    GitHubDiagitAdapter,
    WorkSummaryMarkdownAdapter,
    build_github_commit_observation,
    compute_sha256,
)
from data2dsl_comparator import compare_observations
from data2dsl_contract_v0.validate import validate_document


@pytest.fixture
def golden_query() -> dict[str, Any]:
    return {
        "schema": "autogrammar.data2dsl/query/v0",
        "query_id": "query:work-summary:week-2026-08-10",
        "subject": {
            "repository": "https://github.com/autogrammar/data2dsl",
            "actor": "github:matthiaslew",
        },
        "metric": {
            "id": "git.commit.count",
            "version": "v1",
            "value_kind": "integer",
            "unit": "count",
        },
        "window": {
            "start": "2026-08-10T00:00:00Z",
            "end": "2026-08-17T00:00:00Z",
            "semantics": "half-open-utc",
        },
        "left_source": {"id": "source:work-summary", "kind": "markdown"},
        "right_source": {"id": "source:github", "kind": "github"},
        "comparison": {
            "equality": "integer-exact",
            "delta_direction": "right-minus-left",
            "missing_is_zero": False,
        },
    }


def test_github_adapter_valid_and_unevaluable(golden_query: dict[str, Any]) -> None:
    page_digest = compute_sha256(b'[{"sha": "abc"}]')
    page = DiagitPageEvidence(
        page=1,
        endpoint="/repos/autogrammar/data2dsl/commits",
        digest_sha256=page_digest,
        source_revision=f"sha256:{page_digest}",
        source_uri="https://api.github.com/repos/autogrammar/data2dsl/commits?page=1",
    )
    response = DiagitCommitMetricResponse(
        status="OK",
        commit_count=10,
        pages=[page],
    )
    adapter = GitHubDiagitAdapter()
    obs = adapter.normalize(golden_query, response, side="right", observation_id="observation:github:10")

    assert obs["schema"] == "autogrammar.data2dsl/observation/v0"
    assert obs["state"] == "OBSERVED"
    assert obs["value"] == {"kind": "integer", "value": "10"}
    assert len(obs["evidence"]) == 1
    assert obs["evidence"][0]["digest_sha256"] == page_digest

    err_response = DiagitCommitMetricResponse(status="ERROR", commit_count=None, error_message="Rate limited")
    err_obs = adapter.normalize(golden_query, err_response, side="right")
    assert err_obs["state"] == "UNEVALUABLE"
    assert err_obs["value"] is None
    assert len(err_obs["evidence"]) == 1


def test_markdown_adapter_valid_and_missing(golden_query: dict[str, Any]) -> None:
    markdown_doc = "# Summary\n- matthiaslew: 12 commits\n"
    md_adapter = WorkSummaryMarkdownAdapter()
    claim = md_adapter.extract_commit_claim(markdown_doc, "github:matthiaslew")
    assert claim is not None
    assert claim.value == 12

    obs = md_adapter.normalize(golden_query, claim, side="left", observation_id="observation:claim:12")
    assert obs["state"] == "OBSERVED"
    assert obs["value"] == {"kind": "integer", "value": "12"}
    assert len(obs["evidence"]) == 1

    missing_claim = md_adapter.extract_commit_claim("# Empty\n", "github:matthiaslew")
    assert missing_claim is None
    uneval_obs = md_adapter.normalize(golden_query, missing_claim, side="left")
    assert uneval_obs["state"] == "UNEVALUABLE"
    assert uneval_obs["value"] is None


def test_golden_case_conflict(golden_query: dict[str, Any]) -> None:
    markdown_doc = "# Summary\n- matthiaslew: 12 commits\n"
    md_adapter = WorkSummaryMarkdownAdapter()
    claim = md_adapter.extract_commit_claim(markdown_doc, "github:matthiaslew")
    left_obs = md_adapter.normalize(golden_query, claim, side="left", observation_id="observation:claim:12")

    page_digest = compute_sha256(b"commits:10")
    page = DiagitPageEvidence(
        page=1,
        endpoint="/repos/autogrammar/data2dsl/commits",
        digest_sha256=page_digest,
        source_revision=f"sha256:{page_digest}",
        source_uri="https://api.github.com/repos/autogrammar/data2dsl/commits",
    )
    gh_response = DiagitCommitMetricResponse(status="OK", commit_count=10, pages=[page])
    gh_adapter = GitHubDiagitAdapter()
    right_obs = gh_adapter.normalize(golden_query, gh_response, side="right", observation_id="observation:github:10")

    bundle = compare_observations(golden_query, left_obs, right_obs)

    assert bundle["result"]["outcome"] == "CONFLICT"
    assert bundle["result"]["delta"] == {"kind": "integer", "value": "-2"}
    assert len(bundle["result"]["evidence_ids"]) == 2
    validate_document(bundle)


def test_golden_case_match(golden_query: dict[str, Any]) -> None:
    markdown_doc = "# Summary\n- matthiaslew: 10 commits\n"
    md_adapter = WorkSummaryMarkdownAdapter()
    claim = md_adapter.extract_commit_claim(markdown_doc, "github:matthiaslew")
    left_obs = md_adapter.normalize(golden_query, claim, side="left", observation_id="observation:claim:10")

    gh_response = DiagitCommitMetricResponse(status="OK", commit_count=10)
    gh_adapter = GitHubDiagitAdapter()
    right_obs = gh_adapter.normalize(golden_query, gh_response, side="right", observation_id="observation:github:10")

    bundle = compare_observations(golden_query, left_obs, right_obs)

    assert bundle["result"]["outcome"] == "MATCH"
    assert bundle["result"]["delta"] is None
    validate_document(bundle)


def test_golden_case_missing_and_unevaluable(golden_query: dict[str, Any]) -> None:
    gh_response = DiagitCommitMetricResponse(status="OK", commit_count=10)
    gh_adapter = GitHubDiagitAdapter()
    right_obs = gh_adapter.normalize(golden_query, gh_response, side="right")

    bundle_missing_left = compare_observations(golden_query, None, right_obs)
    assert bundle_missing_left["result"]["outcome"] == "MISSING_LEFT"
    validate_document(bundle_missing_left)

    right_as_left = dict(right_obs, side="left")
    bundle_missing_right = compare_observations(golden_query, right_as_left, None)
    assert bundle_missing_right["result"]["outcome"] == "MISSING_RIGHT"
    validate_document(bundle_missing_right)

    err_response = DiagitCommitMetricResponse(status="ERROR", commit_count=None)
    err_obs = gh_adapter.normalize(golden_query, err_response, side="right")
    bundle_uneval = compare_observations(golden_query, right_as_left, err_obs)
    assert bundle_uneval["result"]["outcome"] == "UNEVALUABLE"
    validate_document(bundle_uneval)


def test_code2logic_adapter(golden_query: dict[str, Any]) -> None:
    from data2dsl_adapters import Code2LogicAdapter, Code2LogicMetricResponse

    query = dict(golden_query, metric={"id": "code.function.count", "version": "v1", "value_kind": "integer", "unit": "count"})
    resp = Code2LogicMetricResponse(status="OK", value=15, value_kind="integer", path="src/core.py", start_line=1, end_line=100)
    adapter = Code2LogicAdapter()
    obs = adapter.normalize(query, resp, side="right", observation_id="observation:code2logic:15")

    assert obs["state"] == "OBSERVED"
    assert obs["value"] == {"kind": "integer", "value": "15"}
    assert len(obs["evidence"]) == 1
    assert obs["evidence"][0]["extractor"]["id"] == "semcod.code2logic"


def test_code2schema_adapter(golden_query: dict[str, Any]) -> None:
    from data2dsl_adapters import Code2SchemaAdapter, Code2SchemaMetricResponse

    query = dict(
        golden_query,
        metric={"id": "schema.entities.set", "version": "v1", "value_kind": "string-set"},
        comparison={"equality": "string-set-exact", "delta_direction": "right-minus-left", "missing_is_zero": False},
    )
    resp = Code2SchemaMetricResponse(status="OK", entities=["User", "Order", "Item"], path="src/models.py")
    adapter = Code2SchemaAdapter()
    obs = adapter.normalize(query, resp, side="right", observation_id="observation:code2schema:entities")

    assert obs["state"] == "OBSERVED"
    assert obs["value"] == {"kind": "string-set", "items": ["Item", "Order", "User"]}
    assert len(obs["evidence"]) == 1
    assert obs["evidence"][0]["extractor"]["id"] == "semcod.code2schema"


def test_curllm_adapter_valid_and_unevaluable(golden_query: dict[str, Any]) -> None:
    adapter = CurllmAdapter()

    # Valid response
    page = CurllmPageEvidence(
        url="https://github.com/autogrammar/data2dsl",
        digest_sha256="4" * 64,
        page=1,
        endpoint="https://github.com/autogrammar/data2dsl",
    )
    resp = CurllmMetricResponse(
        status="OK",
        value=10,
        pages=[page],
    )
    obs = adapter.normalize(golden_query, resp, side="right")
    assert obs["state"] == "OBSERVED"
    assert obs["value"] == {"kind": "integer", "value": "10"}
    assert len(obs["evidence"]) == 1
    assert obs["evidence"][0]["extractor"]["id"] == "semcod.curllm"
    assert obs["evidence"][0]["digest_sha256"] == "4" * 64

    # Unevaluable response on error/timeout
    resp_err = CurllmMetricResponse(status="TIMEOUT", error_message="page timed out")
    obs_err = adapter.normalize(golden_query, resp_err, side="right")
    assert obs_err["state"] == "UNEVALUABLE"
    assert obs_err["value"] is None
    assert obs_err["evidence"][0]["location"]["endpoint"] == "curllm-error"

