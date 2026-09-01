"""Markdown source adapters for data2dsl observation normalization."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import re

from data2dsl_adapter_parts.common import DEFAULT_MDFLOW_EXTRACTOR, SCHEMA_OBSERVATION, compute_sha256



@dataclass(frozen=True)
class MarkdownClaim:
    """A metric claim extracted from markdown structure."""

    value: int
    start_line: int
    end_line: int
    path: str
    digest_sha256: str
    source_revision: str
    source_uri: str


class WorkSummaryMarkdownAdapter:
    """Adapter for extracting and normalizing metric claims from work-summary.md."""

    def __init__(self, extractor: dict[str, str] | None = None) -> None:
        self._extractor = extractor or DEFAULT_MDFLOW_EXTRACTOR

    def extract_commit_claim(
        self,
        markdown_text: str,
        actor: str,
        path: str = "work-summary.md",
        repository_uri: str = "https://github.com/autogrammar/data2dsl",
        source_revision: str | None = None,
        source_uri: str | None = None,
    ) -> MarkdownClaim | None:
        """Extract a commit count claim for the given actor from markdown text."""
        digest = compute_sha256(markdown_text)
        src_rev = source_revision or f"sha256:{digest}"
        src_uri = source_uri or f"{repository_uri}/blob/{digest}/work-summary.md"

        lines = markdown_text.splitlines()
        normalized_actor = actor.replace("github:", "").strip().lower()

        for idx, line in enumerate(lines, start=1):
            line_lower = line.lower()
            if re.search(r'(?:^|\b)' + re.escape(normalized_actor) + r'(?:\b|$)', line_lower):
                match = re.search(r"(\d+)\s*(?:commits|commit)|commits?[:\s]+(\d+)", line, re.IGNORECASE)
                if match:
                    val_str = match.group(1) or match.group(2)
                    return MarkdownClaim(
                        value=int(val_str),
                        start_line=idx,
                        end_line=idx,
                        path=path,
                        digest_sha256=digest,
                        source_revision=src_rev,
                        source_uri=src_uri,
                    )
                cells = [c.strip() for c in line.split("|") if c.strip()]
                for cell in cells:
                    if cell.isdigit():
                        return MarkdownClaim(
                            value=int(cell),
                            start_line=idx,
                            end_line=idx,
                            path=path,
                            digest_sha256=digest,
                            source_revision=src_rev,
                            source_uri=src_uri,
                        )

        return None

    def normalize(
        self,
        query: dict[str, Any],
        claim: MarkdownClaim | None,
        side: str = "left",
        observation_id: str | None = None,
    ) -> dict[str, Any]:
        """Normalize a Markdown claim into a data2dsl observation envelope."""
        query_id = query["query_id"]
        subject = query["subject"]
        metric = query["metric"]
        window = query["window"]
        target_uri = subject["repository"]

        if claim is None:
            obs_id = observation_id or f"observation:claim:unevaluable:{side}"
            return {
                "schema": SCHEMA_OBSERVATION,
                "observation_id": obs_id,
                "query_id": query_id,
                "side": side,
                "subject": subject,
                "metric": metric,
                "window": window,
                "state": "UNEVALUABLE",
                "value": None,
                "evidence": [
                    {
                        "evidence_id": f"evidence:work-summary:error:{side}",
                        "target_uri": target_uri,
                        "source_uri": f"{target_uri}/blob/unknown/work-summary.md",
                        "source_revision": f"sha256:{compute_sha256('missing-claim')}",
                        "media_type": "text/markdown",
                        "digest_sha256": compute_sha256("missing-claim"),
                        "extractor": self._extractor,
                        "location": {
                            "kind": "markdown-lines",
                            "path": "work-summary.md",
                            "start_line": 1,
                            "end_line": 1,
                        },
                    }
                ],
            }

        count = claim.value
        obs_id = observation_id or f"observation:claim:{count}"
        evidence_id = f"evidence:work-summary:lines-{claim.start_line}-{claim.end_line}"

        return {
            "schema": SCHEMA_OBSERVATION,
            "observation_id": obs_id,
            "query_id": query_id,
            "side": side,
            "subject": subject,
            "metric": metric,
            "window": window,
            "state": "OBSERVED",
            "value": {"kind": "integer", "value": str(count)},
            "evidence": [
                {
                    "evidence_id": evidence_id,
                    "target_uri": target_uri,
                    "source_uri": claim.source_uri,
                    "source_revision": claim.source_revision,
                    "media_type": "text/markdown",
                    "digest_sha256": claim.digest_sha256,
                    "extractor": self._extractor,
                    "location": {
                        "kind": "markdown-lines",
                        "path": claim.path,
                        "start_line": claim.start_line,
                        "end_line": claim.end_line,
                    },
                }
            ],
        }


# ---------------------------------------------------------------------------
# Code2Logic Adapter
# ---------------------------------------------------------------------------


