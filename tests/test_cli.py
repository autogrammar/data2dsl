from __future__ import annotations

import json
from pathlib import Path
import pytest
from data2dsl_cli import main


def test_cli_self_test(capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["--self-test"])
    assert code == 0
    captured = capsys.readouterr()
    assert "data2dsl CLI self-test passed." in captured.out


def test_cli_compare_golden_match(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    md_file = tmp_path / "work-summary.md"
    md_file.write_text(
        "# Summary\n- alice: 10 commits\n",
        encoding="utf-8",
    )

    gh_file = tmp_path / "gh.json"
    gh_file.write_text(
        json.dumps(
            {
                "repository": "owner/repo",
                "actor": "alice",
                "time_window_start": "2026-08-01T00:00:00Z",
                "time_window_end": "2026-08-02T00:00:00Z",
                "commit_count": 10,
            }
        ),
        encoding="utf-8",
    )

    out_file = tmp_path / "result.json"
    code = main(
        [
            "compare-golden",
            "--markdown",
            str(md_file),
            "--github-response",
            str(gh_file),
            "--output",
            str(out_file),
        ]
    )
    assert code == 0
    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert data["result"]["outcome"] == "MATCH"

    # Test validate command
    val_code = main(["validate", "--bundle", str(out_file)])
    assert val_code == 0
    captured = capsys.readouterr()
    assert "VALID:" in captured.out


def test_cli_compare_observations(tmp_path: Path) -> None:
    digest_a = "a" * 64
    digest_d = "d" * 64
    left = {
        "schema": "autogrammar.data2dsl/observation/v0",
        "observation_id": "obs:left",
        "query_id": "query:test",
        "side": "left",
        "subject": {"repository": "https://github.com/owner/repo", "actor": "github:alice"},
        "metric": {"id": "git.commit.count", "version": "v1", "value_kind": "integer", "unit": "count"},
        "window": {"start": "2026-08-01T00:00:00Z", "end": "2026-08-02T00:00:00Z", "semantics": "half-open-utc"},
        "state": "OBSERVED",
        "value": {"kind": "integer", "value": "10"},
        "evidence": [
            {
                "evidence_id": "ev:1",
                "target_uri": "https://github.com/owner/repo",
                "source_uri": "https://github.com/owner/repo/blob/abc/work-summary.md",
                "source_revision": f"sha256:{digest_a}",
                "media_type": "text/markdown",
                "digest_sha256": digest_a,
                "extractor": {"id": "mdflow", "version": "0.1.0"},
                "location": {"kind": "markdown-lines", "path": "work-summary.md", "start_line": 1, "end_line": 1},
            }
        ],
    }

    right = {
        "schema": "autogrammar.data2dsl/observation/v0",
        "observation_id": "obs:right",
        "query_id": "query:test",
        "side": "right",
        "subject": {"repository": "https://github.com/owner/repo", "actor": "github:alice"},
        "metric": {"id": "git.commit.count", "version": "v1", "value_kind": "integer", "unit": "count"},
        "window": {"start": "2026-08-01T00:00:00Z", "end": "2026-08-02T00:00:00Z", "semantics": "half-open-utc"},
        "state": "OBSERVED",
        "value": {"kind": "integer", "value": "12"},
        "evidence": [
            {
                "evidence_id": "ev:2",
                "target_uri": "https://github.com/owner/repo",
                "source_uri": "https://api.github.com/repos/owner/repo/commits",
                "source_revision": f"sha256:{digest_d}",
                "media_type": "application/json",
                "digest_sha256": digest_d,
                "extractor": {"id": "diagit", "version": "0.1.0"},
                "location": {"kind": "github-page", "endpoint": "/repos/owner/repo/commits", "page": 1, "cursor": None},
            }
        ],
    }

    left_file = tmp_path / "left.json"
    right_file = tmp_path / "right.json"
    out_file = tmp_path / "bundle.json"
    left_file.write_text(json.dumps(left), encoding="utf-8")
    right_file.write_text(json.dumps(right), encoding="utf-8")

    code = main(["compare", "--left", str(left_file), "--right", str(right_file), "--output", str(out_file)])
    assert code == 0
    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert data["result"]["outcome"] == "CONFLICT"
    assert data["result"]["delta"] == {"kind": "integer", "value": "2"}


def test_skill_definitions_and_execution() -> None:
    from data2dsl_skill import Data2DslSkill

    tools = Data2DslSkill.get_tool_definitions()
    assert len(tools) == 2
    tool_names = [t["name"] for t in tools]
    assert "data2dsl_compare" in tool_names
    assert "data2dsl_self_test" in tool_names

    test_res = Data2DslSkill.self_test()
    assert test_res["status"] == "PASS"

    query = {
        "schema": "autogrammar.data2dsl/query/v0",
        "query_id": "query:skill-test",
        "subject": {"repository": "https://github.com/owner/repo", "actor": "github:alice"},
        "metric": {"id": "git.commit.count", "version": "v1", "value_kind": "integer", "unit": "count"},
        "window": {"start": "2026-08-01T00:00:00Z", "end": "2026-08-02T00:00:00Z", "semantics": "half-open-utc"},
        "left_source": {"kind": "markdown-work-summary", "uri": "https://github.com/owner/repo/blob/abc/work-summary.md", "revision": "sha256:aaa", "extractor": {"id": "mdflow", "version": "0.1.0"}},
        "right_source": {"kind": "github-commit-query", "uri": "https://api.github.com/repos/owner/repo/commits", "revision": "sha256:ddd", "extractor": {"id": "diagit", "version": "0.1.0"}},
        "comparison": {"delta_kind": "integer", "tolerance": "0", "direction": "exact"},
    }

    # Error case: missing observations
    err_res = Data2DslSkill.execute_compare(query=query)
    assert err_res["status"] == "ERROR"
    assert err_res["error_code"] == "MISSING_LEFT_OBSERVATION"

    # Execution with raw adapter inputs
    raw_left = {"markdown_content": "# Summary\n- alice: 10 commits\n", "source_uri": "https://github.com/owner/repo/blob/abc/work-summary.md"}
    raw_right = {"repository": "owner/repo", "actor": "alice", "time_window_start": "2026-08-01T00:00:00Z", "time_window_end": "2026-08-02T00:00:00Z", "commit_count": 10}

    exec_res = Data2DslSkill.execute_compare(
        query=query,
        left_raw=raw_left,
        left_source_type="markdown",
        right_raw=raw_right,
        right_source_type="github"
    )
    assert exec_res["status"] == "OK"
    assert exec_res["result"]["outcome"] == "MATCH"


