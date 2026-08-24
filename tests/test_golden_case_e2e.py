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


def test_planfile_adapter_valid_and_unevaluable(golden_query: dict[str, Any]) -> None:
    from data2dsl_adapters import PlanfileAdapter, PlanfileMetricResponse, PlanfileTicketEvidence

    adapter = PlanfileAdapter()

    # Valid response with tickets
    t1 = PlanfileTicketEvidence(ticket_id="TICK-001", title="First ticket", status="DONE", path="planfile.yaml", start_line=5, end_line=10)
    t2 = PlanfileTicketEvidence(ticket_id="TICK-002", title="Second ticket", status="OPEN", path="planfile.yaml", start_line=12, end_line=18)
    resp = PlanfileMetricResponse(status="OK", tickets=[t1, t2], path="planfile.yaml")

    # Integer metric
    obs_int = adapter.normalize(golden_query, resp, side="right")
    assert obs_int["state"] == "OBSERVED"
    assert obs_int["value"] == {"kind": "integer", "value": "2"}
    assert len(obs_int["evidence"]) == 2
    assert obs_int["evidence"][0]["extractor"]["id"] == "semcod.planfile"

    # String-set metric
    query_set = dict(
        golden_query,
        metric={"id": "planfile.tickets.set", "version": "v1", "value_kind": "string-set"},
    )
    obs_set = adapter.normalize(query_set, resp, side="left")
    assert obs_set["state"] == "OBSERVED"
    assert obs_set["value"] == {"kind": "string-set", "items": ["TICK-001", "TICK-002"]}

    # Unevaluable response
    resp_err = PlanfileMetricResponse(status="NOT_FOUND", error_message="planfile.yaml missing")
    obs_err = adapter.normalize(golden_query, resp_err, side="right")
    assert obs_err["state"] == "UNEVALUABLE"
    assert obs_err["value"] is None


def test_deta_adapter_valid_and_unevaluable(golden_query: dict[str, Any]) -> None:
    from data2dsl_adapters import DetaAdapter, DetaServiceEvidence, DetaTopologyResponse

    adapter = DetaAdapter()

    s1 = DetaServiceEvidence(name="web", service_type="frontend", ports=["80", "443"], manifest_path="compose.yml")
    s2 = DetaServiceEvidence(name="api", service_type="backend", ports=["8080"], manifest_path="compose.yml")
    resp = DetaTopologyResponse(status="OK", services=[s1, s2], ports=["80", "443", "8080"], manifest_path="compose.yml")

    # Service count integer
    obs_srv = adapter.normalize(golden_query, resp, side="right")
    assert obs_srv["state"] == "OBSERVED"
    assert obs_srv["value"] == {"kind": "integer", "value": "2"}
    assert len(obs_srv["evidence"]) == 2
    assert obs_srv["evidence"][0]["extractor"]["id"] == "semcod.deta"

    # Exposed ports string-set
    query_ports = dict(
        golden_query,
        metric={"id": "infra.ports.set", "name": "exposed_ports", "version": "v1", "value_kind": "string-set"},
    )
    obs_ports = adapter.normalize(query_ports, resp, side="left")
    assert obs_ports["state"] == "OBSERVED"
    assert obs_ports["value"] == {"kind": "string-set", "items": ["443", "80", "8080"]}

    # Unevaluable response
    resp_err = DetaTopologyResponse(status="ERROR", error_message="compose syntax error")
    obs_err = adapter.normalize(golden_query, resp_err, side="right")
    assert obs_err["state"] == "UNEVALUABLE"
    assert obs_err["value"] is None


def test_intent_contract_adapter_valid_and_unevaluable(golden_query: dict[str, Any]) -> None:
    from data2dsl_adapters import IntentContractAdapter, IntentContractResponse

    adapter = IntentContractAdapter()

    resp = IntentContractResponse(
        status="OK",
        contract_id="contract-alpha",
        parties=["Alice", "Bob"],
        deliverables=["report.pdf", "code.zip"],
        obligations=["delivery_on_time", "quality_audit"],
        path="intent-contract.dsl.json",
    )

    # Deliverables set
    query_deliv = dict(
        golden_query,
        metric={"id": "contract.deliverables.set", "property": "deliverables", "version": "v1", "value_kind": "string-set"},
    )
    obs_deliv = adapter.normalize(query_deliv, resp, side="right")
    assert obs_deliv["state"] == "OBSERVED"
    assert obs_deliv["value"] == {"kind": "string-set", "items": ["code.zip", "report.pdf"]}
    assert len(obs_deliv["evidence"]) == 1
    assert obs_deliv["evidence"][0]["extractor"]["id"] == "subactor.intent-contract-dsl"

    # Parties count integer
    query_parties = dict(
        golden_query,
        metric={"id": "contract.parties.count", "property": "parties", "name": "party_count", "version": "v1", "value_kind": "integer"},
    )
    obs_parties = adapter.normalize(query_parties, resp, side="left")
    assert obs_parties["state"] == "OBSERVED"
    assert obs_parties["value"] == {"kind": "integer", "value": "2"}

    # Obligations set
    query_oblig = dict(
        golden_query,
        metric={"id": "contract.obligations.set", "property": "obligations", "version": "v1", "value_kind": "string-set"},
    )
    obs_oblig = adapter.normalize(query_oblig, resp, side="left")
    assert obs_oblig["state"] == "OBSERVED"
    assert obs_oblig["value"] == {"kind": "string-set", "items": ["delivery_on_time", "quality_audit"]}

    # Unevaluable response
    resp_err = IntentContractResponse(status="ERROR", error_message="invalid schema")
    obs_err = adapter.normalize(golden_query, resp_err, side="right")
    assert obs_err["state"] == "UNEVALUABLE"
    assert obs_err["value"] is None


def test_float_comparator_match_and_conflict(golden_query: dict[str, Any]) -> None:
    query_float = dict(
        golden_query,
        metric={"id": "code.cyclomatic.average", "version": "v1", "value_kind": "float", "unit": "score"},
        comparison={"equality": "float-exact", "delta_direction": "right-minus-left", "missing_is_zero": False},
    )

    ev_left = {
        "evidence_id": "evidence:left:1",
        "target_uri": "https://github.com/autogrammar/data2dsl",
        "source_uri": "https://github.com/autogrammar/data2dsl/blob/main/report.json",
        "source_revision": "sha256:" + "a" * 64,
        "media_type": "application/json",
        "digest_sha256": "a" * 64,
        "extractor": {"id": "semcod.code2llm", "version": "0.1.0"},
        "location": {"kind": "markdown-lines", "path": "report.json", "start_line": 1, "end_line": 10},
    }
    ev_right = {
        "evidence_id": "evidence:right:1",
        "target_uri": "https://github.com/autogrammar/data2dsl",
        "source_uri": "https://github.com/autogrammar/data2dsl/blob/main/actual.json",
        "source_revision": "sha256:" + "b" * 64,
        "media_type": "application/json",
        "digest_sha256": "b" * 64,
        "extractor": {"id": "semcod.code2llm", "version": "0.1.0"},
        "location": {"kind": "markdown-lines", "path": "actual.json", "start_line": 1, "end_line": 10},
    }

    obs_left = {
        "schema": "autogrammar.data2dsl/observation/v0",
        "observation_id": "obs:float:left",
        "query_id": query_float["query_id"],
        "side": "left",
        "subject": query_float["subject"],
        "metric": query_float["metric"],
        "window": query_float["window"],
        "state": "OBSERVED",
        "value": {"kind": "float", "value": "12.5"},
        "evidence": [ev_left],
    }

    # MATCH case
    obs_right_match = dict(obs_left, observation_id="obs:float:right:match", side="right", evidence=[ev_right])
    bundle_match = compare_observations(query_float, obs_left, obs_right_match)
    assert bundle_match["result"]["outcome"] == "MATCH"
    assert bundle_match["result"]["delta"] is None
    validate_document(bundle_match)

    # CONFLICT case: right (15.75) - left (12.5) = +3.25
    obs_right_conflict = dict(
        obs_left,
        observation_id="obs:float:right:conflict",
        side="right",
        value={"kind": "float", "value": "15.75"},
        evidence=[ev_right],
    )
    bundle_conflict = compare_observations(query_float, obs_left, obs_right_conflict)
    assert bundle_conflict["result"]["outcome"] == "CONFLICT"
    assert bundle_conflict["result"]["delta"] == {"kind": "float", "value": "3.25"}
    validate_document(bundle_conflict)


def test_percentage_comparator_match_and_conflict(golden_query: dict[str, Any]) -> None:
    query_pct = dict(
        golden_query,
        metric={"id": "test.coverage.percentage", "version": "v1", "value_kind": "percentage", "unit": "percentage"},
        comparison={"equality": "percentage-exact", "delta_direction": "right-minus-left", "missing_is_zero": False},
    )

    ev_left = {
        "evidence_id": "evidence:left:1",
        "target_uri": "https://github.com/autogrammar/data2dsl",
        "source_uri": "https://github.com/autogrammar/data2dsl/blob/main/report.json",
        "source_revision": "sha256:" + "c" * 64,
        "media_type": "application/json",
        "digest_sha256": "c" * 64,
        "extractor": {"id": "semcod.pyqual", "version": "0.1.0"},
        "location": {"kind": "markdown-lines", "path": "report.json", "start_line": 1, "end_line": 10},
    }
    ev_right = {
        "evidence_id": "evidence:right:1",
        "target_uri": "https://github.com/autogrammar/data2dsl",
        "source_uri": "https://github.com/autogrammar/data2dsl/blob/main/actual.json",
        "source_revision": "sha256:" + "d" * 64,
        "media_type": "application/json",
        "digest_sha256": "d" * 64,
        "extractor": {"id": "semcod.pyqual", "version": "0.1.0"},
        "location": {"kind": "markdown-lines", "path": "actual.json", "start_line": 1, "end_line": 10},
    }

    obs_left = {
        "schema": "autogrammar.data2dsl/observation/v0",
        "observation_id": "obs:pct:left",
        "query_id": query_pct["query_id"],
        "side": "left",
        "subject": query_pct["subject"],
        "metric": query_pct["metric"],
        "window": query_pct["window"],
        "state": "OBSERVED",
        "value": {"kind": "percentage", "value": "80.0%"},
        "evidence": [ev_left],
    }

    # MATCH case
    obs_right_match = dict(obs_left, observation_id="obs:pct:right:match", side="right", value={"kind": "percentage", "value": "80%"}, evidence=[ev_right])
    bundle_match = compare_observations(query_pct, obs_left, obs_right_match)
    assert bundle_match["result"]["outcome"] == "MATCH"
    assert bundle_match["result"]["delta"] is None
    validate_document(bundle_match)

    # CONFLICT case: right (95.5%) - left (80.0%) = +15.5%
    obs_right_conflict = dict(
        obs_left,
        observation_id="obs:pct:right:conflict",
        side="right",
        value={"kind": "percentage", "value": "95.5%"},
        evidence=[ev_right],
    )
    bundle_conflict = compare_observations(query_pct, obs_left, obs_right_conflict)
    assert bundle_conflict["result"]["outcome"] == "CONFLICT"
    assert bundle_conflict["result"]["delta"] == {"kind": "percentage", "value": "15.5%"}
    validate_document(bundle_conflict)


