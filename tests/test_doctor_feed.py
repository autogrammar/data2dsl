from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from data2dsl_cli import main as cli_main
from data2dsl_doctor import (
    DiagnosticProfileFormatter,
    EvidenceRef,
    format_diagnostic_profile,
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
) -> Dict[str, Any]:
    left_ev = left_evidence or [_make_evidence("ev:left:1", "sha256:1111111111111111111111111111111111111111111111111111111111111111")]
    right_ev = right_evidence or [_make_evidence("ev:right:1", "sha256:2222222222222222222222222222222222222222222222222222222222222222")]

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

    return {
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


def test_format_percentage_severities():
    b_crit = _make_bundle("CONFLICT", {"kind": "percentage", "value": "-25.0%"})
    b_high = _make_bundle("CONFLICT", {"kind": "percentage", "value": "-12.5%"})
    b_med = _make_bundle("CONFLICT", {"kind": "percentage", "value": "6.0%"})
    b_low = _make_bundle("CONFLICT", {"kind": "percentage", "value": "1.5%"})

    profile = format_diagnostic_profile([b_crit, b_high, b_med, b_low])
    symptoms = profile["symptoms"]

    assert len(symptoms) == 4
    assert symptoms[0]["severity"] == "CRITICAL"
    assert symptoms[0]["delta"]["value"] == "-25.0%"
    assert symptoms[1]["severity"] == "HIGH"
    assert symptoms[1]["delta"]["value"] == "-12.5%"
    assert symptoms[2]["severity"] == "MEDIUM"
    assert symptoms[2]["delta"]["value"] == "6.0%"
    assert symptoms[3]["severity"] == "LOW"
    assert symptoms[3]["delta"]["value"] == "1.5%"

    assert profile["summary"]["CRITICAL"] == 1
    assert profile["summary"]["HIGH"] == 1
    assert profile["summary"]["MEDIUM"] == 1
    assert profile["summary"]["LOW"] == 1
    assert profile["summary"]["total"] == 4


def test_format_integer_and_float_severities():
    b_int_crit = _make_bundle("CONFLICT", {"kind": "integer", "value": "60"}, metric_id="int.crit")
    b_int_med = _make_bundle("CONFLICT", {"kind": "integer", "value": "4"}, metric_id="int.med")
    b_float_high = _make_bundle("CONFLICT", {"kind": "float", "value": "15.5"}, metric_id="flt.high")
    b_float_low = _make_bundle("CONFLICT", {"kind": "float", "value": "0.3"}, metric_id="flt.low")

    profile = format_diagnostic_profile([b_int_med, b_int_crit, b_float_low, b_float_high])
    symptoms = profile["symptoms"]

    assert symptoms[0]["severity"] == "CRITICAL"
    assert symptoms[0]["metric"]["id"] == "int.crit"

    assert symptoms[1]["severity"] == "HIGH"
    assert symptoms[1]["metric"]["id"] == "flt.high"

    assert symptoms[2]["severity"] == "MEDIUM"
    assert symptoms[2]["metric"]["id"] == "int.med"

    assert symptoms[3]["severity"] == "LOW"
    assert symptoms[3]["metric"]["id"] == "flt.low"


def test_string_set_and_missing_keys():
    delta_set = {
        "kind": "string-set",
        "added": ["auth_v2.py"],
        "removed": ["auth_middleware.py", "legacy_auth.py"],
    }
    b_set = _make_bundle("CONFLICT", delta_set)
    profile = format_diagnostic_profile(b_set)

    symptom = profile["symptoms"][0]
    assert symptom["severity"] == "MEDIUM"  # 3 items total
    assert symptom["missing_keys"] == ["auth_middleware.py", "legacy_auth.py"]


def test_outcomes_match_unevaluable_missing():
    b_match = _make_bundle("MATCH", None, metric_id="m.match")
    b_uneval = _make_bundle("UNEVALUABLE", None, metric_id="m.uneval")
    b_miss_left = _make_bundle("MISSING_LEFT", None, metric_id="m.miss_left")
    b_miss_right = _make_bundle("MISSING_RIGHT", None, metric_id="m.miss_right")

    profile = format_diagnostic_profile([b_match, b_uneval, b_miss_left, b_miss_right])
    symptoms = profile["symptoms"]

    # UNEVALUABLE (mag 50) > MISSING_LEFT / RIGHT (mag 40) > MATCH (INFO)
    assert symptoms[0]["outcome"] == "UNEVALUABLE"
    assert symptoms[0]["severity"] == "HIGH"

    assert symptoms[1]["outcome"] in ("MISSING_LEFT", "MISSING_RIGHT")
    assert symptoms[1]["severity"] == "HIGH"

    # Verify missing_keys for missing sides
    s_left = next(s for s in symptoms if s["outcome"] == "MISSING_LEFT")
    assert s_left["missing_keys"] == ["left"]
    s_right = next(s for s in symptoms if s["outcome"] == "MISSING_RIGHT")
    assert s_right["missing_keys"] == ["right"]

    s_match = next(s for s in symptoms if s["outcome"] == "MATCH")
    assert s_match["severity"] == "INFO"
    assert s_match["missing_keys"] == []


def test_evidence_chain_deduplication():
    shared_ev = _make_evidence("ev:shared:1", "sha256:9999999999999999999999999999999999999999999999999999999999999999")
    b1 = _make_bundle("CONFLICT", {"kind": "integer", "value": "5"}, left_evidence=[shared_ev])
    b2 = _make_bundle("MATCH", None, right_evidence=[shared_ev])

    profile = DiagnosticProfileFormatter.format_profile([b1, b2])
    chain = profile["evidence_chain"]

    # Shared evidence should appear once in evidence_chain
    shared_entries = [e for e in chain if e["evidence_id"] == "ev:shared:1"]
    assert len(shared_entries) == 1
    assert shared_entries[0]["digest_sha256"].startswith("sha256:")


def test_evidence_ref_dataclass():
    ev_dict = _make_evidence("ev:custom", "sha256:abcd")
    ref = EvidenceRef(
        evidence_id=ev_dict["evidence_id"],
        target_uri=ev_dict["target_uri"],
        source_uri=ev_dict["source_uri"],
        source_revision=ev_dict["source_revision"],
        media_type=ev_dict["media_type"],
        digest_sha256=ev_dict["digest_sha256"],
        extractor=ev_dict["extractor"],
        location=ev_dict["location"],
    )
    d = ref.to_dict()
    assert d["evidence_id"] == "ev:custom"
    assert d["digest_sha256"] == "sha256:abcd"


def test_cli_feed_doctor(tmp_path: Path):
    bundle = _make_bundle("CONFLICT", {"kind": "percentage", "value": "-12.5%"})
    bundle_file = tmp_path / "bundle.json"
    bundle_file.write_text(json.dumps(bundle), encoding="utf-8")

    out_file = tmp_path / "diagnostic_profile.json"
    ret = cli_main(["feed-doctor", "--bundle", str(bundle_file), "--output", str(out_file)])
    assert ret == 0
    assert out_file.exists()

    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert data["diagnostic_version"] == "1.0.0"
    assert len(data["symptoms"]) == 1
    assert data["symptoms"][0]["severity"] == "HIGH"
    assert data["summary"]["HIGH"] == 1
