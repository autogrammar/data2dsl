"""Tests verifying subactor authority token exact matching and diagnostic summary resolution (F13)."""

from data2dsl_subactor import (
    simulate_self_healing_cycle,
    validate_delegation_envelope,
)


def test_subactor_authority_exact_token_matching():
    """F13: Subactor authority must strictly match allowed tokens, rejecting substrings like unauthorized_plan."""
    # Invalid: contains "plan" as substring inside "unauthorized_plan"
    invalid_env = {
        "role": "supervisor",
        "goal": "Test goal",
        "scope": "tests/**",
        "acceptance": "all pass",
        "authority": "unauthorized_plan",
        "limits": "none",
        "report": "stdout",
    }
    res = validate_delegation_envelope(invalid_env)
    assert not res.valid
    assert any(e.code == "COMM-AUTH-001" for e in res.errors)

    # Valid: exact keyword "plan"
    valid_env = dict(invalid_env, authority="plan, dry-run")
    res_valid = validate_delegation_envelope(valid_env)
    assert res_valid.valid


def test_simulate_self_healing_diagnostic_severity_summary():
    """F13: simulate_self_healing_cycle includes valid diagnostic_severity_summary dictionary."""
    query = {
        "schema": "autogrammar.data2dsl/query/v0",
        "query_id": "query:healing:test",
        "subject": {"repository": "https://github.com/autogrammar/data2dsl", "actor": "alice"},
        "metric": {"id": "git.commit.count", "version": "v1", "value_kind": "integer", "unit": "commits"},
        "window": {"start": "2026-08-01T00:00:00Z", "end": "2026-08-27T00:00:00Z", "semantics": "half-open-utc"},
        "left_source": {"id": "s:l", "kind": "markdown"},
        "right_source": {"id": "s:r", "kind": "github"},
        "comparison": {"equality": "integer-exact", "delta_direction": "right-minus-left", "missing_is_zero": False},
    }

    left_obs = {
        "schema": "autogrammar.data2dsl/observation/v0",
        "observation_id": "obs:l:1",
        "query_id": "query:healing:test",
        "side": "left",
        "subject": {"repository": "https://github.com/autogrammar/data2dsl", "actor": "alice"},
        "metric": {"id": "git.commit.count", "version": "v1", "value_kind": "integer", "unit": "commits"},
        "window": {"start": "2026-08-01T00:00:00Z", "end": "2026-08-27T00:00:00Z", "semantics": "half-open-utc"},
        "state": "OBSERVED",
        "value": {"kind": "integer", "value": "10"},
        "evidence": [],
    }

    right_obs = {
        "schema": "autogrammar.data2dsl/observation/v0",
        "observation_id": "obs:r:1",
        "query_id": "query:healing:test",
        "side": "right",
        "subject": {"repository": "https://github.com/autogrammar/data2dsl", "actor": "alice"},
        "metric": {"id": "git.commit.count", "version": "v1", "value_kind": "integer", "unit": "commits"},
        "window": {"start": "2026-08-01T00:00:00Z", "end": "2026-08-27T00:00:00Z", "semantics": "half-open-utc"},
        "state": "OBSERVED",
        "value": {"kind": "integer", "value": "8"},
        "evidence": [],
    }

    healing = simulate_self_healing_cycle(query, left_obs, right_obs)
    assert healing["status"] == "HEALED"
    summary = healing["pre_repair"]["diagnostic_severity_summary"]
    assert summary is not None
    assert isinstance(summary, dict)
    assert "total" in summary
