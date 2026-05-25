"""Ordinal traversal and labeling algorithms.

Author: Juan Esteban Bedoya <jebedoyal@udistrital.edu.co>
"""

from __future__ import annotations

from collections import deque
from typing import Dict, List

from app.services.graphs.models import Graph
from app.services.graphs.validators import GraphValidationError


def ordinal_function(graph: Graph) -> Dict[str, object]:
	"""Assign ordinal labels using direction-aware topological traversal.

	The traversal starts from vertices without labeled predecessors and
	continues top-down and left-right using lexicographic ordering.

	Args:
		graph (Graph): Input graph.

	Returns:
		Dict[str, object]: Ordinal map and traversal order.

	Raises:
		GraphValidationError: If direction is missing or graph has cycles.

	"""
	if not graph.directed:
		raise GraphValidationError('Ordinal function requires directed graph')

	vertices = sorted(graph.vertices)
	in_degree = {name: 0 for name in vertices}
	adjacency: Dict[str, List[str]] = {name: [] for name in vertices}

	for edge in graph.edges.values():
		adjacency[edge.source].append(edge.target)
		in_degree[edge.target] += 1

	for name in adjacency:
		adjacency[name].sort()

	queue = deque(sorted([name for name, degree in in_degree.items() if degree == 0]))
	order: List[str] = []
	while queue:
		current = queue.popleft()
		order.append(current)
		for neighbor in adjacency[current]:
			in_degree[neighbor] -= 1
			if in_degree[neighbor] == 0:
				queue.append(neighbor)

	if len(order) != len(vertices):
		raise GraphValidationError('Ordinal function requires an acyclic directed graph')

	ordinal_map = {name: idx + 1 for idx, name in enumerate(order)}
	for vertex_name, ordinal in ordinal_map.items():
		graph.vertices[vertex_name].ordinal = ordinal

	return {'ordinal_map': ordinal_map, 'traversal_order': order}
