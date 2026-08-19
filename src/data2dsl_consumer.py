"""Reasoning consumer integration feed for todo2code and external decision engines.

Maintains strict separation of concerns:
- data2dsl provides factual outcomes, typed deltas, and cryptographic evidence envelopes.
- todo2code / consumers perform policy decisions, semantic reasoning, and mutations.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any

from data2dsl_contract_v0.validate import validate_document


def compute_sha256(content: str | bytes) -> str:
    if isinstance(content, str):
        content = content.encode("utf-8")
    return hashlib.sha256(content).hexdigest()


@dataclass(frozen=True)
class ConsumerEvidenceFact:
    evidence_id: str
    target_uri: str
    source_uri: str
    source_revision: str
    media_type: str
    digest_sha256: str
    extractor: dict[str, str]
    location: dict[str, Any]


@dataclass(frozen=True)
class ReasoningFactPayload:
    """Factual export feed structure consumed by todo2code reasoning engines."""

    schema: str
    feed_id: str
    query_id: str
    subject: dict[str, str]
    metric: dict[str, str]
    window: dict[str, str]
    outcome: str
    delta: dict[str, Any] | None
    left_summary: dict[str, Any]
    right_summary: dict[str, Any]
    evidence: list[ConsumerEvidenceFact]
    factual_digest: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "feed_id": self.feed_id,
            "query_id": self.query_id,
            "subject": self.subject,
            "metric": self.metric,
            "window": self.window,
            "outcome": self.outcome,
            "delta": self.delta,
            "left_summary": self.left_summary,
            "right_summary": self.right_summary,
            "evidence": [
                {
                    "evidence_id": ev.evidence_id,
                    "target_uri": ev.target_uri,
                    "source_uri": ev.source_uri,
                    "source_revision": ev.source_revision,
                    "media_type": ev.media_type,
                    "digest_sha256": ev.digest_sha256,
                    "extractor": ev.extractor,
                    "location": ev.location,
                }
                for ev in self.evidence
            ],
            "factual_digest": self.factual_digest,
        }


class ConsumerFactFeed:
    """Transforms data2dsl comparison bundles into factual reasoning payloads for consumers."""

    FEED_SCHEMA = "autogrammar.data2dsl/consumer-fact-feed/v0"

    @classmethod
    def export_reasoning_payload(
        cls, bundle: dict[str, Any], *, validate: bool = True
    ) -> ReasoningFactPayload:
        """Export a validated data2dsl comparison bundle into a consumer reasoning fact feed."""
        if validate:
            validate_document(bundle)

        query = bundle["query"]
        result = bundle["result"]
        observations = bundle["observations"]

        obs_by_side = {obs["side"]: obs for obs in observations}
        left_obs = obs_by_side.get("left")
        right_obs = obs_by_side.get("right")

        left_summary = {
            "observation_id": left_obs["observation_id"] if left_obs else None,
            "state": left_obs["state"] if left_obs else "MISSING",
            "value": left_obs["value"] if left_obs else None,
        }
        right_summary = {
            "observation_id": right_obs["observation_id"] if right_obs else None,
            "state": right_obs["state"] if right_obs else "MISSING",
            "value": right_obs["value"] if right_obs else None,
        }

        all_evidence: list[ConsumerEvidenceFact] = []
        for obs in observations:
            for ev in obs.get("evidence", []):
                all_evidence.append(
                    ConsumerEvidenceFact(
                        evidence_id=ev["evidence_id"],
                        target_uri=ev["target_uri"],
                        source_uri=ev["source_uri"],
                        source_revision=ev["source_revision"],
                        media_type=ev["media_type"],
                        digest_sha256=ev["digest_sha256"],
                        extractor=ev["extractor"],
                        location=ev["location"],
                    )
                )

        bundle_canonical = json.dumps(bundle, sort_keys=True, separators=(",", ":"))
        factual_digest = compute_sha256(bundle_canonical)
        feed_id = f"fact-feed:{query['query_id']}"

        return ReasoningFactPayload(
            schema=cls.FEED_SCHEMA,
            feed_id=feed_id,
            query_id=query["query_id"],
            subject=query["subject"],
            metric=query["metric"],
            window=query["window"],
            outcome=result["outcome"],
            delta=result.get("delta"),
            left_summary=left_summary,
            right_summary=right_summary,
            evidence=all_evidence,
            factual_digest=f"sha256:{factual_digest}",
        )
