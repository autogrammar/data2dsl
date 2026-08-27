import json
from pathlib import Path

from data2dsl_batch import BatchMultiQueryComparator
from data2dsl_cli import main as cli_main


QUERY_1 = {
    "schema": "autogrammar.data2dsl/query/v0",
    "query_id": "query:batch:tasks",
    "subject": {
        "repository": "https://github.com/autogrammar/data2dsl",
        "actor": "antigravity",
    },
    "metric": {
        "id": "tasks_completed",
        "version": "1.0.0",
        "value_kind": "integer",
        "unit": "tasks",
    },
    "window": {
        "start": "2026-08-01T00:00:00Z",
        "end": "2026-08-27T00:00:00Z",
        "semantics": "half-open-utc",
    },
    "left_source": {"id": "source:planfile", "kind": "planfile"},
    "right_source": {"id": "source:sumd", "kind": "sumd"},
    "comparison": {
        "equality": "exact",
        "delta_direction": "right-minus-left",
        "missing_is_zero": False,
    },
}

QUERY_2 = {
    "schema": "autogrammar.data2dsl/query/v0",
    "query_id": "query:batch:coverage",
    "subject": {
        "repository": "https://github.com/autogrammar/data2dsl",
        "actor": "antigravity",
    },
    "metric": {
        "id": "code_coverage",
        "version": "1.0.0",
        "value_kind": "percentage",
        "unit": "percent",
    },
    "window": {
        "start": "2026-08-01T00:00:00Z",
        "end": "2026-08-27T00:00:00Z",
        "semantics": "half-open-utc",
    },
    "left_source": {"id": "source:coverage", "kind": "coverage"},
    "right_source": {"id": "source:ci", "kind": "ci"},
    "comparison": {
        "equality": "percentage-exact",
        "delta_direction": "right-minus-left",
        "missing_is_zero": False,
    },
}


def test_batch_comparator_all_match():
    left_obs = [
        {
            "schema": "autogrammar.data2dsl/observation/v0",
            "observation_id": "obs:left:tasks",
            "query_id": "query:batch:tasks",
            "side": "left",
            "subject": QUERY_1["subject"],
            "metric": QUERY_1["metric"],
            "window": QUERY_1["window"],
            "state": "OBSERVED",
            "value": {"kind": "integer", "value": "10"},
            "evidence": [{"evidence_id": "ev:1", "digest_sha256": "1111", "source_uri": "uri:1", "source_revision": "sha256:1111"}],
        },
        {
            "schema": "autogrammar.data2dsl/observation/v0",
            "observation_id": "obs:left:coverage",
            "query_id": "query:batch:coverage",
            "side": "left",
            "subject": QUERY_2["subject"],
            "metric": QUERY_2["metric"],
            "window": QUERY_2["window"],
            "state": "OBSERVED",
            "value": {"kind": "percentage", "value": "95.0%"},
            "evidence": [{"evidence_id": "ev:2", "digest_sha256": "2222", "source_uri": "uri:2", "source_revision": "sha256:2222"}],
        },
    ]

    right_obs = [
        {
            "schema": "autogrammar.data2dsl/observation/v0",
            "observation_id": "obs:right:tasks",
            "query_id": "query:batch:tasks",
            "side": "right",
            "subject": QUERY_1["subject"],
            "metric": QUERY_1["metric"],
            "window": QUERY_1["window"],
            "state": "OBSERVED",
            "value": {"kind": "integer", "value": "10"},
            "evidence": [{"evidence_id": "ev:3", "digest_sha256": "3333", "source_uri": "uri:3", "source_revision": "sha256:3333"}],
        },
        {
            "schema": "autogrammar.data2dsl/observation/v0",
            "observation_id": "obs:right:coverage",
            "query_id": "query:batch:coverage",
            "side": "right",
            "subject": QUERY_2["subject"],
            "metric": QUERY_2["metric"],
            "window": QUERY_2["window"],
            "state": "OBSERVED",
            "value": {"kind": "percentage", "value": "95.0%"},
            "evidence": [{"evidence_id": "ev:4", "digest_sha256": "4444", "source_uri": "uri:4", "source_revision": "sha256:4444"}],
        },
    ]

    comparator = BatchMultiQueryComparator()
    report = comparator.compare_batch([QUERY_1, QUERY_2], left_obs, right_obs)

    assert report.summary.total_queries == 2
    assert report.summary.matches == 2
    assert report.summary.conflicts == 0
    assert report.summary.is_clean is True
    assert report.summary.clean_ratio == 1.0
    assert len(report.bundles) == 2


def test_batch_comparator_with_conflicts_and_missing():
    left_obs = [
        {
            "schema": "autogrammar.data2dsl/observation/v0",
            "observation_id": "obs:left:tasks",
            "query_id": "query:batch:tasks",
            "side": "left",
            "subject": QUERY_1["subject"],
            "metric": QUERY_1["metric"],
            "window": QUERY_1["window"],
            "state": "OBSERVED",
            "value": {"kind": "integer", "value": "10"},
            "evidence": [{"evidence_id": "ev:1", "digest_sha256": "1111", "source_uri": "uri:1", "source_revision": "sha256:1111"}],
        },
    ]

    right_obs = [
        {
            "schema": "autogrammar.data2dsl/observation/v0",
            "observation_id": "obs:right:tasks",
            "query_id": "query:batch:tasks",
            "side": "right",
            "subject": QUERY_1["subject"],
            "metric": QUERY_1["metric"],
            "window": QUERY_1["window"],
            "state": "OBSERVED",
            "value": {"kind": "integer", "value": "8"},
            "evidence": [{"evidence_id": "ev:3", "digest_sha256": "3333", "source_uri": "uri:3", "source_revision": "sha256:3333"}],
        },
    ]

    comparator = BatchMultiQueryComparator()
    report = comparator.compare_batch([QUERY_1, QUERY_2], left_obs, right_obs)

    assert report.summary.total_queries == 2
    assert report.summary.conflicts == 1
    assert report.summary.missing_left == 0 or report.summary.missing_right == 0
    assert report.summary.is_clean is False


def test_batch_cli(tmp_path: Path):
    queries_file = tmp_path / "queries.json"
    left_file = tmp_path / "left.json"
    right_file = tmp_path / "right.json"
    output_file = tmp_path / "report.json"

    queries_file.write_text(json.dumps([QUERY_1]), encoding="utf-8")
    obs = {
        "schema": "autogrammar.data2dsl/observation/v0",
        "observation_id": "obs:1",
        "query_id": "query:batch:tasks",
        "side": "left",
        "subject": QUERY_1["subject"],
        "metric": QUERY_1["metric"],
        "window": QUERY_1["window"],
        "state": "OBSERVED",
        "value": {"kind": "integer", "value": "10"},
        "evidence": [{"evidence_id": "ev:1", "digest_sha256": "1111", "source_uri": "uri:1", "source_revision": "sha256:1111"}],
    }
    left_file.write_text(json.dumps([obs]), encoding="utf-8")
    right_file.write_text(json.dumps([obs]), encoding="utf-8")

    exit_code = cli_main([
        "batch",
        "--queries", str(queries_file),
        "--left", str(left_file),
        "--right", str(right_file),
        "--output", str(output_file),
    ])

    assert exit_code == 0
    assert output_file.exists()
    report_data = json.loads(output_file.read_text(encoding="utf-8"))
    assert report_data["summary"]["is_clean"] is True
    assert report_data["summary"]["matches"] == 1


def test_batch_cli_markdown(tmp_path: Path):
    queries_file = tmp_path / "queries.json"
    left_file = tmp_path / "left.json"
    right_file = tmp_path / "right.json"
    output_file = tmp_path / "report.md"

    queries_file.write_text(json.dumps([QUERY_1]), encoding="utf-8")
    obs = {
        "schema": "autogrammar.data2dsl/observation/v0",
        "observation_id": "obs:1",
        "query_id": "query:batch:tasks",
        "side": "left",
        "subject": QUERY_1["subject"],
        "metric": QUERY_1["metric"],
        "window": QUERY_1["window"],
        "state": "OBSERVED",
        "value": {"kind": "integer", "value": "10"},
        "evidence": [{"evidence_id": "ev:1", "digest_sha256": "1111", "source_uri": "uri:1", "source_revision": "sha256:1111"}],
    }
    left_file.write_text(json.dumps([obs]), encoding="utf-8")
    right_file.write_text(json.dumps([obs]), encoding="utf-8")

    exit_code = cli_main([
        "batch",
        "--queries", str(queries_file),
        "--left", str(left_file),
        "--right", str(right_file),
        "--format", "markdown",
        "--output", str(output_file),
    ])

    assert exit_code == 0
    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8")
    assert "# data2dsl Comparison Report" in content
    assert "CLEAN (All Match)" in content
    assert "`query:batch:tasks`" in content
