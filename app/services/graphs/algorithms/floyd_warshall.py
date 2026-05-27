"""Floyd-Warshall shortest-path algorithm.

Provide an implementation of the Floyd-Warshall algorithm to compute
all-pairs shortest paths in weighted graphs. Generate the distance
matrix, predecessor matrix, reconstructed shortest paths, and detect
negative cycles.

Author: Juan Esteban Bedoya <jebedoyal@udistrital.edu.co>

This file is part of ComputerScience2 project.

ComputerScience2 is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version.

ComputerScience2 is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with ComputerScience2. If not, see <https://www.gnu.org/licenses/>.
"""

from __future__ import annotations

from math import inf
from typing import Dict, List, Optional

from app.services.graphs.algorithms.shared import sorted_vertices
from app.services.graphs.models import FloydWarshallResult, Graph
from app.services.graphs.validators import GraphValidationError


def _reconstruct_path(
	predecessors: List[List[Optional[str]]],
	vertex_labels: List[str],
	vertex_index: Dict[str, int],
	source_index: int,
	target_index: int,
) -> List[str]:
	"""Reconstruct a shortest path from a predecessor matrix.

	Traverse the predecessor matrix backwards starting from the
	target vertex until the source vertex is reached.

	If no valid predecessor chain exists, return an empty path.

	Args:
		predecessors:
			Matrix storing predecessor vertices for shortest paths.
		vertex_labels:
			Ordered list of graph vertex names.
		vertex_index:
			Mapping between vertex names and matrix indices.
		source_index:
			Index of the source vertex.
		target_index:
			Index of the target vertex.

	Returns:
		List[str]: Ordered sequence of vertices representing the
		shortest path. Returns an empty list if no valid path exists.

	"""
	if source_index == target_index:
		return [vertex_labels[source_index]]

	current = vertex_labels[target_index]
	path = [current]
	visited = {current}

	while current != vertex_labels[source_index]:
		predecessor = predecessors[source_index][vertex_index[current]]
		if predecessor is None or predecessor in visited:
			return []
		path.append(predecessor)
		visited.add(predecessor)
		current = predecessor

	path.reverse()
	return path


def floyd_warshall(graph: Graph) -> FloydWarshallResult:
	"""Compute all-pairs shortest paths using Floyd-Warshall.

	Apply dynamic programming to compute the minimum path cost
	between every pair of vertices in a weighted graph.

	The algorithm progressively improves shortest-path estimates
	by allowing intermediate vertices in the paths.

	Generate:
		- Distance matrix.
		- Predecessor matrix.
		- Reconstructed shortest paths.
		- Negative-cycle detection result.

	Args:
		graph: Weighted graph to analyze.

	Returns:
		FloydWarshallResult: Object containing:
			- ``distance_matrix``:
				Matrix of minimum distances between vertices.
			- ``predecessor_matrix``:
				Matrix storing predecessor relationships.
			- ``shortest_paths``:
				Dictionary containing reconstructed shortest paths.
			- ``negative_cycle_detected``:
				Whether a negative cycle exists in the graph.
			- ``vertex_labels``:
				Ordered list of graph vertices.

	Raises:
		GraphValidationError:
			If the graph is not weighted or contains edges
			without weights.

	"""
	if not graph.weighted:
		raise GraphValidationError('Floyd-Warshall requires a weighted graph')

	vertex_labels = sorted_vertices(graph)
	vertex_index = {name: index for index, name in enumerate(vertex_labels)}
	size = len(vertex_labels)
	distance_matrix = [[inf for _ in range(size)] for _ in range(size)]
	predecessor_matrix: List[List[Optional[str]]] = [
		[None for _ in range(size)] for _ in range(size)
	]

	for index, vertex in enumerate(vertex_labels):
		distance_matrix[index][index] = 0.0
		predecessor_matrix[index][index] = vertex

	for edge in graph.edges.values():
		if edge.weight is None:
			raise GraphValidationError('Floyd-Warshall requires weighted edges')
		left_index = vertex_index[edge.source]
		right_index = vertex_index[edge.target]
		weight = float(edge.weight)
		if weight < distance_matrix[left_index][right_index]:
			distance_matrix[left_index][right_index] = weight
			predecessor_matrix[left_index][right_index] = edge.source
		if not edge.directed and weight < distance_matrix[right_index][left_index]:
			distance_matrix[right_index][left_index] = weight
			predecessor_matrix[right_index][left_index] = edge.target

	for middle in range(size):
		for left in range(size):
			if distance_matrix[left][middle] == inf:
				continue
			for right in range(size):
				if distance_matrix[middle][right] == inf:
					continue
				candidate = distance_matrix[left][middle] + distance_matrix[middle][right]
				if candidate < distance_matrix[left][right]:
					distance_matrix[left][right] = candidate
					predecessor_matrix[left][right] = predecessor_matrix[middle][right]

	negative_cycle_detected = any(distance_matrix[index][index] < 0 for index in range(size))
	shortest_paths: Dict[str, Dict[str, List[str]]] = {name: {} for name in vertex_labels}
	for left_index, source in enumerate(vertex_labels):
		for right_index, target in enumerate(vertex_labels):
			if distance_matrix[left_index][right_index] == inf:
				shortest_paths[source][target] = []
				continue
			shortest_paths[source][target] = _reconstruct_path(
				predecessor_matrix,
				vertex_labels,
				vertex_index,
				left_index,
				right_index,
			)

	return FloydWarshallResult(
		distance_matrix=distance_matrix,
		predecessor_matrix=predecessor_matrix,
		shortest_paths=shortest_paths,
		negative_cycle_detected=negative_cycle_detected,
		vertex_labels=vertex_labels,
	)
