"""Vertex and edge coloring algorithms.

Author: Juan Esteban Bedoya <jebedoyal@udistrital.edu.co>
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Set

from app.services.graphs.models import ColoringResult, Graph


def _vertex_neighbors(graph: Graph) -> Dict[str, Set[str]]:
	"""Build undirected vertex neighborhood map."""
	neighbors: Dict[str, Set[str]] = {name: set() for name in graph.vertices}
	for edge in graph.edges.values():
		neighbors[edge.source].add(edge.target)
		neighbors[edge.target].add(edge.source)
	return neighbors


def vertex_coloring(graph: Graph) -> ColoringResult:
	"""Compute greedy vertex coloring and classes."""
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
	"""Count valid k-colorings with backtracking for small instances."""
	vertices = sorted(graph.vertices)
	neighbors = _vertex_neighbors(graph)
	assignment: Dict[str, int] = {}
	count = 0

	def backtrack(index: int) -> None:
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
	"""Compute greedy edge coloring and classes."""
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
