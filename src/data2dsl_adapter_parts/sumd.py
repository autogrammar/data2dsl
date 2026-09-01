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
            if "|" in line:
                cells = [c.strip() for c in line.split("|") if c.strip()]
                if len(cells) >= 2:
                    k, v = cells[0].lower(), cells[1]
                    if k == clean_key:
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
                if k == clean_key:
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


