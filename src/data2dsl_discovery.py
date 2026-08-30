"""Deterministic discovery graph for explicit JSON registries and projections."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Iterable, Mapping
from typing import Any
from urllib.parse import parse_qsl, urlsplit

GRAPH_SCHEMA = "autogrammar.data2dsl/data-network/v0"
MAX_SOURCES = 32
MAX_SOURCE_BYTES = 4 * 1024 * 1024
MAX_DEPTH = 24
MAX_NODES = 5000
ENTITY_CONTAINERS = frozenset({
    "applications", "artifacts", "bindings", "capabilities", "entries",
    "projects", "providers", "repositories", "resources", "routes",
    "strategies", "tickets", "tools",
})
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


def discover_data_network(
    sources: Iterable[Mapping[str, Any]], *, query: str | None = None,
) -> dict[str, Any]:
    """Build a bounded graph from explicit ``{uri, document}`` JSON sources."""
    source_rows = list(sources)
    if not 1 <= len(source_rows) <= MAX_SOURCES:
        raise DiscoveryError("source_count_out_of_bounds")
    if query is not None and not isinstance(query, str):
        raise DiscoveryError("query_invalid")

    nodes: dict[str, dict[str, Any]] = {}
    edges: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    source_evidence: list[dict[str, Any]] = []
    source_uris: set[str] = set()
    redacted_fields = 0

    def add_node(node: dict[str, Any]) -> str:
        node_id = str(node["id"])
        nodes.setdefault(node_id, node)
        if len(nodes) > MAX_NODES:
            raise DiscoveryError("graph_node_limit_exceeded")
        return node_id

    def add_edge(source: str, target: str, relation: str, source_id: str) -> None:
        key = (source, target, relation, source_id)
        edges.setdefault(key, {
            "from": source, "to": target, "relation": relation,
            "source_id": source_id,
        })

    for row in source_rows:
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
        source_uris.add(uri)
        raw = _canonical(document)
        if len(raw) > MAX_SOURCE_BYTES:
            raise DiscoveryError(f"source_too_large:{uri}")
        digest = hashlib.sha256(raw).hexdigest()
        source_id = add_node({
            "id": _stable_id("source", uri), "kind": "source", "label": uri,
            "uri": uri, "sha256": digest,
        })
        source_evidence.append({"id": source_id, "uri": uri, "sha256": digest})

        def walk(
            value: Any,
            parts: tuple[str, ...],
            owner_id: str,
            depth: int,
            source_uri: str = uri,
            source_node_id: str = source_id,
        ) -> None:
            nonlocal redacted_fields
            if depth > MAX_DEPTH:
                raise DiscoveryError(
                    f"source_depth_exceeded:{source_uri}{_pointer(parts)}"
                )
            if isinstance(value, dict):
                for key in sorted(value):
                    child = value[key]
                    key_text = str(key)
                    child_parts = (*parts, key_text)
                    if _sensitive_key(key_text):
                        redacted_fields += 1
                        continue
                    child_owner = owner_id
                    if parts and parts[-1].lower() in ENTITY_CONTAINERS:
                        identity = f"{source_uri}#{_pointer(child_parts)}"
                        child_owner = add_node({
                            "id": _stable_id("entity", identity),
                            "kind": "entity", "label": key_text,
                            "source_id": source_node_id,
                            "pointer": _pointer(child_parts),
                            "container": parts[-1],
                        })
                        add_edge(owner_id, child_owner, "contains", source_node_id)
                    if isinstance(child, str) and _reference_value(key_text, child):
                        if _sensitive_query(child):
                            redacted_fields += 1
                            continue
                        reference_id = add_node({
                            "id": _stable_id("reference", child),
                            "kind": "reference", "label": child, "uri": child,
                        })
                        relation = "declares-schema" if key_text.lower() in {"$schema", "schema", "schema_ref"} else "references"
                        add_edge(child_owner, reference_id, relation, source_node_id)
                    walk(child, child_parts, child_owner, depth + 1)
            elif isinstance(value, list):
                for index, child in enumerate(value):
                    walk(child, (*parts, str(index)), owner_id, depth + 1)

        walk(document, (), source_id, 0)

    ordered_nodes = sorted(nodes.values(), key=lambda item: item["id"])
    ordered_edges = sorted(
        edges.values(),
        key=lambda item: (item["from"], item["to"], item["relation"], item["source_id"]),
    )
    if query:
        needle = query.casefold()
        matched = {
            node["id"] for node in ordered_nodes
            if needle in " ".join(str(value) for value in node.values()).casefold()
        }
        connected = set(matched)
        for edge in ordered_edges:
            if edge["from"] in matched or edge["to"] in matched:
                connected.update((edge["from"], edge["to"]))
        ordered_nodes = [node for node in ordered_nodes if node["id"] in connected]
        ordered_edges = [
            edge for edge in ordered_edges
            if edge["from"] in connected and edge["to"] in connected
        ]

    graph: dict[str, Any] = {
        "schema": GRAPH_SCHEMA,
        "query": query,
        "sources": sorted(source_evidence, key=lambda item: item["uri"]),
        "nodes": ordered_nodes,
        "edges": ordered_edges,
        "summary": {
            "source_count": len(source_evidence), "node_count": len(ordered_nodes),
            "edge_count": len(ordered_edges), "redacted_field_count": redacted_fields,
        },
    }
    graph["sha256"] = hashlib.sha256(_canonical(graph)).hexdigest()
    return graph
