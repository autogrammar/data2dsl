"""Tests verifying batch missing observation handling and markdown report formatting (F10, F12)."""

from data2dsl_batch import (
    BatchMultiQueryComparator,
    format_markdown_report,
)


def _make_query(qid: str = "q1", metric_id: str = "metric.count"):
    return {
        "schema": "autogrammar.data2dsl/query/v0",
        "query_id": qid,
        "subject": {"repository": "https://github.com/autogrammar/data2dsl", "actor": "alice"},
        "metric": {"id": metric_id, "version": "v1", "value_kind": "integer", "unit": "count"},
        "window": {"start": "2026-08-01T00:00:00Z", "end": "2026-08-27T00:00:00Z", "semantics": "half-open-utc"},
        "left_source": {"id": "s:l", "kind": "markdown"},
        "right_source": {"id": "s:r", "kind": "github"},
        "comparison": {"equality": "integer-exact", "delta_direction": "right-minus-left", "missing_is_zero": False},
    }


def _make_obs(qid: str, side: str, val: int = 10):
    return {
        "schema": "autogrammar.data2dsl/observation/v0",
        "observation_id": f"obs:{side}:{qid}",
        "query_id": qid,
        "side": side,
        "subject": {"repository": "https://github.com/autogrammar/data2dsl", "actor": "alice"},
        "metric": {"id": "metric.count", "version": "v1", "value_kind": "integer", "unit": "count"},
        "window": {"start": "2026-08-01T00:00:00Z", "end": "2026-08-27T00:00:00Z", "semantics": "half-open-utc"},
        "state": "OBSERVED",
        "value": {"kind": "integer", "value": str(val)},
        "evidence": [
            {
                "evidence_id": f"ev:{side}:{qid}",
                "target_uri": "https://github.com/autogrammar/data2dsl",
                "source_uri": "https://github.com/autogrammar/data2dsl",
                "source_revision": "HEAD",
                "media_type": "text/markdown",
                "digest_sha256": "a" * 64,
                "extractor": {"id": "test", "version": "1.0"},
                "location": {"kind": "markdown-lines", "path": "README.md", "start_line": 1, "end_line": 1},
            }
        ],
    }


def test_batch_missing_left_and_right_counters():
    """F10: Missing left or right observations produce MISSING_LEFT/MISSING_RIGHT outcomes and valid metrics."""
    batch_comp = BatchMultiQueryComparator()
    q1 = _make_query("q1")
    q2 = _make_query("q2")
    q3 = _make_query("q3")

    # q1 has only right (missing left)
    # q2 has only left (missing right)
    # q3 has both (match)
    left_obs = [_make_obs("q2", "left", 10), _make_obs("q3", "left", 10)]
    right_obs = [_make_obs("q1", "right", 10), _make_obs("q3", "right", 10)]

    report = batch_comp.compare_batch([q1, q2, q3], left_obs, right_obs)
    assert report.summary.total_queries == 3
    assert report.summary.matches == 1
    assert report.summary.missing_left == 1
    assert report.summary.missing_right == 1
    assert report.summary.conflicts == 0
    assert not report.summary.is_clean


def test_markdown_report_formatting_with_missing_and_sets():
    """F12: Markdown formatter handles missing observations and complex items gracefully."""
    batch_comp = BatchMultiQueryComparator()
    q1 = _make_query("q1")
    q2 = _make_query("q2")

    left_obs = [_make_obs("q1", "left", 10)]
    right_obs = [_make_obs("q2", "right", 10)]

    report = batch_comp.compare_batch([q1, q2], left_obs, right_obs)
    md = format_markdown_report(report)

    assert "| `(missing)` |" in md or "(missing)" in md
    assert "MISSING_LEFT" in md
    assert "MISSING_RIGHT" in md
    assert "# data2dsl Comparison Report" in md
