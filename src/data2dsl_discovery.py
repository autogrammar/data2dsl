"""Deterministic discovery graph for explicit JSON registries and projections."""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections.abc import Iterable, Mapping
from typing import Any
from urllib.parse import parse_qsl, urlsplit

GRAPH_SCHEMA = "autogrammar.data2dsl/data-network/v0"
MAX_SOURCES = 32
MAX_SOURCE_BYTES = 4 * 1024 * 1024
MAX_DEPTH = 24
MAX_NODES = 5000
MAX_QUERY_TERMS = 16
MAX_QUERY_TERM_LENGTH = 80
MAX_ENTITY_ATTRIBUTES = 32
MAX_ATTRIBUTE_LENGTH = 160
ENTITY_CONTAINERS = frozenset({
    "applications", "artifacts", "bindings", "capabilities", "entries",
    "projects", "providers", "pull_requests", "repositories", "resources",
    "routes", "strategies", "tickets", "tools",
})
OPERATIONAL_ATTRIBUTE_KEYS = frozenset({
    "action", "availability", "blocked", "child_error", "child_state",
    "coding_ticket", "conclusion", "disposition", "enabled", "error_code",
    "failure_code", "health", "mode", "model", "ok", "open_issues",
    "open_pull_requests", "pending_count", "provider", "pull_request",
    "queue_depth", "readiness_scope", "ready", "ready_count", "repository",
    "running_count", "stage", "state", "status", "transport", "waiting_count",
})
ENTITY_LABEL_KEYS = ("repository", "name", "id", "ticket", "coding_ticket", "pull_request")
IDENTITY_ATTRIBUTE_KEYS = frozenset({"coding_ticket", "pull_request", "repository"})
REFERENCE_KEYS = frozenset({
    "$id", "$schema", "artifact_id", "canonical_uri", "href", "locator",
    "main_resource", "policy", "schema", "schema_ref", "source_uri", "uri",
    "url",
})
URI_PREFIXES = (
    "artifact://", "capability://", "data2dsl://", "http://", "https://",
    "knowledge://", "planfile://", "poa://", "repo://", "strategy://",
)
SENSITIVE_KEY = re.compile(
    r"(?:^|_)(?:api_?key|access_?token|password|private_?key|secret|token)(?:$|_)",
    re.IGNORECASE,
)
SENSITIVE_SUFFIXES = ("apikey", "accesstoken", "password", "privatekey", "secret", "token")
SENSITIVE_SCALAR = re.compile(
    r"(?:\b(?:sk|ghp|xoxb|xapp)[-_][A-Za-z0-9_-]{16,}\b|"
    r"\bgithub_pat_[A-Za-z0-9_]{16,}\b|\beyJ[A-Za-z0-9_-]{20,}\.)",
    re.IGNORECASE,
)
SAFE_OPERATIONAL_SCALAR = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/,=+@ -]{0,159}$")


class DiscoveryError(ValueError):
    """Raised when an explicit discovery request exceeds its safe boundary."""


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
    ).encode()


def _stable_id(kind: str, value: str) -> str:
    digest = hashlib.sha256(f"{kind}\0{value}".encode()).hexdigest()
    return f"data2dsl:{kind}:{digest[:24]}"


def _pointer(parts: Iterable[str]) -> str:
    escaped = [part.replace("~", "~0").replace("/", "~1") for part in parts]
    return "" if not escaped else "/" + "/".join(escaped)


def _reference_value(key: str, value: str) -> bool:
    lowered = key.lower()
    return (
        lowered in REFERENCE_KEYS
        or lowered.endswith(("_ref", "_uri", "_url"))
        or value.startswith(URI_PREFIXES)
    )


def _sensitive_key(key: str) -> bool:
    compact = re.sub(r"[^a-z0-9]", "", key.casefold())
    return bool(SENSITIVE_KEY.search(key)) or compact.endswith(SENSITIVE_SUFFIXES)


def _sensitive_query(uri: str) -> bool:
    return any(_sensitive_key(key) for key, _ in parse_qsl(urlsplit(uri).query))


def _query_terms(query: str | list[str] | None) -> tuple[str, ...]:
    if query is None or query == "":
        return ()
    values = [query] if isinstance(query, str) else query
    if not isinstance(values, list) or not 1 <= len(values) <= MAX_QUERY_TERMS:
        raise DiscoveryError("query_invalid")
    normalized: list[str] = []
    for value in values:
        if (
            not isinstance(value, str)
            or not value.strip()
            or len(value) > MAX_QUERY_TERM_LENGTH
        ):
            raise DiscoveryError("query_invalid")
        folded = value.casefold()
        if folded not in normalized:
            normalized.append(folded)
    return tuple(normalized)


def _safe_operational_scalar(value: Any) -> str | int | float | bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value if -(2**63) <= value < 2**63 else None
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if not isinstance(value, str) or len(value) > MAX_ATTRIBUTE_LENGTH:
        return None
    if (
        not SAFE_OPERATIONAL_SCALAR.fullmatch(value)
        or SENSITIVE_SCALAR.search(value)
        or _reference_value("value", value)
        or _sensitive_query(value)
    ):
        return None
    return value


def _entity_attributes(value: Any) -> dict[str, str | int | float | bool]:
    if not isinstance(value, Mapping):
        return {}
    attributes: dict[str, str | int | float | bool] = {}
    for key in sorted(value):
        key_text = str(key)
        if key_text.casefold() not in OPERATIONAL_ATTRIBUTE_KEYS or _sensitive_key(key_text):
            continue
        scalar = _safe_operational_scalar(value[key])
        if scalar is not None:
            attributes[key_text] = scalar
        if len(attributes) >= MAX_ENTITY_ATTRIBUTES:
            break
    return attributes


def _entity_label(value: Any, fallback: str) -> str:
    if not isinstance(value, Mapping):
        return fallback
    for key in ENTITY_LABEL_KEYS:
        scalar = _safe_operational_scalar(value.get(key))
        if scalar is not None:
            return f"{key}:{scalar}"
    return fallback


def _queryable_node_text(node: Mapping[str, Any], *, operational_only: bool) -> str:
    if not operational_only:
        return json.dumps(node, ensure_ascii=False, sort_keys=True).casefold()
    if node.get("kind") != "entity" or not isinstance(node.get("attributes"), Mapping):
        return ""
    attributes = {
        key: value for key, value in node["attributes"].items()
        if str(key).casefold() not in IDENTITY_ATTRIBUTE_KEYS
    }
    return json.dumps(attributes, ensure_ascii=False, sort_keys=True).casefold()


class _GraphBuilder:
    """Mutable node/edge registry shared by the document walkers."""

    def __init__(self) -> None:
        self.nodes: dict[str, dict[str, Any]] = {}
        self.edges: dict[tuple[str, str, str, str], dict[str, Any]] = {}
        self.redacted_fields = 0

    def add_node(self, node: dict[str, Any]) -> str:
        node_id = str(node["id"])
        self.nodes.setdefault(node_id, node)
        if len(self.nodes) > MAX_NODES:
            raise DiscoveryError("graph_node_limit_exceeded")
        return node_id

    def add_edge(self, source: str, target: str, relation: str, source_id: str) -> None:
        key = (source, target, relation, source_id)
        self.edges.setdefault(key, {
            "from": source, "to": target, "relation": relation,
            "source_id": source_id,
        })

    def add_reference(self, key_text: str, child: str, child_owner: str, source_node_id: str) -> None:
        reference_id = self.add_node({
            "id": _stable_id("reference", child),
            "kind": "reference", "label": child, "uri": child,
        })
        relation = "declares-schema" if key_text.lower() in {"$schema", "schema", "schema_ref"} else "references"
        self.add_edge(child_owner, reference_id, relation, source_node_id)


def _walk_dict_entry(
    builder: _GraphBuilder,
    key: Any,
    child: Any,
    parts: tuple[str, ...],
    owner_id: str,
    depth: int,
    source_uri: str,
    source_node_id: str,
) -> None:
    key_text = str(key)
    child_parts = (*parts, key_text)
    if _sensitive_key(key_text):
        builder.redacted_fields += 1
        return
    child_owner = owner_id
    if parts and parts[-1].lower() in ENTITY_CONTAINERS:
        child_owner = builder.add_node(_entity_node(
            source_uri, child_parts, child, key_text, source_node_id, parts[-1],
        ))
        builder.add_edge(owner_id, child_owner, "contains", source_node_id)
    if isinstance(child, str) and _reference_value(key_text, child):
        if _sensitive_query(child):
            builder.redacted_fields += 1
            return
        builder.add_reference(key_text, child, child_owner, source_node_id)
    _walk(builder, child, child_parts, child_owner, depth + 1, source_uri, source_node_id)


def _walk_list_entry(
    builder: _GraphBuilder,
    index: int,
    child: Any,
    parts: tuple[str, ...],
    owner_id: str,
    depth: int,
    source_uri: str,
    source_node_id: str,
) -> None:
    child_parts = (*parts, str(index))
    child_owner = owner_id
    if parts and parts[-1].lower() in ENTITY_CONTAINERS:
        child_owner = builder.add_node(_entity_node(
            source_uri, child_parts, child, str(index), source_node_id, parts[-1],
        ))
        builder.add_edge(owner_id, child_owner, "contains", source_node_id)
    _walk(builder, child, child_parts, child_owner, depth + 1, source_uri, source_node_id)


def _walk(
    builder: _GraphBuilder,
    value: Any,
    parts: tuple[str, ...],
    owner_id: str,
    depth: int,
    source_uri: str,
    source_node_id: str,
) -> None:
    if depth > MAX_DEPTH:
        raise DiscoveryError(
            f"source_depth_exceeded:{source_uri}{_pointer(parts)}"
        )
    if isinstance(value, dict):
        for key in sorted(value):
            _walk_dict_entry(
                builder, key, value[key], parts, owner_id, depth, source_uri, source_node_id,
            )
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _walk_list_entry(
                builder, index, child, parts, owner_id, depth, source_uri, source_node_id,
            )


def _filter_by_query(
    ordered_nodes: list[dict[str, Any]],
    ordered_edges: list[dict[str, Any]],
    query_terms: list[str],
    operational_query: bool,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Keep only query-matched nodes and the edges connecting them."""
    matched = {
        node["id"] for node in ordered_nodes
        if any(
            term in _queryable_node_text(node, operational_only=operational_query)
            for term in query_terms
        )
    }
    connected = set(matched)
    for edge in ordered_edges:
        if edge["from"] in matched or edge["to"] in matched:
            connected.update((edge["from"], edge["to"]))
    nodes = [node for node in ordered_nodes if node["id"] in connected]
    edges = [
        edge for edge in ordered_edges
        if edge["from"] in connected and edge["to"] in connected
    ]
    return nodes, edges


def discover_data_network(
    sources: Iterable[Mapping[str, Any]], *, query: str | list[str] | None = None,
) -> dict[str, Any]:
    """Build a bounded graph from explicit ``{uri, document}`` JSON sources."""
    source_rows = list(sources)
    if not 1 <= len(source_rows) <= MAX_SOURCES:
        raise DiscoveryError("source_count_out_of_bounds")
    query_terms = _query_terms(query)
    operational_query = isinstance(query, list)

    builder = _GraphBuilder()
    source_evidence: list[dict[str, Any]] = []
    source_uris: set[str] = set()

    for row in source_rows:
        uri, document = _validated_source(row, source_uris)
        source_uris.add(uri)
        raw = _canonical(document)
        if len(raw) > MAX_SOURCE_BYTES:
            raise DiscoveryError(f"source_too_large:{uri}")
        digest = hashlib.sha256(raw).hexdigest()
        source_id = builder.add_node({
            "id": _stable_id("source", uri), "kind": "source", "label": uri,
            "uri": uri, "sha256": digest,
        })
        source_evidence.append({"id": source_id, "uri": uri, "sha256": digest})
        _walk(builder, document, (), source_id, 0, uri, source_id)

    ordered_nodes = sorted(builder.nodes.values(), key=lambda item: item["id"])
    ordered_edges = sorted(
        builder.edges.values(),
        key=lambda item: (item["from"], item["to"], item["relation"], item["source_id"]),
    )
    if query_terms:
        ordered_nodes, ordered_edges = _filter_by_query(
            ordered_nodes, ordered_edges, query_terms, operational_query,
        )

    graph: dict[str, Any] = {
        "schema": GRAPH_SCHEMA,
        "query": query,
        "sources": sorted(source_evidence, key=lambda item: item["uri"]),
        "nodes": ordered_nodes,
        "edges": ordered_edges,
        "summary": {
            "source_count": len(source_evidence), "node_count": len(ordered_nodes),
            "edge_count": len(ordered_edges), "redacted_field_count": builder.redacted_fields,
        },
    }
    graph["sha256"] = hashlib.sha256(_canonical(graph)).hexdigest()
    return graph


def _validated_source(row: Any, source_uris: set[str]) -> tuple[str, Any]:
    """Validate one source row and return its ``(uri, document)`` pair."""
    if not isinstance(row, Mapping):
        raise DiscoveryError("source_entry_invalid")
    uri = row.get("uri")
    document = row.get("document")
    if not isinstance(uri, str) or not uri or not isinstance(document, (dict, list)):
        raise DiscoveryError("source_entry_invalid")
    if _sensitive_query(uri):
        raise DiscoveryError("source_uri_contains_sensitive_query")
    if uri in source_uris:
        raise DiscoveryError(f"source_uri_duplicate:{uri}")
    return uri, document


def _entity_node(
    source_uri: str,
    child_parts: tuple[str, ...],
    child: Any,
    key_text: str,
    source_node_id: str,
    container: str,
) -> dict[str, Any]:
    """Build the entity node for a container member."""
    node: dict[str, Any] = {
        "id": _stable_id("entity", f"{source_uri}#{_pointer(child_parts)}"),
        "kind": "entity",
        "label": _entity_label(child, key_text),
        "source_id": source_node_id,
        "pointer": _pointer(child_parts),
        "container": container,
    }
    attributes = _entity_attributes(child)
    if attributes:
        node["attributes"] = attributes
    return node
