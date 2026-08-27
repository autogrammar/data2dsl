import json
from pathlib import Path

from data2dsl_subactor import simulate_self_healing_cycle
from data2dsl_cli import main as cli_main


QUERY = {
    "schema": "autogrammar.data2dsl/query/v0",
    "query_id": "query:e2e:self_healing",
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
        "start": "2026-08-01T00:00:00Z",
        "end": "2026-08-15T00:00:00Z",
        "semantics": "half-open-utc",
    },
    "left_source": {"id": "source:work-summary", "kind": "markdown"},
    "right_source": {"id": "source:diagit:github", "kind": "github"},
    "comparison": {
        "equality": "integer-exact",
        "delta_direction": "right-minus-left",
        "missing_is_zero": False,
    },
}

LEFT_OBSERVATION = {
    "schema": "autogrammar.data2dsl/observation/v0",
    "observation_id": "obs:work-summary:alice",
    "side": "left",
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
        "start": "2026-08-01T00:00:00Z",
        "end": "2026-08-15T00:00:00Z",
        "semantics": "half-open-utc",
    },
    "state": "OBSERVED",
    "value": {
        "kind": "integer",
        "value": "42",
    },
    "evidence": [
        {
            "evidence_id": "evidence:work-summary:1",
            "digest_sha256": "1111111111111111111111111111111111111111111111111111111111111111",
            "source_uri": "file:///docs/work-summary.md",
            "source_revision": "sha256:1111111111111111111111111111111111111111111111111111111111111111",
        }
    ],
}

RIGHT_OBSERVATION = {
    "schema": "autogrammar.data2dsl/observation/v0",
    "observation_id": "obs:github:alice",
    "side": "right",
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
        "start": "2026-08-01T00:00:00Z",
        "end": "2026-08-15T00:00:00Z",
        "semantics": "half-open-utc",
    },
    "state": "OBSERVED",
    "value": {
        "kind": "integer",
        "value": "40",
    },
    "evidence": [
        {
            "evidence_id": "evidence:github:1",
            "digest_sha256": "2222222222222222222222222222222222222222222222222222222222222222",
            "source_uri": "https://api.github.com/repos/autogrammar/data2dsl",
            "source_revision": "sha256:2222222222222222222222222222222222222222222222222222222222222222",
        }
    ],
}


def test_simulate_self_healing_cycle_success():
    res = simulate_self_healing_cycle(QUERY, LEFT_OBSERVATION, RIGHT_OBSERVATION)

    assert res["status"] == "HEALED"
    assert res["closed_loop_verification"]["outcome_before"] == "CONFLICT"
    assert res["closed_loop_verification"]["outcome_after"] == "MATCH"
    assert res["closed_loop_verification"]["is_clean"] is True
    assert res["remediation_actions_applied"] >= 1


def test_cli_simulate_healing(tmp_path: Path):
    query_p = tmp_path / "query.json"
    left_p = tmp_path / "left.json"
    right_p = tmp_path / "right.json"
    out_p = tmp_path / "result.json"

    query_p.write_text(json.dumps(QUERY), encoding="utf-8")
    left_p.write_text(json.dumps(LEFT_OBSERVATION), encoding="utf-8")
    right_p.write_text(json.dumps(RIGHT_OBSERVATION), encoding="utf-8")

    code = cli_main([
        "simulate-healing",
        "--query", str(query_p),
        "--left", str(left_p),
        "--right", str(right_p),
        "--output", str(out_p),
    ])

    assert code == 0
    assert out_p.exists()
    data = json.loads(out_p.read_text(encoding="utf-8"))
    assert data["status"] == "HEALED"
    assert data["closed_loop_verification"]["is_clean"] is True
