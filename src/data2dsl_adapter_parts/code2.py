"""Code2 source adapters for data2dsl observation normalization."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence


from data2dsl_adapter_parts.common import (
    DEFAULT_CODE2LOGIC_EXTRACTOR,
    DEFAULT_CODE2SCHEMA_EXTRACTOR,
    SCHEMA_OBSERVATION,
    compute_sha256,
)

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
                    "evidence_id": f"evidence:code2logic:{response.path.replace('/', ':')}:{response.start_line}-{response.end_line}",
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
                    "evidence_id": f"evidence:code2schema:{response.path.replace('/', ':')}:{response.start_line}-{response.end_line}",
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


