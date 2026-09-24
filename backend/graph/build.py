"""Construction of the NetworkX MultiDiGraph from resolved entities and edges."""

from __future__ import annotations

import sys
from pathlib import Path

import networkx as nx

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.schema import Edge, Entity, edges_from_json, entities_from_json

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures"
ENTITIES_FIXTURE = FIXTURE_DIR / "resolved_entities_sample.json"
EDGES_FIXTURE = FIXTURE_DIR / "resolved_edges_sample.json"


def build_graph(entities: list[Entity], edges: list[Edge]) -> nx.MultiDiGraph:
    """Build a directed multigraph from resolved entities and edges.

    Nodes are keyed by entity id; edges keep every parallel observation
    between the same pair of nodes (call records, transactions, ...).
    """
    graph = nx.MultiDiGraph()

    for entity in entities:
        graph.add_node(
            entity.id,
            type=entity.type.value,
            attributes=dict(entity.attributes),
            source_tags=list(entity.source_tags),
            first_seen=entity.first_seen,
        )

    for edge in edges:
        missing = [n for n in (edge.source_id, edge.target_id) if n not in graph]
        if missing:
            print(
                f"warning: dropping edge {edge.source_id!r}->{edge.target_id!r} "
                f"({edge.type.value}), unknown node(s): {', '.join(missing)}",
                file=sys.stderr,
            )
            continue
        graph.add_edge(
            edge.source_id,
            edge.target_id,
            type=edge.type.value,
            timestamp=edge.timestamp,
            source_tag=edge.source_tag,
            weight=edge.weight,
            metadata=dict(edge.metadata),
        )

    return graph


def node_types(graph: nx.MultiDiGraph) -> list[str]:
    """Sorted list of distinct entity types present in the graph."""
    return sorted({data["type"] for _, data in graph.nodes(data=True)})


if __name__ == "__main__":
    entities = entities_from_json(ENTITIES_FIXTURE)
    edges = edges_from_json(EDGES_FIXTURE)
    graph = build_graph(entities, edges)
    print(f"Nodes: {graph.number_of_nodes()}")
    print(f"Edges: {graph.number_of_edges()}")
    print(f"Node types: {', '.join(node_types(graph))}")
