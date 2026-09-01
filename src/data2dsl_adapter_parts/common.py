"""Shared constants and helpers for data2dsl source adapters."""

from __future__ import annotations

import hashlib

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
