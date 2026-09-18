"""Sumd source adapters for data2dsl observation normalization."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import re

from data2dsl_adapter_parts.common import DEFAULT_SUMD_EXTRACTOR, SCHEMA_OBSERVATION, compute_sha256

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
            match = self._table_row_match(line, clean_key)
            if match:
                val, kind = _parse_typed_value(match)
                return self._metric_response(
                    metric_id, val, kind, path,
                    markdown_text, source_revision, i,
                )

        # Try descriptor or key-value pattern: metric_id: value
        for i, line in enumerate(lines, start=1):
            match = self._descriptor_match(line, clean_key)
            if match:
                val, kind = _parse_typed_value(match, allow_string_set=False)
                return self._metric_response(
                    metric_id, val, kind, path,
                    markdown_text, source_revision, i,
                )

        return None

    @staticmethod
    def _table_row_match(line: str, clean_key: str) -> str | None:
        """Return the raw value cell when line is a `| key | value |` row for clean_key."""
        if "|" not in line:
            return None
        cells = [cell.strip() for cell in line.split("|") if cell.strip()]
        if len(cells) >= 2 and cells[0].lower() == clean_key:
            return cells[1]
        return None

    @staticmethod
    def _descriptor_match(line: str, clean_key: str) -> str | None:
        """Return the raw value when line is a `key: value` descriptor for clean_key."""
        match = re.match(r"^([a-zA-Z0-9_.-]+)\s*:\s*(.*)$", line.strip())
        if match and match.group(1).lower() == clean_key:
            return match.group(2).strip()
        return None

    @staticmethod
    def _metric_response(
        metric_id: str,
        val: Any,
        kind: str,
        path: str,
        markdown_text: str,
        source_revision: str | None,
        line_no: int,
    ) -> SUMDMetricResponse:
        digest = compute_sha256(markdown_text)
        return SUMDMetricResponse(
            status="OK",
            metric_key=metric_id,
            value=val,
            value_kind=kind,
            document_path=path,
            digest_sha256=digest,
            source_revision=source_revision or f"sha256:{digest}",
            start_line=line_no,
            end_line=line_no,
        )


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


def _parse_typed_value(v: str, allow_string_set: bool = True) -> tuple[Any, str]:
    """Parse a raw cell/descriptor value into a typed value and its kind."""
    if v.endswith("%"):
        return float(v.rstrip("%").strip()), "percentage"
    try:
        return int(v), "integer"
    except ValueError:
        pass
    try:
        return float(v), "float"
    except ValueError:
        pass
    if allow_string_set and ("," in v or ";" in v):
        return [item.strip() for item in re.split(r"[,;]+", v) if item.strip()], "string-set"
    return v, "string"
