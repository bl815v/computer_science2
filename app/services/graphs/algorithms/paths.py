"""Path algorithms for directed and undirected graphs.

Author: Juan Esteban Bedoya <jebedoyal@udistrital.edu.co>
"""

from __future__ import annotations

import heapq
from typing import Dict, List, Optional, Tuple

from app.services.graphs.models import BellmanResult, DijkstraResult, Graph, PathResult
from app.services.graphs.validators import GraphValidationError


def _adjacency(graph: Graph) -> Dict[str, List[Tuple[str, float, str]]]:
	"""Build adjacency list including edge names and effective weights."""
	adj = {name: [] for name in graph.vertices}
	for edge in graph.edges.values():
		weight = float(edge.weight if edge.weight is not None else 1.0)
		adj[edge.source].append((edge.target, weight, edge.name))
		if not edge.directed:
			adj[edge.target].append((edge.source, weight, edge.name))
	return adj


def _restore_path(predecessor: Dict[str, Optional[str]], source: str, target: str) -> List[str]:
	"""Restore source-target path from predecessor map."""
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
	"""Compute Bellman lambda values over ordinal traversal order."""
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
		steps.append(
			f"lambda_{vertex} = min[{','.join(expression_parts)}] = {best[0]}"
		)

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
	"""Run Dijkstra shortest-path algorithm."""
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
	"""Compute weighted tree distance between two trees.

	Distance = sum(weights(union)) - sum(weights(intersection)).
	"""
	def signature(edge_name: str, graph: Graph) -> tuple[str, str]:
		edge = graph.edges[edge_name]
		ordered = tuple(sorted((edge.source, edge.target)))
		return ordered[0], ordered[1]

	edges_a = {signature(name, graph_a): name for name in graph_a.edges}
	edges_b = {signature(name, graph_b): name for name in graph_b.edges}

	union_keys = set(edges_a).union(edges_b)
	inter_keys = set(edges_a).intersection(edges_b)

	def edge_weight(graph: Graph, edge_name: str) -> float:
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
	"""Compatibility helper returning generic path result via Dijkstra."""
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
