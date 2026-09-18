"""Bounded data-network discovery public entrypoint for data2dsl."""

from __future__ import annotations

import hashlib
from collections.abc import Iterable, Mapping
from typing import Any

from data2dsl_discovery_graph import (
    GRAPH_SCHEMA,
    MAX_QUERY_TERM_LENGTH,
    MAX_QUERY_TERMS,
    MAX_SOURCE_BYTES,
    MAX_SOURCES,
    DiscoveryError,
    SENSITIVE_SCALAR,
    _canonical,
    _filter_by_query,
    _GraphBuilder,
    _stable_id,
    _validated_source,
    _walk,
)


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


