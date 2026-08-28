from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from data2dsl_cli import main as cli_main
from data2dsl_remediation import (
    RemediationIntentFormatter,
    format_remediation_intent,
)


def _make_evidence(eid: str, digest: str) -> Dict[str, Any]:
    return {
        "evidence_id": eid,
        "target_uri": "https://github.com/autogrammar/data2dsl",
        "source_uri": "https://github.com/autogrammar/data2dsl",
        "source_revision": "HEAD",
        "media_type": "application/json",
        "digest_sha256": digest,
        "extractor": {"id": "test:extractor", "version": "1.0"},
        "location": {"path": "work-summary.md"},
    }


def _make_bundle(
    outcome: str = "CONFLICT",
    delta: Dict[str, Any] | None = None,
    metric_id: str = "git.commit.count",
    left_evidence: list[Dict[str, Any]] | None = None,
    right_evidence: list[Dict[str, Any]] | None = None,
    ticket_id: str | None = None,
) -> Dict[str, Any]:
    left_ev = left_evidence or [
        _make_evidence("ev:left:1", "sha256:1111111111111111111111111111111111111111111111111111111111111111")
    ]
    right_ev = right_evidence or [
        _make_evidence("ev:right:1", "sha256:2222222222222222222222222222222222222222222222222222222222222222")
    ]

    observations = []
    if outcome != "MISSING_LEFT":
        observations.append({
            "observation_id": "obs:left:1",
            "side": "left",
            "state": "OBSERVED" if outcome != "UNEVALUABLE" else "FAILED",
            "value": {"kind": "integer", "value": "10"},
            "evidence": left_ev,
        })
    if outcome != "MISSING_RIGHT":
        observations.append({
            "observation_id": "obs:right:1",
            "side": "right",
            "state": "OBSERVED" if outcome != "UNEVALUABLE" else "FAILED",
            "value": {"kind": "integer", "value": "12"},
            "evidence": right_ev,
        })

    bundle: Dict[str, Any] = {
        "schema": "autogrammar.data2dsl/comparison-bundle/v0",
        "query": {
            "schema": "autogrammar.data2dsl/query/v0",
            "query_id": f"query:{metric_id}",
            "subject": {"repository": "https://github.com/autogrammar/data2dsl", "actor": "github:alice"},
            "metric": {"id": metric_id, "version": "v1", "value_kind": "integer", "unit": "count"},
            "window": {"start": "2026-08-10T00:00:00Z", "end": "2026-08-17T00:00:00Z", "semantics": "half-open-utc"},
        },
        "observations": observations,
        "result": {
            "schema": "autogrammar.data2dsl/comparison-result/v0",
            "query_id": f"query:{metric_id}",
            "outcome": outcome,
            "delta": delta,
            "evidence_ids": [e["evidence_id"] for e in left_ev + right_ev],
        },
    }
    if ticket_id:
        bundle["ticket_id"] = ticket_id
    return bundle


def test_remediation_intent_conflict_numeric():
    bundle_int = _make_bundle(
        outcome="CONFLICT",
        delta={"kind": "integer", "value": "-2"},
        metric_id="git.commit.count",
    )
    intent = format_remediation_intent(bundle_int, ticket_id="ticket-044")

    assert intent["schema"] == "autogrammar.data2dsl/remediation-feed/v0"
    assert intent["ticket"] == "ticket-044"
    assert intent["remediation_version"] == "1.0.0"
    assert intent["status"] == "PROPOSED"
    assert len(intent["actionable_items"]) == 1

    item = intent["actionable_items"][0]
    assert item["action"] == "synchronize_metric"
    assert item["outcome"] == "CONFLICT"
    assert item["required_delta"] == {"kind": "integer", "value": "-2"}
    assert item["target_subject"] == "https://github.com/autogrammar/data2dsl"
    assert len(item["left_evidence"]) == 1
    assert len(item["right_evidence"]) == 1
    assert len(intent["evidence_digest"]) == 2
    assert "sha256:1111111111111111111111111111111111111111111111111111111111111111" in intent["evidence_digest"]


def test_remediation_intent_conflict_percentage_and_float():
    bundle_pct = _make_bundle(
        outcome="CONFLICT",
        delta={"kind": "percentage", "value": "-15.0%"},
        metric_id="test.coverage",
    )
    bundle_flt = _make_bundle(
        outcome="CONFLICT",
        delta={"kind": "float", "value": "3.5"},
        metric_id="pyqual.score",
    )

    intent = format_remediation_intent([bundle_pct, bundle_flt])
    assert intent["status"] == "PROPOSED"
    assert len(intent["actionable_items"]) == 2
    assert intent["actionable_items"][0]["action"] == "synchronize_metric"
    assert intent["actionable_items"][1]["action"] == "synchronize_metric"


def test_remediation_intent_conflict_string_set():
    delta_set = {
        "kind": "string-set",
        "added": ["extra_feature.py"],
        "removed": ["required_module.py"],
    }
    bundle_set = _make_bundle(
        outcome="CONFLICT",
        delta=delta_set,
        metric_id="ast.exported_symbols",
    )
    intent = RemediationIntentFormatter.format_intent(bundle_set, target_repo="autogrammar/custom-repo")

    assert intent["status"] == "PROPOSED"
    assert len(intent["actionable_items"]) == 1
    item = intent["actionable_items"][0]
    assert item["action"] == "resolve_conflict"
    assert item["target_subject"] == "autogrammar/custom-repo"
    assert "1 added, 1 removed" in item["description"]


def test_remediation_intent_match_satisfied():
    bundle_match = _make_bundle(outcome="MATCH", delta=None, metric_id="git.commit.count")
    intent = format_remediation_intent(bundle_match)

    assert intent["status"] == "SATISFIED"
    assert intent["actionable_items"] == []
    assert "satisfied" in intent["summary"].lower()


def test_remediation_intent_missing_observations():
    b_miss_left = _make_bundle("MISSING_LEFT", None, metric_id="m.miss_left")
    b_miss_right = _make_bundle("MISSING_RIGHT", None, metric_id="m.miss_right")

    intent = format_remediation_intent([b_miss_left, b_miss_right])
    assert intent["status"] == "PROPOSED"
    assert len(intent["actionable_items"]) == 2
    assert intent["actionable_items"][0]["action"] == "restore_missing_entries"
    assert intent["actionable_items"][1]["action"] == "restore_missing_entries"


def test_remediation_intent_unevaluable_blocked():
    b_uneval = _make_bundle("UNEVALUABLE", None, metric_id="m.uneval")
    intent = format_remediation_intent(b_uneval)

    assert intent["status"] == "BLOCKED"
    assert len(intent["actionable_items"]) == 1
    assert intent["actionable_items"][0]["action"] == "investigate_missing_telemetry"
    assert "blocked" in intent["summary"].lower()


def test_cli_feed_koru(tmp_path: Path, capsys):
    bundle = _make_bundle(
        outcome="CONFLICT",
        delta={"kind": "integer", "value": "-5"},
        ticket_id="ticket-bundle-id",
    )
    bundle_file = tmp_path / "bundle.json"
    bundle_file.write_text(json.dumps(bundle), encoding="utf-8")

    out_file = tmp_path / "remediation_intent.json"
    ret = cli_main([
        "feed-koru",
        "--bundle",
        str(bundle_file),
        "--output",
        str(out_file),
        "--ticket",
        "ticket-cli-override",
    ])
    assert ret == 0
    assert out_file.exists()

    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert data["schema"] == "autogrammar.data2dsl/remediation-feed/v0"
    assert data["ticket"] == "ticket-cli-override"
    assert data["status"] == "PROPOSED"
    assert len(data["actionable_items"]) == 1
    assert data["actionable_items"][0]["action"] == "synchronize_metric"

    # Test stdout output without --output
    ret_stdout = cli_main(["feed-koru", "--bundle", str(bundle_file)])
    assert ret_stdout == 0
    captured = capsys.readouterr()
    stdout_data = json.loads(captured.out)
    assert stdout_data["ticket"] == "ticket-bundle-id"
    assert stdout_data["status"] == "PROPOSED"
