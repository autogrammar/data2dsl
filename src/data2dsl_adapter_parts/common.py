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


def observation_envelope(
    query: dict,
    obs_id: str,
    side: str,
    state: str,
    value,
    evidence: list,
) -> dict:
    """Build the standard data2dsl observation envelope."""
    return {
        "schema": SCHEMA_OBSERVATION,
        "observation_id": obs_id,
        "query_id": query["query_id"],
        "side": side,
        "subject": query["subject"],
        "metric": query["metric"],
        "window": query["window"],
        "state": state,
        "value": value,
        "evidence": evidence,
    }


def evidence_entry(
    *,
    evidence_id: str,
    target_uri: str,
    path: str,
    source_revision: str,
    digest: str,
    extractor: dict,
    location_kind: str,
    media_type: str = "application/json",
    start_line: int = 1,
    end_line: int = 1,
) -> dict:
    """Build one evidence entry for an observation."""
    return {
        "evidence_id": evidence_id,
        "target_uri": target_uri,
        "source_uri": f"{target_uri}/{path}",
        "source_revision": source_revision,
        "media_type": media_type,
        "digest_sha256": digest,
        "extractor": extractor,
        "location": {
            "kind": location_kind,
            "path": path,
            "start_line": start_line,
            "end_line": end_line,
        },
    }


def format_number(value: float | int, kind: str) -> str:
    """Format a numeric observation value."""
    if kind == "integer":
        return str(int(value))
    return f"{float(value):.2f}"


def numeric_value(raw_val: float | int | None, val_kind: str, preferred: str) -> dict | None:
    """Build a numeric value object; falls back to the other numeric kind."""
    if raw_val is None:
        return None
    if val_kind == preferred:
        return {"kind": preferred, "value": format_number(raw_val, preferred)}
    other = "float" if preferred == "integer" else "integer"
    return {"kind": other, "value": format_number(raw_val, other)}


def temperature_value(raw_val: float | None, val_kind: str) -> dict | None:
    """Build a temperature value object honouring the percentage kind."""
    if raw_val is None:
        return None
    if val_kind == "percentage":
        return {"kind": "percentage", "value": f"{float(raw_val):.2f}%"}
    return {"kind": "float", "value": f"{float(raw_val):.2f}"}


def set_value(items, val_kind: str) -> dict:
    """Build a string-set value object; an integer kind yields the item count."""
    items_sorted = sorted(list(items))
    if val_kind == "integer":
        return {"kind": "integer", "value": str(len(items_sorted))}
    return {"kind": "string-set", "items": items_sorted}


def error_observation(
    query: dict,
    *,
    prefix: str,
    side: str,
    observation_id: str | None,
    target_uri: str,
    path: str,
    status: str,
    error_message: str | None,
    extractor: dict,
    location_kind: str,
    media_type: str = "application/json",
) -> dict:
    """Build the UNEVALUABLE observation for an errored source response."""
    obs_id = observation_id or f"observation:{prefix}:unevaluable:{side}"
    err_text = error_message or f"error:{status}"
    err_digest = compute_sha256(err_text)
    evidence = [
        evidence_entry(
            evidence_id=f"evidence:{prefix}:error:{side}",
            target_uri=target_uri,
            path=path,
            source_revision=f"sha256:{err_digest}",
            digest=err_digest,
            extractor=extractor,
            location_kind=location_kind,
            media_type=media_type,
        )
    ]
    return observation_envelope(query, obs_id, side, "UNEVALUABLE", None, evidence)


def unsupported_observation(
    query: dict,
    *,
    prefix: str,
    side: str,
    observation_id: str | None,
    obs_suffix: str = "unevaluable",
    target_uri: str,
    path: str,
    source_revision: str | None,
    extractor: dict,
    location_kind: str,
    media_type: str = "application/json",
) -> dict:
    """Build the UNEVALUABLE observation for an unsupported metric query."""
    obs_id = observation_id or f"observation:{prefix}:{obs_suffix}:{side}"
    path_digest = compute_sha256(path)
    evidence = [
        evidence_entry(
            evidence_id=f"evidence:{prefix}:unsupported:{side}",
            target_uri=target_uri,
            path=path,
            source_revision=source_revision or f"sha256:{path_digest}",
            digest=path_digest,
            extractor=extractor,
            location_kind=location_kind,
            media_type=media_type,
        )
    ]
    return observation_envelope(query, obs_id, side, "UNEVALUABLE", None, evidence)
