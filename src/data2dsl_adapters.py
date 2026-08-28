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
DEFAULT_CURLLM_EXTRACTOR = {"id": "semcod.curllm", "version": "0.1.0"}
DEFAULT_PLANFILE_EXTRACTOR = {"id": "semcod.planfile", "version": "0.1.0"}
DEFAULT_DETA_EXTRACTOR = {"id": "semcod.deta", "version": "0.1.0"}
DEFAULT_INTENT_CONTRACT_EXTRACTOR = {"id": "subactor.intent-contract-dsl", "version": "0.1.0"}
DEFAULT_OQL_EXTRACTOR = {"id": "oqlos.telemetry", "version": "0.1.0"}
DEFAULT_SUMD_EXTRACTOR = {"id": "semcod.sumd", "version": "0.1.0"}


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
            if normalized_actor in line_lower:
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


# ---------------------------------------------------------------------------
# Curllm Browser / BQL Source Adapter
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CurllmPageEvidence:
    """Represents page-level evidence from Curllm browser automation."""

    url: str
    digest_sha256: str
    page: int = 1
    endpoint: str = "web-page"
    source_revision: str | None = None
    media_type: str = "text/html"


@dataclass(frozen=True)
class CurllmMetricResponse:
    """Response structure from Curllm browser automation / BQL query."""

    status: str  # "OK", "ERROR", "TIMEOUT", "UNAVAILABLE"
    value: int | str | Sequence[str] | None = None
    pages: Sequence[CurllmPageEvidence] = field(default_factory=tuple)
    source_revision: str | None = None
    error_message: str | None = None


class CurllmAdapter:
    """Adapter for normalizing Curllm browser automation facts into observations."""

    def __init__(self, extractor: dict[str, str] | None = None) -> None:
        self._extractor = extractor or DEFAULT_CURLLM_EXTRACTOR

    def normalize(
        self,
        query: dict[str, Any],
        response: CurllmMetricResponse,
        side: str = "right",
        observation_id: str | None = None,
    ) -> dict[str, Any]:
        """Normalize Curllm BQL browser response into data2dsl observation."""
        query_id = query["query_id"]
        subject = query["subject"]
        metric = query["metric"]
        window = query["window"]
        target_uri = subject["repository"]

        if response.status != "OK" or response.value is None or not response.pages:
            obs_id = observation_id or f"observation:curllm:unevaluable:{side}"
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
                        "evidence_id": f"evidence:curllm:error:{side}",
                        "target_uri": target_uri,
                        "source_uri": target_uri,
                        "source_revision": f"sha256:{err_digest}",
                        "media_type": "text/html",
                        "digest_sha256": err_digest,
                        "extractor": self._extractor,
                        "location": {
                            "kind": "github-page",
                            "endpoint": "curllm-error",
                            "page": 1,
                            "cursor": None,
                        },
                    }
                ],
            }

        val_kind = metric.get("value_kind", "integer")
        val_obj: dict[str, Any]
        if val_kind == "integer":
            val_obj = {"kind": "integer", "value": str(int(response.value))}  # type: ignore[arg-type]
        elif val_kind == "string-set":
            items = sorted(list(response.value))  # type: ignore[arg-type]
            val_obj = {"kind": "string-set", "items": items}
        else:
            val_obj = {"kind": "string", "value": str(response.value)}

        evidence_list = []
        for idx, page in enumerate(response.pages, start=1):
            src_rev = page.source_revision or response.source_revision or f"sha256:{page.digest_sha256}"
            evidence_list.append(
                {
                    "evidence_id": f"evidence:curllm:page:{idx}:{page.digest_sha256[:8]}",
                    "target_uri": target_uri,
                    "source_uri": page.url,
                    "source_revision": src_rev,
                    "media_type": page.media_type,
                    "digest_sha256": page.digest_sha256,
                    "extractor": self._extractor,
                    "location": {
                        "kind": "github-page",
                        "endpoint": page.endpoint,
                        "page": page.page,
                        "cursor": None,
                    },
                }
            )

        # Sort evidence lexicographically by evidence_id
        evidence_list.sort(key=lambda e: e["evidence_id"])
        first_digest = evidence_list[0]["digest_sha256"][:8] if evidence_list else "00000000"
        obs_id = observation_id or f"observation:curllm:{first_digest}"

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
            "evidence": evidence_list,
        }


# ---------------------------------------------------------------------------
# Planfile SDLC / Ticket Adapter
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PlanfileTicketEvidence:
    """Represents a single ticket or task evidence from Planfile."""

    ticket_id: str
    title: str = ""
    status: str = "OPEN"
    path: str = "planfile.yaml"
    start_line: int = 1
    end_line: int = 1
    digest_sha256: str | None = None
    media_type: str = "application/yaml"


@dataclass(frozen=True)
class PlanfileMetricResponse:
    """Response structure from semcod/planfile query."""

    status: str  # "OK", "ERROR", "NOT_FOUND"
    tickets: Sequence[PlanfileTicketEvidence] = field(default_factory=tuple)
    count: int | None = None
    path: str = "planfile.yaml"
    source_revision: str | None = None
    error_message: str | None = None


class PlanfileAdapter:
    """Adapter for converting semcod/planfile tickets and tasks into data2dsl observations."""

    def __init__(self, extractor: dict[str, str] | None = None) -> None:
        self._extractor = extractor or DEFAULT_PLANFILE_EXTRACTOR

    def normalize(
        self,
        query: dict[str, Any],
        response: PlanfileMetricResponse,
        side: str = "left",
        observation_id: str | None = None,
    ) -> dict[str, Any]:
        """Normalize a Planfile response into a data2dsl observation envelope."""
        query_id = query["query_id"]
        subject = query["subject"]
        metric = query["metric"]
        window = query["window"]
        target_uri = subject.get("repository", "file://local/planfile")

        if response.status != "OK" or (response.count is None and not response.tickets and response.error_message):
            obs_id = observation_id or f"observation:planfile:unevaluable:{side}"
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
                        "evidence_id": f"evidence:planfile:error:{side}",
                        "target_uri": target_uri,
                        "source_uri": f"{target_uri}/{response.path}",
                        "source_revision": f"sha256:{err_digest}",
                        "media_type": "application/yaml",
                        "digest_sha256": err_digest,
                        "extractor": self._extractor,
                        "location": {
                            "kind": "yaml-lines",
                            "path": response.path,
                            "start_line": 1,
                            "end_line": 1,
                        },
                    }
                ],
            }

        val_kind = metric.get("value_kind", "integer")
        val_obj: dict[str, Any]
        if val_kind == "string-set":
            ticket_ids = sorted([t.ticket_id for t in response.tickets])
            val_obj = {"kind": "string-set", "items": ticket_ids}
        elif val_kind == "integer":
            num = response.count if response.count is not None else len(response.tickets)
            val_obj = {"kind": "integer", "value": str(num)}
        else:
            val_obj = {"kind": "string", "value": str(response.count if response.count is not None else len(response.tickets))}

        evidence_list = []
        if response.tickets:
            for t in response.tickets:
                digest = t.digest_sha256 or compute_sha256(f"{t.ticket_id}:{t.status}")
                src_rev = response.source_revision or f"sha256:{digest}"
                evidence_list.append(
                    {
                        "evidence_id": f"evidence:planfile:{t.ticket_id}:{digest[:8]}",
                        "target_uri": target_uri,
                        "source_uri": f"{target_uri}/{t.path}",
                        "source_revision": src_rev,
                        "media_type": t.media_type,
                        "digest_sha256": digest,
                        "extractor": self._extractor,
                        "location": {
                            "kind": "yaml-lines",
                            "path": t.path,
                            "start_line": t.start_line,
                            "end_line": t.end_line,
                        },
                    }
                )
        else:
            digest = compute_sha256(f"count:{response.count}")
            src_rev = response.source_revision or f"sha256:{digest}"
            evidence_list.append(
                {
                    "evidence_id": f"evidence:planfile:{response.path}:{digest[:8]}",
                    "target_uri": target_uri,
                    "source_uri": f"{target_uri}/{response.path}",
                    "source_revision": src_rev,
                    "media_type": "application/yaml",
                    "digest_sha256": digest,
                    "extractor": self._extractor,
                    "location": {
                        "kind": "yaml-lines",
                        "path": response.path,
                        "start_line": 1,
                        "end_line": 1,
                    },
                }
            )

        evidence_list.sort(key=lambda e: e["evidence_id"])
        first_digest = evidence_list[0]["digest_sha256"][:8] if evidence_list else "00000000"
        obs_id = observation_id or f"observation:planfile:{first_digest}"

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
            "evidence": evidence_list,
        }


# ---------------------------------------------------------------------------
# Deta Infrastructure / Topology Adapter
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DetaServiceEvidence:
    """Represents an infrastructure component or service from Deta topology."""

    name: str
    service_type: str = "service"
    ports: Sequence[str] = field(default_factory=tuple)
    manifest_path: str = "compose.yml"
    start_line: int = 1
    end_line: int = 1
    digest_sha256: str | None = None
    media_type: str = "application/yaml"


@dataclass(frozen=True)
class DetaTopologyResponse:
    """Response structure from semcod/deta topology analysis."""

    status: str  # "OK", "ERROR", "UNAVAILABLE"
    services: Sequence[DetaServiceEvidence] = field(default_factory=tuple)
    service_count: int | None = None
    ports: Sequence[str] = field(default_factory=tuple)
    manifest_path: str = "compose.yml"
    source_revision: str | None = None
    error_message: str | None = None


class DetaAdapter:
    """Adapter for converting semcod/deta infrastructure topology facts into data2dsl observations."""

    def __init__(self, extractor: dict[str, str] | None = None) -> None:
        self._extractor = extractor or DEFAULT_DETA_EXTRACTOR

    def normalize(
        self,
        query: dict[str, Any],
        response: DetaTopologyResponse,
        side: str = "left",
        observation_id: str | None = None,
    ) -> dict[str, Any]:
        """Normalize a Deta topology response into a data2dsl observation envelope."""
        query_id = query["query_id"]
        subject = query["subject"]
        metric = query["metric"]
        window = query["window"]
        target_uri = subject.get("repository", "file://local/infra")

        if response.status != "OK" or (response.service_count is None and not response.services and not response.ports and response.error_message):
            obs_id = observation_id or f"observation:deta:unevaluable:{side}"
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
                        "evidence_id": f"evidence:deta:error:{side}",
                        "target_uri": target_uri,
                        "source_uri": f"{target_uri}/{response.manifest_path}",
                        "source_revision": f"sha256:{err_digest}",
                        "media_type": "application/yaml",
                        "digest_sha256": err_digest,
                        "extractor": self._extractor,
                        "location": {
                            "kind": "yaml-lines",
                            "path": response.manifest_path,
                            "start_line": 1,
                            "end_line": 1,
                        },
                    }
                ],
            }

        val_kind = metric.get("value_kind", "integer")
        metric_id = (metric.get("id") or metric.get("name") or "").lower()
        metric_prop = metric.get("property", "").lower()
        is_port_query = "port" in metric_id or "port" in metric_prop or "ports" in metric_id or "ports" in metric_prop

        val_obj: dict[str, Any]
        if is_port_query:
            if val_kind == "string-set":
                val_obj = {"kind": "string-set", "items": sorted(list(response.ports))}
            else:
                val_obj = {"kind": "integer", "value": str(len(response.ports))}
        else:
            if val_kind == "string-set":
                service_names = sorted([s.name for s in response.services])
                val_obj = {"kind": "string-set", "items": service_names}
            elif val_kind == "integer":
                count = response.service_count if response.service_count is not None else len(response.services)
                val_obj = {"kind": "integer", "value": str(count)}
            else:
                count = response.service_count if response.service_count is not None else len(response.services)
                val_obj = {"kind": "string", "value": str(count)}

        evidence_list = []
        if response.services:
            for s in response.services:
                digest = s.digest_sha256 or compute_sha256(f"{s.name}:{s.service_type}")
                src_rev = response.source_revision or f"sha256:{digest}"
                evidence_list.append(
                    {
                        "evidence_id": f"evidence:deta:service:{s.name}:{digest[:8]}",
                        "target_uri": target_uri,
                        "source_uri": f"{target_uri}/{s.manifest_path}",
                        "source_revision": src_rev,
                        "media_type": s.media_type,
                        "digest_sha256": digest,
                        "extractor": self._extractor,
                        "location": {
                            "kind": "yaml-lines",
                            "path": s.manifest_path,
                            "start_line": s.start_line,
                            "end_line": s.end_line,
                        },
                    }
                )
        else:
            ports_str = ",".join(str(p) for p in sorted(response.ports))
            digest = compute_sha256(f"topology:{response.manifest_path}:{response.service_count}:{ports_str}")
            src_rev = response.source_revision or f"sha256:{digest}"
            evidence_list.append(
                {
                    "evidence_id": f"evidence:deta:{response.manifest_path}:{digest[:8]}",
                    "target_uri": target_uri,
                    "source_uri": f"{target_uri}/{response.manifest_path}",
                    "source_revision": src_rev,
                    "media_type": "application/yaml",
                    "digest_sha256": digest,
                    "extractor": self._extractor,
                    "location": {
                        "kind": "yaml-lines",
                        "path": response.manifest_path,
                        "start_line": 1,
                        "end_line": 1,
                    },
                }
            )

        evidence_list.sort(key=lambda e: e["evidence_id"])
        first_digest = evidence_list[0]["digest_sha256"][:8] if evidence_list else "00000000"
        obs_id = observation_id or f"observation:deta:{first_digest}"

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
            "evidence": evidence_list,
        }


# ---------------------------------------------------------------------------
# Subactor Intent Contract Adapter
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class IntentContractResponse:
    """Response structure from subactor/intent-contract-dsl-runtime."""

    status: str  # "OK", "ERROR", "UNAVAILABLE"
    contract_id: str = "intent-contract-001"
    parties: Sequence[str] = field(default_factory=tuple)
    deliverables: Sequence[str] = field(default_factory=tuple)
    obligations: Sequence[str] = field(default_factory=tuple)
    path: str = "intent-contract.dsl.json"
    start_line: int = 1
    end_line: int = 1
    source_revision: str | None = None
    error_message: str | None = None


class IntentContractAdapter:
    """Adapter for converting Subactor Intent Contracts into data2dsl observations."""

    def __init__(self, extractor: dict[str, str] | None = None) -> None:
        self._extractor = extractor or DEFAULT_INTENT_CONTRACT_EXTRACTOR

    def normalize(
        self,
        query: dict[str, Any],
        response: IntentContractResponse,
        side: str = "left",
        observation_id: str | None = None,
    ) -> dict[str, Any]:
        """Normalize an Intent Contract response into a data2dsl observation envelope."""
        query_id = query["query_id"]
        subject = query["subject"]
        metric = query["metric"]
        window = query["window"]
        target_uri = subject.get("repository", "file://local/contracts")

        if response.status != "OK" or response.error_message:
            obs_id = observation_id or f"observation:intent_contract:unevaluable:{side}"
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
                        "evidence_id": f"evidence:intent_contract:error:{side}",
                        "target_uri": target_uri,
                        "source_uri": f"{target_uri}/{response.path}",
                        "source_revision": f"sha256:{err_digest}",
                        "media_type": "application/json",
                        "digest_sha256": err_digest,
                        "extractor": self._extractor,
                        "location": {
                            "kind": "json-lines",
                            "path": response.path,
                            "start_line": 1,
                            "end_line": 1,
                        },
                    }
                ],
            }

        val_kind = metric.get("value_kind", "string-set")
        metric_id = (metric.get("id") or metric.get("name") or "").lower()
        metric_prop = metric.get("property", "").lower()

        val_obj: dict[str, Any]
        if "party" in metric_id or "parties" in metric_id or "parties" in metric_prop or "party" in metric_prop:
            parties_sorted = sorted(list(response.parties))
            if val_kind == "integer":
                val_obj = {"kind": "integer", "value": str(len(parties_sorted))}
            else:
                val_obj = {"kind": "string-set", "items": parties_sorted}
        elif "obligation" in metric_id or "obligations" in metric_id or "obligations" in metric_prop or "obligation" in metric_prop:
            obligations_sorted = sorted(list(response.obligations))
            if val_kind == "integer":
                val_obj = {"kind": "integer", "value": str(len(obligations_sorted))}
            else:
                val_obj = {"kind": "string-set", "items": obligations_sorted}
        elif "deliverable" in metric_id or "deliverables" in metric_id or "deliverables" in metric_prop or "deliverable" in metric_prop or not metric_id:
            deliverables_sorted = sorted(list(response.deliverables))
            if val_kind == "integer":
                val_obj = {"kind": "integer", "value": str(len(deliverables_sorted))}
            else:
                val_obj = {"kind": "string-set", "items": deliverables_sorted}
        else:
            return {
                "schema": SCHEMA_OBSERVATION,
                "observation_id": observation_id or f"observation:intent_contract:unsupported:{side}",
                "query_id": query_id,
                "side": side,
                "subject": subject,
                "metric": metric,
                "window": window,
                "state": "UNEVALUABLE",
                "value": None,
                "evidence": [
                    {
                        "evidence_id": f"evidence:intent_contract:unsupported:{side}",
                        "target_uri": target_uri,
                        "source_uri": f"{target_uri}/{response.path}",
                        "source_revision": response.source_revision or f"sha256:{compute_sha256(response.path)}",
                        "media_type": "application/json",
                        "digest_sha256": compute_sha256(response.path),
                        "extractor": self._extractor,
                        "location": {
                            "kind": "json-lines",
                            "path": response.path,
                            "start_line": 1,
                            "end_line": 1,
                        },
                    }
                ],
            }

        val_repr = ",".join(sorted(str(i) for i in val_obj["items"])) if val_obj.get("kind") == "string-set" else str(val_obj.get("value", ""))
        parties_str = ",".join(sorted(response.parties))
        obligations_str = ",".join(sorted(response.obligations))
        deliverables_str = ",".join(sorted(response.deliverables))
        digest = compute_sha256(f"{response.contract_id}:{parties_str}:{obligations_str}:{deliverables_str}:{val_repr}")
        src_rev = response.source_revision or f"sha256:{digest}"
        obs_id = observation_id or f"observation:intent_contract:{digest[:8]}"

        evidence_list = [
            {
                "evidence_id": f"evidence:intent_contract:{response.contract_id}:{digest[:8]}",
                "target_uri": target_uri,
                "source_uri": f"{target_uri}/{response.path}",
                "source_revision": src_rev,
                "media_type": "application/json",
                "digest_sha256": digest,
                "extractor": self._extractor,
                "location": {
                    "kind": "json-lines",
                    "path": response.path,
                    "start_line": response.start_line,
                    "end_line": response.end_line,
                },
            }
        ]

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
            "evidence": evidence_list,
        }


# ---------------------------------------------------------------------------
# OQL Scenario & Telemetry Adapter (oqlos)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class OqlScenarioSpecResponse:
    """Response structure representing declared specification from an OQL scenario."""

    status: str  # "OK", "UNAVAILABLE", "ERROR"
    scenario_id: str
    path: str
    start_line: int = 1
    end_line: int = 1
    sample_rate_hz: float | int | None = None
    max_temperature_celsius: float | None = None
    frequency_mhz: float | int | None = None
    packet_throughput: float | int | None = None
    active_pins: Sequence[str] = field(default_factory=tuple)
    buses: Sequence[str] = field(default_factory=tuple)
    source_revision: str | None = None
    error_message: str | None = None


@dataclass(frozen=True)
class OqlTelemetryLogResponse:
    """Response structure representing observed sensor/hardware telemetry logs."""

    status: str  # "OK", "UNAVAILABLE", "ERROR"
    log_id: str
    path: str
    start_line: int = 1
    end_line: int = 1
    avg_sample_rate_hz: float | int | None = None
    peak_temperature_celsius: float | None = None
    observed_frequency_mhz: float | int | None = None
    avg_packet_throughput: float | int | None = None
    active_pins: Sequence[str] = field(default_factory=tuple)
    active_buses: Sequence[str] = field(default_factory=tuple)
    timestamp_start: str | None = None
    timestamp_end: str | None = None
    source_revision: str | None = None
    error_message: str | None = None


class OqlTelemetryAdapter:
    """Adapter for converting OQL scenario specs and telemetry logs into data2dsl observations."""

    def __init__(self, extractor: dict[str, str] | None = None) -> None:
        self._extractor = extractor or DEFAULT_OQL_EXTRACTOR

    def normalize(
        self,
        query: dict[str, Any],
        response: OqlScenarioSpecResponse | OqlTelemetryLogResponse,
        side: str = "left",
        observation_id: str | None = None,
    ) -> dict[str, Any]:
        """Normalize an OQL spec or telemetry response into a data2dsl observation envelope."""
        if isinstance(response, OqlScenarioSpecResponse):
            return self.normalize_spec(query, response, side=side, observation_id=observation_id)
        elif isinstance(response, OqlTelemetryLogResponse):
            return self.normalize_telemetry(query, response, side=side, observation_id=observation_id)
        raise ValueError(f"Unsupported response type for OqlTelemetryAdapter: {type(response)}")

    def normalize_spec(
        self,
        query: dict[str, Any],
        response: OqlScenarioSpecResponse,
        side: str = "left",
        observation_id: str | None = None,
    ) -> dict[str, Any]:
        """Normalize an OQL scenario specification into a data2dsl observation."""
        query_id = query["query_id"]
        subject = query["subject"]
        metric = query["metric"]
        window = query["window"]
        target_uri = subject.get("repository", "file://local/oql-scenarios")

        if response.status != "OK" or response.error_message:
            obs_id = observation_id or f"observation:oql_spec:unevaluable:{side}"
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
                        "evidence_id": f"evidence:oql_spec:error:{side}",
                        "target_uri": target_uri,
                        "source_uri": f"{target_uri}/{response.path}",
                        "source_revision": f"sha256:{err_digest}",
                        "media_type": "application/json",
                        "digest_sha256": err_digest,
                        "extractor": self._extractor,
                        "location": {
                            "kind": "oql-scenario",
                            "path": response.path,
                            "start_line": 1,
                            "end_line": 1,
                        },
                    }
                ],
            }

        val_kind = metric.get("value_kind", "float")
        metric_id = (metric.get("id") or metric.get("name") or "").lower()
        metric_prop = metric.get("property", "").lower()

        val_obj: dict[str, Any]
        if "sample_rate" in metric_id or "sample_rate" in metric_prop:
            raw_val = response.sample_rate_hz
            if raw_val is None:
                val_obj = None
            elif val_kind == "integer":
                val_obj = {"kind": "integer", "value": str(int(raw_val))}
            else:
                val_obj = {"kind": "float", "value": f"{float(raw_val):.2f}"}
        elif "temperature" in metric_id or "thermal" in metric_id or "celsius" in metric_prop:
            raw_val = response.max_temperature_celsius
            if raw_val is None:
                val_obj = None
            elif val_kind == "percentage":
                val_obj = {"kind": "percentage", "value": f"{float(raw_val):.2f}%"}
            else:
                val_obj = {"kind": "float", "value": f"{float(raw_val):.2f}"}
        elif "frequency" in metric_id or "frequency_mhz" in metric_prop:
            raw_val = response.frequency_mhz
            if raw_val is None:
                val_obj = None
            elif val_kind == "integer":
                val_obj = {"kind": "integer", "value": str(int(raw_val))}
            else:
                val_obj = {"kind": "float", "value": f"{float(raw_val):.2f}"}
        elif "throughput" in metric_id or "packet_throughput" in metric_prop:
            raw_val = response.packet_throughput
            if raw_val is None:
                val_obj = None
            elif val_kind == "float":
                val_obj = {"kind": "float", "value": f"{float(raw_val):.2f}"}
            else:
                val_obj = {"kind": "integer", "value": str(int(raw_val))}
        elif "pin" in metric_id or "gpio" in metric_id or "pins" in metric_prop:
            pins_sorted = sorted(list(response.active_pins))
            if val_kind == "integer":
                val_obj = {"kind": "integer", "value": str(len(pins_sorted))}
            else:
                val_obj = {"kind": "string-set", "items": pins_sorted}
        elif "bus" in metric_id or "buses" in metric_prop:
            buses_sorted = sorted(list(response.buses))
            if val_kind == "integer":
                val_obj = {"kind": "integer", "value": str(len(buses_sorted))}
            else:
                val_obj = {"kind": "string-set", "items": buses_sorted}
        else:
            val_obj = None

        if val_obj is None:
            obs_id = observation_id or f"observation:oql_spec:unevaluable:{side}"
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
                        "evidence_id": f"evidence:oql_spec:unsupported:{side}",
                        "target_uri": target_uri,
                        "source_uri": f"{target_uri}/{response.path}",
                        "source_revision": response.source_revision or f"sha256:{compute_sha256(response.path)}",
                        "media_type": "application/json",
                        "digest_sha256": compute_sha256(response.path),
                        "extractor": self._extractor,
                        "location": {
                            "kind": "oql-scenario",
                            "path": response.path,
                            "start_line": 1,
                            "end_line": 1,
                        },
                    }
                ],
            }

        val_repr = ",".join(sorted(str(i) for i in val_obj["items"])) if val_obj.get("kind") == "string-set" else str(val_obj.get("value", ""))
        digest = compute_sha256(f"{response.scenario_id}:{response.path}:{val_repr}")
        src_rev = response.source_revision or f"sha256:{digest}"
        obs_id = observation_id or f"observation:oql_spec:{digest[:8]}"

        evidence_list = [
            {
                "evidence_id": f"evidence:oql_spec:{response.scenario_id}:{digest[:8]}",
                "target_uri": target_uri,
                "source_uri": f"{target_uri}/{response.path}",
                "source_revision": src_rev,
                "media_type": "application/json",
                "digest_sha256": digest,
                "extractor": self._extractor,
                "location": {
                    "kind": "oql-scenario",
                    "path": response.path,
                    "start_line": response.start_line,
                    "end_line": response.end_line,
                },
            }
        ]

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
            "evidence": evidence_list,
        }

    def normalize_telemetry(
        self,
        query: dict[str, Any],
        response: OqlTelemetryLogResponse,
        side: str = "right",
        observation_id: str | None = None,
    ) -> dict[str, Any]:
        """Normalize an OQL sensor/hardware telemetry log into a data2dsl observation."""
        query_id = query["query_id"]
        subject = query["subject"]
        metric = query["metric"]
        window = query["window"]
        target_uri = subject.get("repository", "file://local/oql-telemetry")

        if response.status != "OK" or response.error_message:
            obs_id = observation_id or f"observation:oql_telemetry:unevaluable:{side}"
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
                        "evidence_id": f"evidence:oql_telemetry:error:{side}",
                        "target_uri": target_uri,
                        "source_uri": f"{target_uri}/{response.path}",
                        "source_revision": f"sha256:{err_digest}",
                        "media_type": "application/json",
                        "digest_sha256": err_digest,
                        "extractor": self._extractor,
                        "location": {
                            "kind": "oql-telemetry-log",
                            "path": response.path,
                            "start_line": 1,
                            "end_line": 1,
                        },
                    }
                ],
            }

        val_kind = metric.get("value_kind", "float")
        metric_id = (metric.get("id") or metric.get("name") or "").lower()
        metric_prop = metric.get("property", "").lower()

        val_obj: dict[str, Any]
        if "sample_rate" in metric_id or "sample_rate" in metric_prop:
            raw_val = response.avg_sample_rate_hz
            if raw_val is None:
                val_obj = None
            elif val_kind == "integer":
                val_obj = {"kind": "integer", "value": str(int(raw_val))}
            else:
                val_obj = {"kind": "float", "value": f"{float(raw_val):.2f}"}
        elif "temperature" in metric_id or "thermal" in metric_id or "celsius" in metric_prop:
            raw_val = response.peak_temperature_celsius
            if raw_val is None:
                val_obj = None
            elif val_kind == "percentage":
                val_obj = {"kind": "percentage", "value": f"{float(raw_val):.2f}%"}
            else:
                val_obj = {"kind": "float", "value": f"{float(raw_val):.2f}"}
        elif "frequency" in metric_id or "frequency_mhz" in metric_prop:
            raw_val = response.observed_frequency_mhz
            if raw_val is None:
                val_obj = None
            elif val_kind == "integer":
                val_obj = {"kind": "integer", "value": str(int(raw_val))}
            else:
                val_obj = {"kind": "float", "value": f"{float(raw_val):.2f}"}
        elif "throughput" in metric_id or "packet_throughput" in metric_prop:
            raw_val = response.avg_packet_throughput
            if raw_val is None:
                val_obj = None
            elif val_kind == "float":
                val_obj = {"kind": "float", "value": f"{float(raw_val):.2f}"}
            else:
                val_obj = {"kind": "integer", "value": str(int(raw_val))}
        elif "pin" in metric_id or "gpio" in metric_id or "pins" in metric_prop:
            pins_sorted = sorted(list(response.active_pins))
            if val_kind == "integer":
                val_obj = {"kind": "integer", "value": str(len(pins_sorted))}
            else:
                val_obj = {"kind": "string-set", "items": pins_sorted}
        elif "bus" in metric_id or "buses" in metric_prop:
            buses_sorted = sorted(list(response.observed_buses))
            if val_kind == "integer":
                val_obj = {"kind": "integer", "value": str(len(buses_sorted))}
            else:
                val_obj = {"kind": "string-set", "items": buses_sorted}
        else:
            val_obj = None

        if val_obj is None:
            obs_id = observation_id or f"observation:oql_telemetry:unevaluable:{side}"
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
                        "evidence_id": f"evidence:oql_telemetry:unsupported:{side}",
                        "target_uri": target_uri,
                        "source_uri": f"{target_uri}/{response.path}",
                        "source_revision": response.source_revision or f"sha256:{compute_sha256(response.path)}",
                        "media_type": "application/json",
                        "digest_sha256": compute_sha256(response.path),
                        "extractor": self._extractor,
                        "location": {
                            "kind": "oql-telemetry-log",
                            "path": response.path,
                            "start_line": 1,
                            "end_line": 1,
                        },
                    }
                ],
            }

        val_repr = ",".join(sorted(str(i) for i in val_obj["items"])) if val_obj.get("kind") == "string-set" else str(val_obj.get("value", ""))
        digest = compute_sha256(f"{response.log_id}:{response.path}:{val_repr}")
        src_rev = response.source_revision or f"sha256:{digest}"
        obs_id = observation_id or f"observation:oql_telemetry:{digest[:8]}"

        evidence_list = [
            {
                "evidence_id": f"evidence:oql_telemetry:{response.log_id}:{digest[:8]}",
                "target_uri": target_uri,
                "source_uri": f"{target_uri}/{response.path}",
                "source_revision": src_rev,
                "media_type": "application/json",
                "digest_sha256": digest,
                "extractor": self._extractor,
                "location": {
                    "kind": "oql-telemetry-log",
                    "path": response.path,
                    "start_line": response.start_line,
                    "end_line": response.end_line,
                },
            }
        ]

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
            "evidence": evidence_list,
        }


# ---------------------------------------------------------------------------
# SUMD (Structured Unified Markdown Document) Adapter
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SUMDMetricResponse:
    status: str
    metric_key: str
    value: Any
    value_kind: str = "integer"
    document_path: str = "document.sumd.md"
    digest_sha256: str | None = None
    source_revision: str | None = None
    descriptor_id: str | None = None
    start_line: int = 1
    end_line: int = 1
    error_message: str | None = None


class SUMDAdapter:
    """Extracts and normalizes metric facts from SUMD markdown tables and descriptor blocks."""

    def __init__(self, extractor: dict[str, str] | None = None) -> None:
        self._extractor = extractor or DEFAULT_SUMD_EXTRACTOR

    def extract_table_metric(
        self,
        markdown_text: str,
        metric_id: str,
        path: str = "document.sumd.md",
        source_uri: str | None = None,
        source_revision: str | None = None,
    ) -> SUMDMetricResponse | None:
        """Parse markdown text and find table row or descriptor matching metric_id."""
        lines = markdown_text.splitlines()
        clean_key = metric_id.lower().strip()

        # Try markdown table row matching: | metric_name | value |
        for i, line in enumerate(lines, start=1):
            if "|" in line:
                cells = [c.strip() for c in line.split("|") if c.strip()]
                if len(cells) >= 2:
                    k, v = cells[0].lower(), cells[1]
                    if k == clean_key or clean_key in k:
                        if v.endswith("%"):
                            val: Any = float(v.rstrip("%").strip())
                            kind = "percentage"
                        else:
                            try:
                                val = int(v)
                                kind = "integer"
                            except ValueError:
                                try:
                                    val = float(v)
                                    kind = "float"
                                except ValueError:
                                    if "," in v or ";" in v:
                                        val = [item.strip() for item in re.split(r"[,;]+", v) if item.strip()]
                                        kind = "string-set"
                                    else:
                                        val = v
                                        kind = "string"

                        digest = compute_sha256(markdown_text)
                        return SUMDMetricResponse(
                            status="OK",
                            metric_key=metric_id,
                            value=val,
                            value_kind=kind,
                            document_path=path,
                            digest_sha256=digest,
                            source_revision=source_revision or f"sha256:{digest}",
                            start_line=i,
                            end_line=i,
                        )

        # Try descriptor or key-value pattern: metric_id: value
        for i, line in enumerate(lines, start=1):
            match = re.match(r"^([a-zA-Z0-9_.-]+)\s*:\s*(.*)$", line.strip())
            if match:
                k, v = match.group(1).lower(), match.group(2).strip()
                if k == clean_key or clean_key in k:
                    if v.endswith("%"):
                        val = float(v.rstrip("%").strip())
                        kind = "percentage"
                    else:
                        try:
                            val = int(v)
                            kind = "integer"
                        except ValueError:
                            try:
                                val = float(v)
                                kind = "float"
                            except ValueError:
                                val = v
                                kind = "string"

                    digest = compute_sha256(markdown_text)
                    return SUMDMetricResponse(
                        status="OK",
                        metric_key=metric_id,
                        value=val,
                        value_kind=kind,
                        document_path=path,
                        digest_sha256=digest,
                        source_revision=source_revision or f"sha256:{digest}",
                        start_line=i,
                        end_line=i,
                    )

        return None

    def normalize(
        self,
        query: dict[str, Any],
        response: SUMDMetricResponse | None,
        side: str = "left",
        observation_id: str | None = None,
    ) -> dict[str, Any]:
        """Normalize SUMD metric response into standard observation/v0 format."""
        query_id = query["query_id"]
        subject = query["subject"]
        metric = query["metric"]
        window = query["window"]
        target_uri = subject.get("repository", "https://github.com/autogrammar/data2dsl")

        if response is None or response.status != "OK" or response.value is None:
            digest = compute_sha256(b"none")
            evidence_list = [
                {
                    "evidence_id": f"evidence:sumd:missing:{digest[:8]}",
                    "target_uri": target_uri,
                    "source_uri": f"{target_uri}/{response.document_path if response else 'document.sumd.md'}",
                    "source_revision": f"sha256:{digest}",
                    "media_type": "text/markdown",
                    "digest_sha256": digest,
                    "extractor": self._extractor,
                    "location": {"kind": "sumd-missing", "path": response.document_path if response else "document.sumd.md"},
                }
            ]
            return {
                "schema": SCHEMA_OBSERVATION,
                "observation_id": observation_id or f"observation:sumd:unevaluable:{digest[:8]}",
                "query_id": query_id,
                "side": side,
                "subject": subject,
                "metric": metric,
                "window": window,
                "state": "UNEVALUABLE",
                "value": None,
                "evidence": evidence_list,
            }

        val_kind = metric.get("value_kind", response.value_kind)
        raw_val = response.value
        val_obj: dict[str, Any]

        if val_kind == "integer":
            val_obj = {"kind": "integer", "value": str(int(raw_val))}
        elif val_kind == "float":
            val_obj = {"kind": "float", "value": f"{float(raw_val):.2f}"}
        elif val_kind == "percentage":
            val_obj = {"kind": "percentage", "value": f"{float(raw_val):.1f}%"}
        elif val_kind == "string-set":
            if isinstance(raw_val, (list, set, tuple)):
                items = sorted(list(str(x) for x in raw_val))
            else:
                items = [str(raw_val)]
            val_obj = {"kind": "string-set", "items": items}
        else:
            val_obj = {"kind": "string", "value": str(raw_val)}

        digest = response.digest_sha256 or compute_sha256(f"{response.document_path}:{response.value}")
        src_rev = response.source_revision or f"sha256:{digest}"
        obs_id = observation_id or f"observation:sumd:{digest[:8]}"

        evidence_list = [
            {
                "evidence_id": f"evidence:sumd:{response.metric_key}:{digest[:8]}",
                "target_uri": target_uri,
                "source_uri": f"{target_uri}/{response.document_path}",
                "source_revision": src_rev,
                "media_type": "text/markdown",
                "digest_sha256": digest,
                "extractor": self._extractor,
                "location": {
                    "kind": "sumd-document",
                    "path": response.document_path,
                    "start_line": response.start_line,
                    "end_line": response.end_line,
                },
            }
        ]

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
            "evidence": evidence_list,
        }


