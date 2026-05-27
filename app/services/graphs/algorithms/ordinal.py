"""Ordinal traversal and labeling algorithms.

Provide algorithms for assigning ordinal labels to vertices in directed
acyclic graphs using a direction-aware topological traversal. The module
computes traversal order and assigns ordinal values to vertices following
lexicographic precedence.

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
from typing import Dict, List

from app.services.graphs.models import Graph
from app.services.graphs.validators import GraphValidationError


def ordinal_function(graph: Graph) -> Dict[str, object]:
	"""Assign ordinal labels using topological traversal.

	The algorithm performs a direction-aware topological traversal over
	a directed acyclic graph (DAG). Traversal starts from vertices with
	no incoming edges and continues following edge directions using
	lexicographic ordering to ensure deterministic results.

	Each visited vertex receives an ordinal label starting at 1
	according to traversal order.

	Args:
		graph (Graph): Directed graph to process.

	Returns:
		Dict[str, object]:
			Dictionary containing:
				- ordinal_map:
					Mapping between vertex names and assigned ordinals.
				- traversal_order:
					List representing the topological traversal order.

	Raises:
		GraphValidationError:
			If the graph is not directed or contains cycles.

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
