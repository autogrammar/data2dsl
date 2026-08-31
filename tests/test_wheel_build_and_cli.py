"""Tests verifying CLI standalone execution and contract self-test."""

from __future__ import annotations

import json
from pathlib import Path

from data2dsl_cli import main as cli_main


def test_cli_self_test():
    """Verify data2dsl --self-test executes and passes cleanly."""
    exit_code = cli_main(["--self-test"])
    assert exit_code == 0


def test_cli_help(capsys):
    """Verify data2dsl --help prints valid help and returns 0."""
    try:
        cli_main(["--help"])
    except SystemExit as exc:
        assert exc.code == 0
    captured = capsys.readouterr()
    assert "data2dsl: neutral factual data comparator" in captured.out


def test_cli_compare_execution(tmp_path: Path):
    """Verify data2dsl compare command execution between two observations."""
    from data2dsl_adapters import (
        DiagitCommitMetricResponse,
        GitHubDiagitAdapter,
        WorkSummaryMarkdownAdapter,
    )

    query_file = tmp_path / "query.json"
    left_file = tmp_path / "left.json"
    right_file = tmp_path / "right.json"
    output_file = tmp_path / "output.json"

    query = {
        "schema": "autogrammar.data2dsl/query/v0",
        "query_id": "q:cli:test",
        "subject": {"repository": "https://github.com/org/repo", "actor": "github:alice"},
        "metric": {"id": "git.commit.count", "version": "v1", "value_kind": "integer", "unit": "count"},
        "window": {"start": "2026-01-01T00:00:00Z", "end": "2026-01-02T00:00:00Z", "semantics": "half-open-utc"},
        "left_source": {"id": "source:work-summary", "kind": "markdown"},
        "right_source": {"id": "source:github", "kind": "github"},
        "comparison": {"equality": "integer-exact", "delta_direction": "right-minus-left", "missing_is_zero": False},
    }

    md_adapter = WorkSummaryMarkdownAdapter()
    claim = md_adapter.extract_commit_claim("- alice: 15 commits\n", "github:alice")
    assert claim is not None
    left_obs = md_adapter.normalize(query, claim, side="left")

    gh_adapter = GitHubDiagitAdapter()
    gh_resp = DiagitCommitMetricResponse(status="OK", commit_count=15)
    right_obs = gh_adapter.normalize(query, gh_resp, side="right")

    query_file.write_text(json.dumps(query), encoding="utf-8")
    left_file.write_text(json.dumps(left_obs), encoding="utf-8")
    right_file.write_text(json.dumps(right_obs), encoding="utf-8")

    exit_code = cli_main([
        "compare",
        "--query", str(query_file),
        "--left", str(left_file),
        "--right", str(right_file),
        "--output", str(output_file),
    ])
    assert exit_code == 0
    assert output_file.exists()
    bundle = json.loads(output_file.read_text(encoding="utf-8"))
    assert bundle["result"]["outcome"] == "MATCH"
