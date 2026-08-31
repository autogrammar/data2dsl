"""Tests verifying resolution of remediation feed schema collision (F09)."""

from data2dsl_remediation import RemediationIntentFormatter, format_remediation_intent


def test_remediation_feed_schema_distinct_from_governance_intent():
    """F09: Schema identifier must be autogrammar.data2dsl/remediation-feed/v0 to avoid collision with governance schema."""
    assert RemediationIntentFormatter.SCHEMA_VERSION == "autogrammar.data2dsl/remediation-feed/v0"
    assert RemediationIntentFormatter.SCHEMA_VERSION != "new-project.remediation-intent/v1"


def test_remediation_feed_structure():
    """F09: Remediation feed output must contain expected top-level properties."""
    bundle = {
        "schema": "autogrammar.data2dsl/comparison-bundle/v0",
        "query": {
            "schema": "autogrammar.data2dsl/query/v0",
            "query_id": "query:test",
            "subject": {"repository": "https://github.com/autogrammar/data2dsl", "actor": "alice"},
            "metric": {"id": "git.commit.count", "version": "v1", "value_kind": "integer", "unit": "commits"},
            "window": {"start": "2026-08-01T00:00:00Z", "end": "2026-08-27T00:00:00Z", "semantics": "half-open-utc"},
        },
        "observations": [
            {
                "observation_id": "obs:left:1",
                "query_id": "query:test",
                "side": "left",
                "subject": {"repository": "https://github.com/autogrammar/data2dsl", "actor": "alice"},
                "metric": {"id": "git.commit.count", "version": "v1", "value_kind": "integer", "unit": "commits"},
                "window": {"start": "2026-08-01T00:00:00Z", "end": "2026-08-27T00:00:00Z", "semantics": "half-open-utc"},
                "state": "OBSERVED",
                "value": {"kind": "integer", "value": "10"},
                "evidence": [{"evidence_id": "ev:left:1", "digest_sha256": "aaa", "source_uri": "uri:l", "source_revision": "sha256:aaa"}],
            },
            {
                "observation_id": "obs:right:1",
                "query_id": "query:test",
                "side": "right",
                "subject": {"repository": "https://github.com/autogrammar/data2dsl", "actor": "alice"},
                "metric": {"id": "git.commit.count", "version": "v1", "value_kind": "integer", "unit": "commits"},
                "window": {"start": "2026-08-01T00:00:00Z", "end": "2026-08-27T00:00:00Z", "semantics": "half-open-utc"},
                "state": "OBSERVED",
                "value": {"kind": "integer", "value": "10"},
                "evidence": [{"evidence_id": "ev:right:1", "digest_sha256": "bbb", "source_uri": "uri:r", "source_revision": "sha256:bbb"}],
            },
        ],
        "result": {
            "schema": "autogrammar.data2dsl/comparison-result/v0",
            "query_id": "query:test",
            "outcome": "MATCH",
            "delta": None,
            "evidence_ids": [],
        },
    }

    feed = format_remediation_intent(bundle, ticket_id="ticket-067")
    assert feed["schema"] == "autogrammar.data2dsl/remediation-feed/v0"
    assert feed["status"] == "SATISFIED"
    assert feed["ticket"] == "ticket-067"
    assert isinstance(feed["actionable_items"], list)
    assert isinstance(feed["evidence_digest"], list)
