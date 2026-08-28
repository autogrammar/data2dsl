"""Tests verifying strict comparability in DeterministicComparator and BatchMultiQueryComparator (F03)."""

import pytest
from data2dsl_comparator import DeterministicComparator
from data2dsl_batch import BatchMultiQueryComparator


@pytest.fixture
def base_query():
    return {
        "schema": "autogrammar.data2dsl/query/v0",
        "query_id": "query:test:commits",
        "subject": {
            "repository": "https://github.com/autogrammar/data2dsl",
            "actor": "alice",
        },
        "metric": {
            "id": "git.commit.count",
            "version": "v1",
            "value_kind": "integer",
            "unit": "commits",
        },
        "window": {
            "start": "2026-08-01T00:00:00Z",
            "end": "2026-08-27T00:00:00Z",
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


@pytest.fixture
def valid_left_obs(base_query):
    return {
        "schema": "autogrammar.data2dsl/observation/v0",
        "observation_id": "obs:left:1",
        "query_id": base_query["query_id"],
        "side": "left",
        "subject": dict(base_query["subject"]),
        "metric": dict(base_query["metric"]),
        "window": dict(base_query["window"]),
        "state": "OBSERVED",
        "value": {"kind": "integer", "value": "42"},
        "evidence": [
            {
                "evidence_id": "ev:left:1",
                "target_uri": "https://github.com/autogrammar/data2dsl",
                "source_uri": "https://github.com/autogrammar/data2dsl",
                "source_revision": "git:0000000000000000000000000000000000000000",
                "media_type": "text/markdown",
                "digest_sha256": "a" * 64,
                "extractor": {"id": "test", "version": "1.0.0"},
                "location": {"kind": "markdown-lines", "path": "summary.md", "start_line": 1, "end_line": 1},
            }
        ],
    }


@pytest.fixture
def valid_right_obs(base_query):
    return {
        "schema": "autogrammar.data2dsl/observation/v0",
        "observation_id": "obs:right:1",
        "query_id": base_query["query_id"],
        "side": "right",
        "subject": dict(base_query["subject"]),
        "metric": dict(base_query["metric"]),
        "window": dict(base_query["window"]),
        "state": "OBSERVED",
        "value": {"kind": "integer", "value": "42"},
        "evidence": [
            {
                "evidence_id": "ev:right:1",
                "target_uri": "https://github.com/autogrammar/data2dsl",
                "source_uri": "https://github.com/autogrammar/data2dsl",
                "source_revision": "git:0000000000000000000000000000000000000000",
                "media_type": "application/json",
                "digest_sha256": "b" * 64,
                "extractor": {"id": "test", "version": "1.0.0"},
                "location": {"kind": "github-page", "endpoint": "commits", "page": 1, "cursor": None},
            }
        ],
    }


def test_matching_observations_return_match(base_query, valid_left_obs, valid_right_obs):
    comp = DeterministicComparator()
    bundle = comp.compare(base_query, valid_left_obs, valid_right_obs)
    assert bundle["result"]["outcome"] == "MATCH"
    assert bundle["result"]["delta"] is None


def test_mismatched_actor_returns_unevaluable(base_query, valid_left_obs, valid_right_obs):
    """If right observation belongs to bob while query is for alice, result must be UNEVALUABLE, not MATCH."""
    valid_right_obs["subject"]["actor"] = "bob"
    comp = DeterministicComparator()
    bundle = comp.compare(base_query, valid_left_obs, valid_right_obs)
    assert bundle["result"]["outcome"] == "UNEVALUABLE", "Mismatched actor must yield UNEVALUABLE"
    assert bundle["result"]["delta"] is None


def test_mismatched_repository_returns_unevaluable(base_query, valid_left_obs, valid_right_obs):
    valid_right_obs["subject"]["repository"] = "https://github.com/other/repo"
    comp = DeterministicComparator()
    bundle = comp.compare(base_query, valid_left_obs, valid_right_obs)
    assert bundle["result"]["outcome"] == "UNEVALUABLE"


def test_mismatched_metric_id_returns_unevaluable(base_query, valid_left_obs, valid_right_obs):
    valid_right_obs["metric"]["id"] = "git.prs.count"
    comp = DeterministicComparator()
    bundle = comp.compare(base_query, valid_left_obs, valid_right_obs)
    assert bundle["result"]["outcome"] == "UNEVALUABLE"


def test_mismatched_metric_value_kind_returns_unevaluable(base_query, valid_left_obs, valid_right_obs):
    valid_right_obs["metric"]["value_kind"] = "string"
    comp = DeterministicComparator()
    bundle = comp.compare(base_query, valid_left_obs, valid_right_obs)
    assert bundle["result"]["outcome"] == "UNEVALUABLE"


def test_mismatched_window_returns_unevaluable(base_query, valid_left_obs, valid_right_obs):
    valid_right_obs["window"]["start"] = "2026-07-01T00:00:00Z"
    comp = DeterministicComparator()
    bundle = comp.compare(base_query, valid_left_obs, valid_right_obs)
    assert bundle["result"]["outcome"] == "UNEVALUABLE"


def test_mismatched_query_id_returns_unevaluable(base_query, valid_left_obs, valid_right_obs):
    valid_right_obs["query_id"] = "query:other:id"
    comp = DeterministicComparator()
    bundle = comp.compare(base_query, valid_left_obs, valid_right_obs)
    assert bundle["result"]["outcome"] == "UNEVALUABLE"


def test_batch_comparator_rejects_cross_query_false_match(base_query, valid_left_obs, valid_right_obs):
    """Batch comparator must not pair observations across different actors/queries and declare clean."""
    batch_comp = BatchMultiQueryComparator()

    q_alice = dict(base_query)
    q_alice["query_id"] = "query:alice"
    q_alice["subject"] = {"repository": "https://github.com/autogrammar/data2dsl", "actor": "alice"}

    q_bob = dict(base_query)
    q_bob["query_id"] = "query:bob"
    q_bob["subject"] = {"repository": "https://github.com/autogrammar/data2dsl", "actor": "bob"}

    left_obs_alice = dict(valid_left_obs)
    left_obs_alice["query_id"] = "query:alice"
    left_obs_alice["subject"] = {"repository": "https://github.com/autogrammar/data2dsl", "actor": "alice"}

    right_obs_bob = dict(valid_right_obs)
    right_obs_bob["query_id"] = "query:bob"
    right_obs_bob["subject"] = {"repository": "https://github.com/autogrammar/data2dsl", "actor": "bob"}

    report = batch_comp.compare_batch(
        queries=[q_alice, q_bob],
        left_observations=[left_obs_alice],
        right_observations=[right_obs_bob],
    )

    # Neither query has both matching sides, so neither should be MATCH
    assert report.summary.matches == 0
    assert not report.summary.is_clean
