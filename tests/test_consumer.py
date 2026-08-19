from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from data2dsl_adapters import DiagitCommitMetricResponse, GitHubDiagitAdapter, WorkSummaryMarkdownAdapter
from data2dsl_cli import main
from data2dsl_comparator import compare_observations
from data2dsl_consumer import ConsumerFactFeed, ReasoningFactPayload


def _create_golden_bundle(outcome_expected: str = "MATCH") -> dict[str, Any]:
    md_content = """# Work Summary

| Person | Commits |
| :--- | :--- |
| Alice | 10 |
"""
    commit_count = 10 if outcome_expected == "MATCH" else 12
    diagit_resp = DiagitCommitMetricResponse(
        status="OK",
        commit_count=commit_count,
        error_message=None,
    )

    query = {
        "schema": "autogrammar.data2dsl/query/v0",
        "query_id": "query:test:consumer",
        "subject": {
            "repository": "https://github.com/autogrammar/data2dsl",
            "actor": "github:alice",
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
        "left_source": {"id": "source:markdown", "kind": "markdown"},
        "right_source": {"id": "source:github", "kind": "github"},
        "comparison": {
            "equality": "integer-exact",
            "delta_direction": "right-minus-left",
            "missing_is_zero": False,
        },
    }

    md_adapter = WorkSummaryMarkdownAdapter()
    claim = md_adapter.extract_commit_claim(
        markdown_text=md_content,
        actor="alice",
        path="work-summary.md",
        repository_uri="https://github.com/autogrammar/data2dsl",
    )
    left_obs = md_adapter.normalize(query, claim, side="left")
    right_obs = GitHubDiagitAdapter().normalize(query, diagit_resp, side="right")

    return compare_observations(query, left_obs, right_obs)


def test_export_reasoning_payload_match():
    bundle = _create_golden_bundle("MATCH")
    payload = ConsumerFactFeed.export_reasoning_payload(bundle)

    assert isinstance(payload, ReasoningFactPayload)
    assert payload.schema == "autogrammar.data2dsl/consumer-fact-feed/v0"
    assert payload.outcome == "MATCH"
    assert payload.delta is None
    assert payload.left_summary["value"] == {"kind": "integer", "value": "10"}
    assert payload.right_summary["value"] == {"kind": "integer", "value": "10"}
    assert len(payload.evidence) == 2
    assert payload.factual_digest.startswith("sha256:")

    d = payload.to_dict()
    assert d["schema"] == ConsumerFactFeed.FEED_SCHEMA
    assert d["outcome"] == "MATCH"
    assert len(d["evidence"]) == 2


def test_export_reasoning_payload_conflict():
    bundle = _create_golden_bundle("CONFLICT")
    payload = ConsumerFactFeed.export_reasoning_payload(bundle)

    assert payload.outcome == "CONFLICT"
    assert payload.delta == {"kind": "integer", "value": "2"}
    assert payload.left_summary["value"] == {"kind": "integer", "value": "10"}
    assert payload.right_summary["value"] == {"kind": "integer", "value": "12"}


def test_cli_feed_consumer(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    bundle = _create_golden_bundle("CONFLICT")
    bundle_path = tmp_path / "bundle.json"
    bundle_path.write_text(json.dumps(bundle), encoding="utf-8")

    out_path = tmp_path / "feed.json"
    exit_code = main(["feed-consumer", "--bundle", str(bundle_path), "--output", str(out_path)])
    assert exit_code == 0
    assert out_path.exists()

    feed_data = json.loads(out_path.read_text(encoding="utf-8"))
    assert feed_data["schema"] == "autogrammar.data2dsl/consumer-fact-feed/v0"
    assert feed_data["outcome"] == "CONFLICT"
    assert feed_data["delta"] == {"kind": "integer", "value": "2"}
