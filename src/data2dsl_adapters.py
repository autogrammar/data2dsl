"""Adapters for acquiring and normalizing facts from external sources into data2dsl observations."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Any, Sequence


SCHEMA_OBSERVATION = "autogrammar.data2dsl/observation/v0"
DEFAULT_DIAGIT_EXTRACTOR = {"id": "subactor.diagit", "version": "0.1.0"}
DEFAULT_MDFLOW_EXTRACTOR = {"id": "semcod.mdflow", "version": "0.1.0"}
DEFAULT_CODE2LOGIC_EXTRACTOR = {"id": "semcod.code2logic", "version": "0.1.0"}
DEFAULT_CODE2SCHEMA_EXTRACTOR = {"id": "semcod.code2schema", "version": "0.1.0"}


def compute_sha256(content: str | bytes) -> str:
    """Compute a hex SHA-256 digest of text or bytes."""
    if isinstance(content, str):
        content = content.encode("utf-8")
    return hashlib.sha256(content).hexdigest()


# ---------------------------------------------------------------------------
# GitHub Diagit Adapter
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DiagitPageEvidence:
    """Represents raw page response evidence from the Diagit GitHub provider."""

    page: int
    endpoint: str
    digest_sha256: str
    source_revision: str
    source_uri: str
    cursor: str | None = None
    media_type: str = "application/json"


@dataclass(frozen=True)
class DiagitCommitMetricResponse:
    """Response structure from the extended Diagit GitHub provider for commit metrics."""

    status: str  # "OK", "NOT_FOUND", "UNAVAILABLE", "ERROR"
    commit_count: int | None = None
    pages: Sequence[DiagitPageEvidence] = field(default_factory=tuple)
    error_message: str | None = None


class GitHubDiagitAdapter:
    """Adapter for converting Diagit GitHub metrics into data2dsl observations."""

    def __init__(self, extractor: dict[str, str] | None = None) -> None:
        self._extractor = extractor or DEFAULT_DIAGIT_EXTRACTOR

    def normalize(
        self,
        query: dict[str, Any],
        response: DiagitCommitMetricResponse,
        side: str = "right",
        observation_id: str | None = None,
    ) -> dict[str, Any]:
        """Normalize a Diagit provider response into a data2dsl observation envelope."""
        query_id = query["query_id"]
        subject = query["subject"]
        metric = query["metric"]
        window = query["window"]
        target_uri = subject["repository"]
        endpoint = "/repos" + target_uri.replace("https://github.com", "") + "/commits"

        if response.status != "OK" or response.commit_count is None:
            obs_id = observation_id or f"observation:github:unevaluable:{side}"
            err_text = response.error_message or f"error:{response.status}"
            err_digest = compute_sha256(err_text)
            err_rev = f"sha256:{err_digest}"
            ev_id = f"evidence:github:error:{side}"
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
                        "evidence_id": ev_id,
                        "target_uri": target_uri,
                        "source_uri": f"https://api.github.com{endpoint}",
                        "source_revision": err_rev,
                        "media_type": "application/json",
                        "digest_sha256": err_digest,
                        "extractor": self._extractor,
                        "location": {
                            "kind": "github-page",
                            "endpoint": endpoint,
                            "page": 1,
                            "cursor": None,
                        },
                    }
                ],
            }

        count = response.commit_count
        obs_id = observation_id or f"observation:github:{count}"

        evidence_list: list[dict[str, Any]] = []
        if response.pages:
            for page_ev in response.pages:
                ev_id = f"evidence:github:commits:page-{page_ev.page}"
                evidence_list.append(
                    {
                        "evidence_id": ev_id,
                        "target_uri": target_uri,
                        "source_uri": page_ev.source_uri,
                        "source_revision": page_ev.source_revision,
                        "media_type": page_ev.media_type,
                        "digest_sha256": page_ev.digest_sha256,
                        "extractor": self._extractor,
                        "location": {
                            "kind": "github-page",
                            "endpoint": page_ev.endpoint,
                            "page": page_ev.page,
                            "cursor": page_ev.cursor,
                        },
                    }
                )
        else:
            dummy_digest = compute_sha256(f"{target_uri}:{count}:{window['start']}:{window['end']}")
            dummy_rev = f"sha256:{dummy_digest}"
            evidence_list.append(
                {
                    "evidence_id": "evidence:github:commits:page-1",
                    "target_uri": target_uri,
                    "source_uri": f"https://api.github.com{endpoint}",
                    "source_revision": dummy_rev,
                    "media_type": "application/json",
                    "digest_sha256": dummy_digest,
                    "extractor": self._extractor,
                    "location": {
                        "kind": "github-page",
                        "endpoint": endpoint,
                        "page": 1,
                        "cursor": None,
                    },
                }
            )

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
            "evidence": evidence_list,
        }


def build_github_commit_observation(
    query: dict[str, Any],
    commit_count: int | None,
    pages: Sequence[DiagitPageEvidence] = (),
    status: str = "OK",
    side: str = "right",
    observation_id: str | None = None,
) -> dict[str, Any]:
    """Convenience helper to construct a normalized observation from raw commit fields."""
    adapter = GitHubDiagitAdapter()
    response = DiagitCommitMetricResponse(
        status=status,
        commit_count=commit_count,
        pages=pages,
    )
    return adapter.normalize(query, response, side=side, observation_id=observation_id)


# ---------------------------------------------------------------------------
# Markdown Adapter
# ---------------------------------------------------------------------------


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
            if normalized_actor in line_lower or "commit" in line_lower:
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


@dataclass(frozen=True)
class Code2LogicMetricResponse:
    """Response from code2logic control/data/call-flow analyzer."""

    status: str  # "OK", "ERROR"
    value: int | str | None = None
    value_kind: str = "integer"
    path: str = "src/main.py"
    start_line: int = 1
    end_line: int = 1
    source_revision: str | None = None
    error_message: str | None = None


class Code2LogicAdapter:
    """Adapter for normalizing code2logic analyzer facts into observations."""

    def __init__(self, extractor: dict[str, str] | None = None) -> None:
        self._extractor = extractor or DEFAULT_CODE2LOGIC_EXTRACTOR

    def normalize(
        self,
        query: dict[str, Any],
        response: Code2LogicMetricResponse,
        side: str = "right",
        observation_id: str | None = None,
    ) -> dict[str, Any]:
        """Normalize code2logic response into data2dsl observation."""
        query_id = query["query_id"]
        subject = query["subject"]
        metric = query["metric"]
        window = query["window"]
        target_uri = subject["repository"]

        if response.status != "OK" or response.value is None:
            obs_id = observation_id or f"observation:code2logic:unevaluable:{side}"
            err_text = response.error_message or f"error:{response.status}"
            err_digest = compute_sha256(err_text)
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
                        "evidence_id": f"evidence:code2logic:error:{side}",
                        "target_uri": target_uri,
                        "source_uri": f"{target_uri}/blob/unknown/{response.path}",
                        "source_revision": f"sha256:{err_digest}",
                        "media_type": "text/markdown",
                        "digest_sha256": err_digest,
                        "extractor": self._extractor,
                        "location": {
                            "kind": "markdown-lines",
                            "path": response.path,
                            "start_line": 1,
                            "end_line": 1,
                        },
                    }
                ],
            }

        val_obj: dict[str, Any]
        if response.value_kind == "integer":
            val_obj = {"kind": "integer", "value": str(response.value)}
        else:
            val_obj = {"kind": "string", "value": str(response.value)}

        digest = compute_sha256(f"{response.path}:{response.value}")
        src_rev = response.source_revision or f"sha256:{digest}"
        obs_id = observation_id or f"observation:code2logic:{response.value}"

        return {
            "schema": SCHEMA_OBSERVATION,
            "observation_id": obs_id,
            "query_id": query_id,
            "side": side,
            "subject": subject,
            "metric": metric,
            "window": window,
            "state": "OBSERVED",
            "value": val_obj,
            "evidence": [
                {
                    "evidence_id": f"evidence:code2logic:{response.path}:{response.start_line}-{response.end_line}",
                    "target_uri": target_uri,
                    "source_uri": f"{target_uri}/blob/{digest}/{response.path}",
                    "source_revision": src_rev,
                    "media_type": "text/markdown",
                    "digest_sha256": digest,
                    "extractor": self._extractor,
                    "location": {
                        "kind": "markdown-lines",
                        "path": response.path,
                        "start_line": response.start_line,
                        "end_line": response.end_line,
                    },
                }
            ],
        }


# ---------------------------------------------------------------------------
# Code2Schema Adapter
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Code2SchemaMetricResponse:
    """Response from code2schema semantic/schema analyzer."""

    status: str  # "OK", "ERROR"
    entities: Sequence[str] = field(default_factory=tuple)
    path: str = "src/schema.py"
    start_line: int = 1
    end_line: int = 1
    source_revision: str | None = None
    error_message: str | None = None


class Code2SchemaAdapter:
    """Adapter for normalizing code2schema analyzer facts into observations."""

    def __init__(self, extractor: dict[str, str] | None = None) -> None:
        self._extractor = extractor or DEFAULT_CODE2SCHEMA_EXTRACTOR

    def normalize(
        self,
        query: dict[str, Any],
        response: Code2SchemaMetricResponse,
        side: str = "right",
        observation_id: str | None = None,
    ) -> dict[str, Any]:
        """Normalize code2schema response into data2dsl observation."""
        query_id = query["query_id"]
        subject = query["subject"]
        metric = query["metric"]
        window = query["window"]
        target_uri = subject["repository"]

        if response.status != "OK":
            obs_id = observation_id or f"observation:code2schema:unevaluable:{side}"
            err_text = response.error_message or f"error:{response.status}"
            err_digest = compute_sha256(err_text)
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
                        "evidence_id": f"evidence:code2schema:error:{side}",
                        "target_uri": target_uri,
                        "source_uri": f"{target_uri}/blob/unknown/{response.path}",
                        "source_revision": f"sha256:{err_digest}",
                        "media_type": "text/markdown",
                        "digest_sha256": err_digest,
                        "extractor": self._extractor,
                        "location": {
                            "kind": "markdown-lines",
                            "path": response.path,
                            "start_line": 1,
                            "end_line": 1,
                        },
                    }
                ],
            }

        sorted_entities = sorted(response.entities)
        val_kind = metric.get("value_kind", "string-set")
        val_obj: dict[str, Any]
        if val_kind == "integer":
            val_obj = {"kind": "integer", "value": str(len(sorted_entities))}
        else:
            val_obj = {"kind": "string-set", "items": sorted_entities}

        digest = compute_sha256(",".join(sorted_entities))
        src_rev = response.source_revision or f"sha256:{digest}"
        obs_id = observation_id or f"observation:code2schema:{digest[:8]}"

        return {
            "schema": SCHEMA_OBSERVATION,
            "observation_id": obs_id,
            "query_id": query_id,
            "side": side,
            "subject": subject,
            "metric": metric,
            "window": window,
            "state": "OBSERVED",
            "value": val_obj,
            "evidence": [
                {
                    "evidence_id": f"evidence:code2schema:{response.path}:{response.start_line}-{response.end_line}",
                    "target_uri": target_uri,
                    "source_uri": f"{target_uri}/blob/{digest}/{response.path}",
                    "source_revision": src_rev,
                    "media_type": "text/markdown",
                    "digest_sha256": digest,
                    "extractor": self._extractor,
                    "location": {
                        "kind": "markdown-lines",
                        "path": response.path,
                        "start_line": response.start_line,
                        "end_line": response.end_line,
                    },
                }
            ],
        }
