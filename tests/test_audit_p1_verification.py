"""Dedicated regression tests for all findings in AUDYT_KODU_2026-08-28.md (P1.1 - P1.6)."""

from __future__ import annotations

import json
from typing import Any

import pytest

from data2dsl_adapters import (
    Code2LogicAdapter,
    Code2SchemaAdapter,
    CurllmAdapter,
    OqlTelemetryAdapter,
    SUMDAdapter,
    WorkSummaryMarkdownAdapter,
)
from data2dsl_batch import BatchMultiQueryComparator
from data2dsl_comparator import DeterministicComparator
from data2dsl_doctor import DiagnosticProfileFormatter
from data2dsl_remediation import RemediationIntentFormatter
from data2dsl_skill import Data2DslSkill


# ---------------------------------------------------------------------------
# P1.2: Comparability validation (side, unit, version, semantics)
# ---------------------------------------------------------------------------


def test_p1_2_comparator_rejects_wrong_side():
    """Observation with side='left' provided as right observation must evaluate to UNEVALUABLE."""
    query = {
        "schema": "autogrammar.data2dsl/query/v0",
        "query_id": "q:side:test",
        "subject": {"repository": "https://github.com/org/repo", "actor": "alice"},
        "metric": {"id": "commits", "value_kind": "integer"},
        "window": {"start": "2026-01-01T00:00:00Z", "end": "2026-01-02T00:00:00Z"},
        "comparison": {"delta_kind": "integer", "tolerance": "0", "direction": "exact"},
    }
    left_obs = {
        "schema": "autogrammar.data2dsl/observation/v0",
        "observation_id": "obs:left",
        "query_id": "q:side:test",
        "side": "left",
        "subject": {"repository": "https://github.com/org/repo", "actor": "alice"},
        "metric": {"id": "commits", "value_kind": "integer"},
        "window": {"start": "2026-01-01T00:00:00Z", "end": "2026-01-02T00:00:00Z"},
        "state": "OBSERVED",
        "value": {"kind": "integer", "value": "10"},
        "evidence": [{"evidence_id": "ev:1", "digest_sha256": "1111", "source_uri": "uri:1", "source_revision": "sha256:1111"}],
    }
    # Passing left_obs as right_obs (which has side='left')
    comparator = DeterministicComparator()
    bundle = comparator.compare(query, left_obs, left_obs)
    assert bundle["result"]["outcome"] == "UNEVALUABLE"


def test_p1_2_comparator_rejects_mismatched_unit_and_version():
    """Mismatched metric unit or version between query and observation must evaluate to UNEVALUABLE."""
    query = {
        "schema": "autogrammar.data2dsl/query/v0",
        "query_id": "q:unit:test",
        "subject": {"repository": "https://github.com/org/repo", "actor": "alice"},
        "metric": {"id": "latency", "value_kind": "integer", "unit": "ms", "version": "v1"},
        "window": {"start": "2026-01-01T00:00:00Z", "end": "2026-01-02T00:00:00Z"},
        "comparison": {"delta_kind": "integer", "tolerance": "0", "direction": "exact"},
    }
    left_obs = {
        "schema": "autogrammar.data2dsl/observation/v0",
        "observation_id": "obs:left",
        "query_id": "q:unit:test",
        "side": "left",
        "subject": {"repository": "https://github.com/org/repo", "actor": "alice"},
        "metric": {"id": "latency", "value_kind": "integer", "unit": "seconds", "version": "v1"},  # different unit
        "window": {"start": "2026-01-01T00:00:00Z", "end": "2026-01-02T00:00:00Z"},
        "state": "OBSERVED",
        "value": {"kind": "integer", "value": "10"},
        "evidence": [{"evidence_id": "ev:1", "digest_sha256": "1111", "source_uri": "uri:1", "source_revision": "sha256:1111"}],
    }
    right_obs = dict(left_obs, side="right", observation_id="obs:right")
    comparator = DeterministicComparator()
    bundle = comparator.compare(query, left_obs, right_obs)
    assert bundle["result"]["outcome"] == "UNEVALUABLE"


# ---------------------------------------------------------------------------
# P1.3: Batch deduplication & ambiguity detection
# ---------------------------------------------------------------------------


def test_p1_3_batch_detects_ambiguous_conflicting_duplicates():
    """Duplicate observations for the same query with conflicting values must produce UNEVALUABLE, regardless of input order."""
    query = {
        "schema": "autogrammar.data2dsl/query/v0",
        "query_id": "q:batch:dup",
        "subject": {"repository": "https://github.com/org/repo", "actor": "alice"},
        "metric": {"id": "tasks", "value_kind": "integer"},
        "window": {"start": "2026-01-01T00:00:00Z", "end": "2026-01-02T00:00:00Z"},
        "comparison": {"delta_kind": "integer", "tolerance": "0", "direction": "exact"},
    }
    left_obs = {
        "schema": "autogrammar.data2dsl/observation/v0",
        "observation_id": "obs:left",
        "query_id": "q:batch:dup",
        "side": "left",
        "subject": {"repository": "https://github.com/org/repo", "actor": "alice"},
        "metric": {"id": "tasks", "value_kind": "integer"},
        "window": {"start": "2026-01-01T00:00:00Z", "end": "2026-01-02T00:00:00Z"},
        "state": "OBSERVED",
        "value": {"kind": "integer", "value": "10"},
        "evidence": [{"evidence_id": "ev:1", "digest_sha256": "1111", "source_uri": "uri:1", "source_revision": "sha256:1111"}],
    }
    right_obs_10 = dict(left_obs, side="right", observation_id="obs:right:10", value={"kind": "integer", "value": "10"})
    right_obs_999 = dict(left_obs, side="right", observation_id="obs:right:999", value={"kind": "integer", "value": "999"})

    cmp = BatchMultiQueryComparator()

    # Order 1: [10, 999]
    report1 = cmp.compare_batch([query], [left_obs], [right_obs_10, right_obs_999])
    assert report1.summary.is_clean is False
    assert report1.summary.ambiguous_count >= 1

    # Order 2: [999, 10] (order must not change the ambiguity detection)
    report2 = cmp.compare_batch([query], [left_obs], [right_obs_999, right_obs_10])
    assert report2.summary.is_clean is False
    assert report2.summary.ambiguous_count >= 1


# ---------------------------------------------------------------------------
# P1.4: Adapter deserialization and semantics
# ---------------------------------------------------------------------------


def test_p1_4_code2schema_entities_deserialization():
    """Code2Schema normalizer must accept entities list without TypeError."""
    query = {
        "schema": "autogrammar.data2dsl/query/v0",
        "query_id": "q:c2s",
        "subject": {"repository": "repo", "actor": "model"},
        "metric": {"id": "code2schema.declared.entities", "value_kind": "string-set"},
        "window": {"start": "2026-01-01T00:00:00Z", "end": "2026-01-02T00:00:00Z"},
        "comparison": {"delta_kind": "string-set", "tolerance": "0", "direction": "exact"},
    }
    res = Data2DslSkill.execute_compare(
        query=query,
        left_raw={"status": "OK", "entities": ["User", "Account"]},
        left_source_type="code2schema",
        right_raw={"status": "OK", "entities": ["User", "Account"]},
        right_source_type="code2schema",
    )
    assert res["status"] == "OK"
    assert res["result"]["outcome"] == "MATCH"


def test_p1_4_curllm_and_code2logic_respect_error_status():
    """Curllm/Code2Logic raw response with status: ERROR must not result in OBSERVED state."""
    query = {
        "schema": "autogrammar.data2dsl/query/v0",
        "query_id": "q:err",
        "subject": {"repository": "repo", "actor": "fetcher"},
        "metric": {"id": "curllm.page.title", "value_kind": "string"},
        "window": {"start": "2026-01-01T00:00:00Z", "end": "2026-01-02T00:00:00Z"},
        "comparison": {"delta_kind": "string", "tolerance": "0", "direction": "exact"},
    }
    res = Data2DslSkill.execute_compare(
        query=query,
        left_raw={"status": "ERROR", "value": "some_stale_value", "error_message": "Network timeout"},
        left_source_type="curllm",
        right_raw={"status": "OK", "value": "some_stale_value"},
        right_source_type="curllm",
    )
    # Left observation is UNEVALUABLE due to ERROR status
    assert res["status"] == "OK"
    assert res["result"]["outcome"] == "UNEVALUABLE"


def test_p1_4_oql_active_buses_field():
    """OQL adapter must read active_buses / buses without AttributeError."""
    query = {
        "schema": "autogrammar.data2dsl/query/v0",
        "query_id": "q:oql:buses",
        "subject": {"repository": "oqlos/device", "actor": "sensor"},
        "metric": {"id": "oql.hardware.bus", "value_kind": "string-set", "property": "buses"},
        "window": {"start": "2026-01-01T00:00:00Z", "end": "2026-01-02T00:00:00Z"},
        "comparison": {"delta_kind": "string-set", "tolerance": "0", "direction": "exact"},
    }
    res = Data2DslSkill.execute_compare(
        query=query,
        left_raw={"status": "OK", "log_id": "log:1", "path": "sensors.log", "active_buses": ["i2c", "spi"]},
        left_source_type="oql_telemetry",
        right_raw={"status": "OK", "scenario_id": "sc:1", "path": "spec.json", "buses": ["i2c", "spi"]},
        right_source_type="oql_spec",
    )
    assert res["status"] == "OK"
    assert res["result"]["outcome"] == "MATCH"


def test_p1_4_oql_raw_zero_value_preserved():
    """OQL raw measurement of 0 (e.g. avg_sample_rate_hz = 0) must be OBSERVED with value 0, not UNEVALUABLE."""
    query = {
        "schema": "autogrammar.data2dsl/query/v0",
        "query_id": "q:oql:zero",
        "subject": {"repository": "oqlos/device", "actor": "sensor"},
        "metric": {"id": "oql.sample_rate.hz", "value_kind": "float", "property": "sample_rate"},
        "window": {"start": "2026-01-01T00:00:00Z", "end": "2026-01-02T00:00:00Z"},
        "comparison": {"delta_kind": "float", "tolerance": "0.0", "direction": "exact"},
    }
    res = Data2DslSkill.execute_compare(
        query=query,
        left_raw={"status": "OK", "log_id": "log:1", "path": "sensors.log", "avg_sample_rate_hz": 0},
        left_source_type="oql_telemetry",
        right_raw={"status": "OK", "scenario_id": "sc:1", "path": "spec.json", "sample_rate_hz": 0},
        right_source_type="oql_spec",
    )
    assert res["status"] == "OK"
    assert res["result"]["outcome"] == "MATCH"
    assert res["bundle"]["observations"][0]["state"] == "OBSERVED"
    assert res["bundle"]["observations"][0]["value"]["value"] == "0.00"


# ---------------------------------------------------------------------------
# P1.5: Exact matching (Actor & SUMD key)
# ---------------------------------------------------------------------------


def test_p1_5_actor_exact_word_boundary_matching():
    """Markdown claim extraction must match 'alice' exactly, not substring 'malice'."""
    text = (
        "# Work Summary\n"
        "- malice: 99 commits\n"
        "- alice: 12 commits\n"
    )
    adapter = WorkSummaryMarkdownAdapter()
    claim = adapter.extract_commit_claim(
        markdown_text=text,
        actor="github:alice",
        repository_uri="https://github.com/org/repo",
    )
    assert claim is not None
    assert claim.value == 12  # Must NOT be 99


def test_p1_5_sumd_exact_key_matching():
    """SUMD extraction must match 'tasks_completed' exactly, not 'tasks_completed_total'."""
    text = (
        "# Execution Report\n\n"
        "| Metric | Value |\n"
        "| --- | --- |\n"
        "| tasks_completed_total | 99 |\n"
        "| tasks_completed | 12 |\n"
    )
    adapter = SUMDAdapter()
    resp = adapter.extract_table_metric(
        markdown_text=text,
        metric_id="tasks_completed",
        path="report.md",
    )
    assert resp is not None
    assert resp.value == 12  # Must NOT be 99


# ---------------------------------------------------------------------------
# P1.6: Evidence ID format (no illegal slashes)
# ---------------------------------------------------------------------------


def test_p1_6_code2logic_and_code2schema_evidence_id_sanitization():
    """Evidence IDs generated from paths with slashes (e.g. src/main.py) must not contain '/'."""
    from data2dsl_adapters import Code2LogicMetricResponse
    adapter = Code2LogicAdapter()
    resp = Code2LogicMetricResponse(status="OK", value="main", value_kind="string", path="src/main.py", start_line=1, end_line=50)
    obs = adapter.normalize(
        response=resp,
        query={
            "schema": "autogrammar.data2dsl/query/v0",
            "query_id": "q:c2l",
            "subject": {"repository": "repo", "actor": "analyzer"},
            "metric": {"id": "code2logic.declared.functions", "value_kind": "string"},
            "window": {"start": "2026-01-01T00:00:00Z", "end": "2026-01-02T00:00:00Z"},
        },
        side="left",
    )
    for ev in obs["evidence"]:
        # Stable ID must not contain '/'
        assert "/" not in ev["evidence_id"]
        assert ":" in ev["evidence_id"]
