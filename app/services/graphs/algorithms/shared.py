"""Shared helpers for graph algorithms.

Author: Juan Esteban Bedoya <jebedoyal@udistrital.edu.co>
"""

from __future__ import annotations

from collections import deque
from typing import Dict, Iterable, List, Set, Tuple

from app.services.graphs.models import Edge, Graph


def sorted_vertices(graph: Graph) -> List[str]:
	"""Return vertices in a stable order."""
	return sorted(graph.vertices)


def sorted_edges(graph: Graph) -> List[str]:
	"""Return edge names in a stable order."""
	return sorted(graph.edges)


def edge_signature(edge: Edge) -> Tuple[str, str]:
	"""Return an undirected signature for an edge."""
	return tuple(sorted((edge.source, edge.target)))


def undirected_neighbors(graph: Graph, excluded_edges: Iterable[str] | None = None) -> Dict[str, Set[str]]:
	"""Build undirected neighbor sets, optionally excluding edges."""
	excluded = set(excluded_edges or [])
	neighbors: Dict[str, Set[str]] = {name: set() for name in graph.vertices}
	for edge_name, edge in graph.edges.items():
		if edge_name in excluded:
			continue
		neighbors[edge.source].add(edge.target)
		neighbors[edge.target].add(edge.source)
	return neighbors


def connected_components(graph: Graph, excluded_edges: Iterable[str] | None = None) -> List[Set[str]]:
	"""Return connected components under an undirected interpretation."""
	neighbors = undirected_neighbors(graph, excluded_edges)
	remaining = set(graph.vertices)
	components: List[Set[str]] = []

	while remaining:
		start = remaining.pop()
		component = {start}
		queue = deque([start])
		while queue:
			current = queue.popleft()
			for neighbor in neighbors[current]:
				if neighbor in component:
					continue
				component.add(neighbor)
				remaining.discard(neighbor)
				queue.append(neighbor)
		components.append(component)

	return components


def is_connected(graph: Graph, excluded_edges: Iterable[str] | None = None) -> bool:
	"""Check whether the graph is connected under an undirected interpretation."""
	if not graph.vertices:
		return True
	return len(connected_components(graph, excluded_edges)) == 1


def boundary_edges(graph: Graph, left_vertices: Set[str], right_vertices: Set[str]) -> List[str]:
	"""Return edges that cross a partition of vertices."""
	boundary: List[str] = []
	for edge_name, edge in graph.edges.items():
		if {edge.source, edge.target}.issubset(left_vertices) or {edge.source, edge.target}.issubset(right_vertices):
			continue
		boundary.append(edge_name)
	return sorted(boundary)
