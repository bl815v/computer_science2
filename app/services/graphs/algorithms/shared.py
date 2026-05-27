"""Shared helpers for graph algorithms.

Provide reusable utility functions for graph traversal, connectivity,
edge classification, and stable ordering used across graph algorithms.

Author: Juan Esteban Bedoya <jebedoyal@udistrital.edu.co>

This file is part of ComputerScience2 project.

ComputerScience2 is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

ComputerScience2 is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with ComputerScience2. If not, see <https://www.gnu.org/licenses/>.
"""

from __future__ import annotations

from collections import deque
from typing import Dict, Iterable, List, Set, Tuple

from app.services.graphs.models import Edge, Graph


def sorted_vertices(graph: Graph) -> List[str]:
	"""Return graph vertices in deterministic lexicographic order.

	Stable ordering is used to guarantee reproducible algorithm results,
	matrix generation, and serialized outputs.

	Args:
		graph (Graph): Input graph instance.

	Returns:
		List[str]: Sorted list of vertex names.

	"""
	return sorted(graph.vertices)


def sorted_edges(graph: Graph) -> List[str]:
	"""Return graph edge names in deterministic lexicographic order.

	Stable ordering simplifies matrix construction and guarantees
	consistent algorithm output across executions.

	Args:
		graph (Graph): Input graph instance.

	Returns:
		List[str]: Sorted list of edge identifiers.

	"""
	return sorted(graph.edges)


def edge_signature(edge: Edge) -> Tuple[str, str]:
	"""Build an undirected canonical signature for an edge.

	The signature is independent of traversal direction and is mainly
	used to compare undirected edge equivalence.

	Args:
		edge (Edge): Graph edge instance.

	Returns:
		Tuple[str, str]: Ordered tuple containing edge endpoints.

	"""
	return tuple(sorted((edge.source, edge.target)))


def undirected_neighbors(
	graph: Graph, excluded_edges: Iterable[str] | None = None
) -> Dict[str, Set[str]]:
	"""Build undirected neighborhood sets for all vertices.

	Edges listed in ``excluded_edges`` are ignored during adjacency
	construction. Directed edges are treated as undirected connections.

	Args:
		graph (Graph): Input graph instance.
		excluded_edges (Iterable[str] | None): Optional iterable of edge
			names that must be excluded.

	Returns:
		Dict[str, Set[str]]: Neighbor map indexed by vertex name.

	"""
	excluded = set(excluded_edges or [])
	neighbors: Dict[str, Set[str]] = {name: set() for name in graph.vertices}
	for edge_name, edge in graph.edges.items():
		if edge_name in excluded:
			continue
		neighbors[edge.source].add(edge.target)
		neighbors[edge.target].add(edge.source)
	return neighbors


def connected_components(
	graph: Graph, excluded_edges: Iterable[str] | None = None
) -> List[Set[str]]:
	"""Compute connected components using breadth-first traversal.

	The graph is interpreted as undirected regardless of edge direction.
	Optionally, selected edges may be excluded from traversal.

	Args:
		graph (Graph): Input graph instance.
		excluded_edges (Iterable[str] | None): Optional iterable of edge
			names ignored during traversal.

	Returns:
		List[Set[str]]: List of connected vertex components.

	"""
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
	"""Determine whether the graph is connected.

	Connectivity is evaluated using an undirected interpretation of the
	graph. Selected edges may optionally be excluded.

	Args:
		graph (Graph): Input graph instance.
		excluded_edges (Iterable[str] | None): Optional iterable of edge
			names ignored during connectivity evaluation.

	Returns:
		bool: True if the graph is connected, otherwise False.

	"""
	if not graph.vertices:
		return True
	return len(connected_components(graph, excluded_edges)) == 1


def boundary_edges(graph: Graph, left_vertices: Set[str], right_vertices: Set[str]) -> List[str]:
	"""Return edges crossing a vertex partition boundary.

	An edge belongs to the boundary when its endpoints are distributed
	across opposite vertex subsets.

	Args:
		graph (Graph): Input graph instance.
		left_vertices (Set[str]): Left partition of vertices.
		right_vertices (Set[str]): Right partition of vertices.

	Returns:
		List[str]: Sorted list of edge names crossing the partition.

	"""
	boundary: List[str] = []
	for edge_name, edge in graph.edges.items():
		if {edge.source, edge.target}.issubset(left_vertices) or {
			edge.source,
			edge.target,
		}.issubset(right_vertices):
			continue
		boundary.append(edge_name)
	return sorted(boundary)
