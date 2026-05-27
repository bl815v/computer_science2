"""Path algorithms for directed and undirected graphs.

Provide shortest-path, traversal, and tree-distance algorithms used by
the graph service layer. Includes Dijkstra, Bellman lambda evaluation,
tree-distance comparison, and generic path reconstruction helpers.

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

import heapq
from typing import Dict, List, Optional, Tuple

from app.services.graphs.models import BellmanResult, DijkstraResult, Graph, PathResult
from app.services.graphs.validators import GraphValidationError


def _adjacency(graph: Graph) -> Dict[str, List[Tuple[str, float, str]]]:
	"""Build adjacency representation for graph traversal.

	The adjacency list stores neighbor information as tuples containing
	target vertex name, effective edge weight, and edge identifier.
	Undirected edges are inserted in both directions.

	Args:
		graph (Graph): Input graph instance.

	Returns:
		Dict[str, List[Tuple[str, float, str]]]: Adjacency list indexed
			by vertex name.

	"""
	adj = {name: [] for name in graph.vertices}
	for edge in graph.edges.values():
		weight = float(edge.weight if edge.weight is not None else 1.0)
		adj[edge.source].append((edge.target, weight, edge.name))
		if not edge.directed:
			adj[edge.target].append((edge.source, weight, edge.name))
	return adj


def _restore_path(predecessor: Dict[str, Optional[str]], source: str, target: str) -> List[str]:
	"""Restore a shortest path from predecessor relationships.

	The reconstruction starts from the target vertex and walks backwards
	through the predecessor map until the source vertex is reached.

	Args:
		predecessor (Dict[str, Optional[str]]): Predecessor map generated
			by a shortest-path algorithm.
		source (str): Source vertex name.
		target (str): Target vertex name.

	Returns:
		List[str]: Ordered list of vertices representing the path from
			source to target. Returns an empty list if no valid path exists.

	"""
	if target not in predecessor:
		return []
	path = []
	cursor: Optional[str] = target
	while cursor is not None:
		path.append(cursor)
		cursor = predecessor.get(cursor)
	path.reverse()
	if path and path[0] == source:
		return path
	return []


def bellman_lambda(
	graph: Graph,
	source: str,
	ordinal_order: List[str],
	target: Optional[str] = None,
) -> BellmanResult:
	"""Compute Bellman lambda values using ordinal traversal order.

	The algorithm evaluates vertices following a previously computed
	topological or ordinal ordering. For each vertex, the minimum lambda
	value is selected from all valid predecessor candidates.

	Args:
		graph (Graph): Input graph.
		source (str): Starting vertex name.
		ordinal_order (List[str]): Vertex evaluation order.
		target (Optional[str]): Optional target vertex for path recovery.

	Returns:
		BellmanResult: Lambda values, predecessor information,
			intermediate evaluation expressions, and optional path.

	Raises:
		GraphValidationError: If the source vertex does not exist.

	"""
	if source not in graph.vertices:
		raise GraphValidationError(f"Source vertex '{source}' does not exist")

	adj = _adjacency(graph)
	predecessor: Dict[str, Optional[str]] = {name: None for name in graph.vertices}
	lambda_values = {name: float('inf') for name in graph.vertices}
	lambda_values[source] = 0.0
	steps: List[str] = []

	for vertex in ordinal_order:
		if vertex == source:
			continue
		candidates: List[Tuple[float, str, float]] = []
		for edge in graph.edges.values():
			if edge.target != vertex:
				continue
			parent = edge.source
			parent_lambda = lambda_values.get(parent, float('inf'))
			weight = float(edge.weight if edge.weight is not None else 1.0)
			if parent_lambda == float('inf'):
				continue
			candidates.append((parent_lambda + weight, parent, weight))

		if not candidates:
			continue

		best = min(candidates, key=lambda item: item[0])
		lambda_values[vertex] = best[0]
		predecessor[vertex] = best[1]
		expression_parts = [f'({lambda_values[p]}+{w})' for _, p, w in candidates]
		steps.append(f'lambda_{vertex} = min[{",".join(expression_parts)}] = {best[0]}')

	path: List[str] = []
	if target is not None:
		path = _restore_path(predecessor, source, target)

	return BellmanResult(
		source=source,
		target=target,
		lambda_values=lambda_values,
		intermediate_steps=steps,
		path=path,
	)


def dijkstra(
	graph: Graph,
	source: str,
	target: Optional[str] = None,
) -> DijkstraResult:
	"""Compute shortest paths using Dijkstra algorithm.

	The algorithm uses a priority queue to iteratively select the vertex
	with minimum tentative distance and relax adjacent edges.

	Args:
		graph (Graph): Input graph.
		source (str): Starting vertex name.
		target (Optional[str]): Optional destination vertex.

	Returns:
		DijkstraResult: Distances, traversal information, predecessor
			relationships, and optional reconstructed path.

	Raises:
		GraphValidationError: If the source vertex does not exist.

	"""
	if source not in graph.vertices:
		raise GraphValidationError(f"Source vertex '{source}' does not exist")

	adj = _adjacency(graph)
	distances = {name: float('inf') for name in graph.vertices}
	predecessor: Dict[str, Optional[str]] = {name: None for name in graph.vertices}
	distances[source] = 0.0
	visited: set[str] = set()
	pairs: List[List[object]] = []
	definitive_order: List[str] = []

	heap: List[Tuple[float, str]] = [(0.0, source)]
	while heap:
		current_distance, current = heapq.heappop(heap)
		if current in visited:
			continue
		visited.add(current)
		definitive_order.append(current)

		for neighbor, weight, edge_name in adj[current]:
			candidate = current_distance + weight
			pairs.append([current, neighbor, candidate, edge_name])
			if candidate < distances[neighbor]:
				distances[neighbor] = candidate
				predecessor[neighbor] = current
				heapq.heappush(heap, (candidate, neighbor))

	path: List[str] = []
	if target is not None:
		path = _restore_path(predecessor, source, target)

	return DijkstraResult(
		source=source,
		target=target,
		pairs=pairs,
		definitive_order=definitive_order,
		distances=distances,
		path=path,
	)


def tree_distance(graph_a: Graph, graph_b: Graph) -> Dict[str, object]:
	"""Compute weighted distance between two trees.

	The distance is defined as:

		union(weights) - intersection(weights)

	Edges are compared using undirected endpoint signatures.

	Args:
		graph_a (Graph): First tree graph.
		graph_b (Graph): Second tree graph.

	Returns:
		Dict[str, object]: Union/intersection edge information,
			accumulated weights, and computed distance.

	Raises:
		GraphValidationError: If a required edge weight is missing.

	"""

	def signature(edge_name: str, graph: Graph) -> tuple[str, str]:
		"""Build undirected edge signature."""
		edge = graph.edges[edge_name]
		ordered = tuple(sorted((edge.source, edge.target)))
		return ordered[0], ordered[1]

	edges_a = {signature(name, graph_a): name for name in graph_a.edges}
	edges_b = {signature(name, graph_b): name for name in graph_b.edges}

	union_keys = set(edges_a).union(edges_b)
	inter_keys = set(edges_a).intersection(edges_b)

	def edge_weight(graph: Graph, edge_name: str) -> float:
		"""Return validated edge weight."""
		edge = graph.edges[edge_name]
		if edge.weight is None:
			raise GraphValidationError('Tree distance requires weighted edges')
		return float(edge.weight)

	union_sum = 0.0
	union_edges: List[str] = []
	for key in sorted(union_keys):
		if key in edges_a:
			name = edges_a[key]
			union_sum += edge_weight(graph_a, name)
			union_edges.append(name)
		else:
			name = edges_b[key]
			union_sum += edge_weight(graph_b, name)
			union_edges.append(name)

	inter_sum = 0.0
	intersection_edges: List[str] = []
	for key in sorted(inter_keys):
		name = edges_a[key]
		inter_sum += edge_weight(graph_a, name)
		intersection_edges.append(name)

	return {
		'union_edges': union_edges,
		'intersection_edges': intersection_edges,
		'union_weight_sum': union_sum,
		'intersection_weight_sum': inter_sum,
		'distance': union_sum - inter_sum,
		'operations': ['union', 'intersection', 'sum', 'subtraction'],
	}


def shortest_path_result(
	graph: Graph,
	source: str,
	target: Optional[str] = None,
) -> PathResult:
	"""Build a generic shortest-path response using Dijkstra.

	This compatibility helper converts a DijkstraResult instance into a
	generic PathResult structure expected by other service layers.

	Args:
		graph (Graph): Input graph.
		source (str): Starting vertex name.
		target (Optional[str]): Optional destination vertex.

	Returns:
		PathResult: Generic shortest-path representation.

	"""
	result = dijkstra(graph, source, target)
	return PathResult(
		source=source,
		target=target,
		distances=result.distances,
		path=result.path,
		steps=[
			{
				'pair': pair,
				'definitive_order': result.definitive_order,
			}
			for pair in result.pairs
		],
	)
