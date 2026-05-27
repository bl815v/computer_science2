"""Vertex and edge coloring algorithms.

Implement greedy graph coloring algorithms for both
vertices and edges. Provide utilities for computing
chromatic classes, chromatic numbers, chromatic indices,
and polynomial evaluations for small graph instances.

The module includes:

	- Vertex neighborhood construction.
	- Greedy vertex coloring.
	- Greedy edge coloring.
	- Chromatic class generation.
	- Exact k-coloring counting using backtracking
	  for small graphs.

Functions:
	_vertex_neighbors:
		Build the undirected neighborhood map for vertices.

	vertex_coloring:
		Compute a greedy vertex coloring and chromatic classes.

	_count_colorings:
		Count valid k-colorings using recursive backtracking.

	edge_coloring:
		Compute a greedy edge coloring and edge-color classes.

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

from collections import defaultdict
from typing import Dict, List, Set

from app.services.graphs.models import ColoringResult, Graph


def _vertex_neighbors(graph: Graph) -> Dict[str, Set[str]]:
	"""Build an undirected neighborhood map for graph vertices.

	Create a dictionary where each vertex is associated
	with the set of adjacent vertices connected through
	graph edges.

	The neighborhood representation is used by coloring
	algorithms to determine adjacency constraints.

	Args:
		graph (Graph):
			Graph instance containing vertices and edges.

	Returns:
		Dict[str, Set[str]]:
			Dictionary mapping each vertex to its
			set of neighboring vertices.

	"""
	neighbors: Dict[str, Set[str]] = {name: set() for name in graph.vertices}
	for edge in graph.edges.values():
		neighbors[edge.source].add(edge.target)
		neighbors[edge.target].add(edge.source)
	return neighbors


def vertex_coloring(graph: Graph) -> ColoringResult:
	"""Compute a greedy vertex coloring of the graph.

	Apply a greedy coloring strategy by processing
	vertices in descending order of degree. Each vertex
	receives the smallest available color not already
	used by its neighbors.

	The algorithm also computes:

		- Chromatic classes.
		- Chromatic number.
		- Chromatic polynomial evaluations for small k.

	Args:
		graph (Graph):
			Graph instance to color.

	Returns:
		ColoringResult:
			Object containing:

				- chromatic_number:
				  Number of colors used.

				- chromatic_polynomial:
				  Evaluated chromatic polynomial values.

				- classes:
				  Mapping of color classes to vertices.

	"""
	neighbors = _vertex_neighbors(graph)
	assignment: Dict[str, int] = {}

	for vertex in sorted(graph.vertices, key=lambda x: (-len(neighbors[x]), x)):
		used = {assignment[n] for n in neighbors[vertex] if n in assignment}
		color = 1
		while color in used:
			color += 1
		assignment[vertex] = color

	classes_map: Dict[str, List[str]] = defaultdict(list)
	for vertex, color in sorted(assignment.items(), key=lambda item: (item[1], item[0])):
		classes_map[f'color{color}'].append(vertex)

	order = len(graph.vertices)
	evaluations = []
	for k in range(1, max(2, order + 1)):
		count = _count_colorings(graph, k)
		evaluations.append(f'P({k})={count}')

	return ColoringResult(
		chromatic_number=max(assignment.values(), default=0),
		chromatic_polynomial='; '.join(evaluations),
		classes=dict(classes_map),
	)


def _count_colorings(graph: Graph, k: int) -> int:
	"""Count valid k-colorings using recursive backtracking.

	Explore all possible color assignments and count
	only those that satisfy the graph coloring constraint:
	adjacent vertices cannot share the same color.

	To avoid excessive computational cost, the algorithm
	is only executed for graphs with at most 10 vertices.

	Args:
		graph (Graph):
			Graph instance to analyze.

		k (int):
			Number of available colors.

	Returns:
		int:
			Total number of valid k-colorings.

			Returns 0 for graphs with more than
			10 vertices.

	"""
	vertices = sorted(graph.vertices)
	neighbors = _vertex_neighbors(graph)
	assignment: Dict[str, int] = {}
	count = 0

	def backtrack(index: int) -> None:
		"""Perform recursive coloring assignment.

		Args:
			index (int):
				Current vertex position in the traversal.

		"""
		nonlocal count
		if index == len(vertices):
			count += 1
			return
		vertex = vertices[index]
		for color in range(1, k + 1):
			if any(assignment.get(nei) == color for nei in neighbors[vertex]):
				continue
			assignment[vertex] = color
			backtrack(index + 1)
			del assignment[vertex]

	if len(vertices) > 10:
		return 0
	backtrack(0)
	return count


def edge_coloring(graph: Graph) -> ColoringResult:
	"""Compute a greedy edge coloring of the graph.

	Apply a greedy coloring strategy over graph edges.
	Two edges are considered adjacent if they share
	at least one endpoint vertex.

	The algorithm computes:

		- Edge chromatic classes.
		- Chromatic index.

	Args:
		graph (Graph):
			Graph instance to color.

	Returns:
		ColoringResult:
			Object containing:

				- chromatic_index:
				  Number of edge colors used.

				- edge_classes:
				  Mapping of edge-color classes.

	"""
	edge_names = sorted(graph.edges)
	adjacent_edges: Dict[str, Set[str]] = {name: set() for name in edge_names}

	for i, edge_name_left in enumerate(edge_names):
		left = graph.edges[edge_name_left]
		left_vertices = {left.source, left.target}
		for edge_name_right in edge_names[i + 1 :]:
			right = graph.edges[edge_name_right]
			right_vertices = {right.source, right.target}
			if left_vertices.intersection(right_vertices):
				adjacent_edges[edge_name_left].add(edge_name_right)
				adjacent_edges[edge_name_right].add(edge_name_left)

	assignment: Dict[str, int] = {}
	for edge_name in sorted(edge_names, key=lambda x: (-len(adjacent_edges[x]), x)):
		used = {assignment[name] for name in adjacent_edges[edge_name] if name in assignment}
		color = 1
		while color in used:
			color += 1
		assignment[edge_name] = color

	edge_classes: Dict[str, List[str]] = defaultdict(list)
	for edge_name, color in sorted(assignment.items(), key=lambda item: (item[1], item[0])):
		edge_classes[f'color{color}'].append(edge_name)

	return ColoringResult(
		chromatic_index=max(assignment.values(), default=0),
		edge_classes=dict(edge_classes),
	)
