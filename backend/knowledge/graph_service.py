"""knowledge/graph_service.py — Knowledge graph with PostgreSQL recursive CTEs."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class GraphNode:
    id: str
    label: str
    node_type: str
    confidence: float = 0.5

@dataclass
class GraphEdge:
    source: str
    target: str
    relationship: str
    confidence: float = 0.5

@dataclass
class KnowledgeGraph:
    nodes: list[GraphNode] = field(default_factory=list)
    edges: list[GraphEdge] = field(default_factory=list)


class KnowledgeGraphService:
    def __init__(self, db_client=None):
        self.db = db_client
        self._nodes: dict[str, GraphNode] = {}
        self._edges: list[GraphEdge] = []

    def add_node(self, node_id: str, label: str, node_type: str, confidence: float = 0.5) -> None:
        self._nodes[node_id] = GraphNode(node_id, label, node_type, confidence)

    def add_edge(self, source: str, target: str, relationship: str, confidence: float = 0.5) -> None:
        self._edges.append(GraphEdge(source, target, relationship, confidence))

    def build_from_extraction(self, extraction: Any, document_id: str = "") -> KnowledgeGraph:
        graph = KnowledgeGraph()
        for concept in getattr(extraction, "concepts", []):
            node_id = f"concept:{concept.name.lower().replace(' ', '_')}"
            graph.nodes.append(GraphNode(node_id, concept.name, "concept", concept.confidence))
        for formula in getattr(extraction, "formulas", []):
            node_id = f"formula:{hash(formula.latex) % 100000}"
            graph.nodes.append(GraphNode(node_id, formula.latex, "formula", formula.confidence))
        for prereq in getattr(extraction, "prerequisites", []):
            target_id = f"concept:{prereq.lower().replace(' ', '_')}"
            graph.nodes.append(GraphNode(target_id, prereq, "concept", 0.5))
        # Add edges: concept -> prerequisite
        for concept in getattr(extraction, "concepts", []):
            for prereq in getattr(extraction, "prerequisites", []):
                source = f"concept:{concept.name.lower().replace(' ', '_')}"
                target = f"concept:{prereq.lower().replace(' ', '_')}"
                graph.edges.append(GraphEdge(source, target, "prerequisite", 0.5))
        # Add edges: chapter -> topic (part-of)
        for chapter in getattr(extraction, "chapters", []):
            for topic in getattr(extraction, "topics", []):
                graph.edges.append(GraphEdge(
                    f"chapter:{chapter.lower().replace(' ', '_')}",
                    f"topic:{topic.lower().replace(' ', '_')}",
                    "part-of", 0.5
                ))
        return graph

    def get_prerequisites(self, concept_id: str, max_depth: int = 5) -> list[str]:
        """Get all prerequisites for a concept using BFS (recursive CTE equivalent)."""
        visited = set()
        queue = [(concept_id, 0)]
        prerequisites = []
        while queue:
            current, depth = queue.pop(0)
            if depth > max_depth or current in visited:
                continue
            visited.add(current)
            for edge in self._edges:
                if edge.source == current and edge.relationship == "prerequisite":
                    prerequisites.append(edge.target)
                    queue.append((edge.target, depth + 1))
        return prerequisites

    def get_learning_path(self, start_concept: str, target_concept: str) -> list[str]:
        """BFS shortest path from start to target."""
        from collections import deque
        queue = deque([(start_concept, [start_concept])])
        visited = {start_concept}
        while queue:
            current, path = queue.popleft()
            if current == target_concept:
                return path
            for edge in self._edges:
                if edge.source == current and edge.relationship in {"prerequisite", "related"}:
                    if edge.target not in visited:
                        visited.add(edge.target)
                        queue.append((edge.target, path + [edge.target]))
        return []

    def find_gaps(self, known_concepts: list[str], target_concept: str) -> list[str]:
        """Find missing prerequisites for a target concept."""
        needed = set(self.get_prerequisites(target_concept))
        known = set(known_concepts)
        return list(needed - known)

    def to_dict(self) -> dict[str, Any]:
        return {
            "nodes": [{"id": n.id, "label": n.label, "type": n.node_type, "confidence": n.confidence} for n in self._nodes.values()],
            "edges": [{"source": e.source, "target": e.target, "relationship": e.relationship, "confidence": e.confidence} for e in self._edges]
        }
