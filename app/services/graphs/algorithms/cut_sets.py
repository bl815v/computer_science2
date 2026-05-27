"""Cut-set algorithms for graphs.

Author: Juan Esteban Bedoya <jebedoyal@udistrital.edu.co>
"""

from __future__ import annotations

from itertools import combinations
from typing import Dict, List

from app.services.graphs.algorithms.shared import boundary_edges, connected_components, sorted_edges
from app.services.graphs.models import Graph


def cut_sets(graph: Graph) -> Dict[str, object]:
	"""Compute minimal edge cut sets and their incidence matrix."""
	edge_labels = sorted_edges(graph)
	base_components = len(connected_components(graph))
	minimal_cut_sets: List[List[str]] = []

	for size in range(1, len(edge_labels) + 1):
		for subset in combinations(edge_labels, size):
			subset_set = set(subset)
			if any(set(existing).issubset(subset_set) for existing in minimal_cut_sets):
				continue
			if len(connected_components(graph, subset)) > base_components:
				minimal_cut_sets.append(list(subset))

	cut_matrix = [[1 if edge in cut_set else 0 for edge in edge_labels] for cut_set in minimal_cut_sets]
	return {
		'cut_sets': minimal_cut_sets,
		'cut_matrix': cut_matrix,
		'edge_labels': edge_labels,
		'disconnecting_sets': minimal_cut_sets,
	}


def fundamental_cut_sets(graph: Graph, branches: List[str]) -> Dict[str, object]:
	"""Compute fundamental cut sets from a spanning tree."""
	edge_labels = sorted_edges(graph)
	fundamental_sets: List[List[str]] = []
	branch_groups: List[List[str]] = []
	chord_groups: List[List[str]] = []

	for branch_name in branches:
		branch_edge = graph.edges[branch_name]
		tree_graph = Graph(graph_id=f'{graph.graph_id}_tree', directed=False, weighted=graph.weighted)
		for vertex_name in graph.vertices:
			tree_graph.vertices[vertex_name] = graph.vertices[vertex_name]
		for tree_branch in branches:
			if tree_branch == branch_name:
				continue
			tree_graph.edges[tree_branch] = graph.edges[tree_branch]
		components = connected_components(tree_graph)
		if len(components) < 2:
			continue
		left_vertices = set(next(iter(components)))
		right_vertices = set(graph.vertices) - left_vertices
		cut_edges = boundary_edges(graph, left_vertices, right_vertices)
		if branch_name not in cut_edges:
			cut_edges = sorted(set(cut_edges + [branch_name]))
		fundamental_sets.append(cut_edges)
		branch_groups.append([branch_name])
		chord_groups.append([edge_name for edge_name in cut_edges if edge_name != branch_name])

	cut_matrix = [[1 if edge in cut_set else 0 for edge in edge_labels] for cut_set in fundamental_sets]
	return {
		'cut_sets': fundamental_sets,
		'cut_matrix': cut_matrix,
		'edge_labels': edge_labels,
		'branches': branch_groups,
		'chords': chord_groups,
	}
