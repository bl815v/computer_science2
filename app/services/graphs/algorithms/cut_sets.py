"""Cut-set algorithms for graphs.

Provide algorithms to compute minimal cut sets and fundamental
cut sets of a graph. Generate the corresponding incidence
matrices used in graph-theory analysis and spanning-tree studies.

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

from itertools import combinations
from typing import Dict, List

from app.services.graphs.algorithms.shared import boundary_edges, connected_components, sorted_edges
from app.services.graphs.models import Graph


def cut_sets(graph: Graph) -> Dict[str, object]:
	"""Compute minimal edge cut sets and their incidence matrix.

	A cut set is a group of edges whose removal increases the number
	of connected components in the graph. This function searches for
	all minimal disconnecting edge sets by evaluating edge subsets
	in increasing order of size.

	For each valid cut set, generate a binary incidence matrix where:
		- 1 indicates that an edge belongs to the cut set.
		- 0 indicates that an edge does not belong to the cut set.

	Args:
		graph: Graph to analyze.

	Returns:
		Dict[str, object]: Dictionary containing:
			- ``cut_sets``:
				List of minimal cut sets.
			- ``cut_matrix``:
				Binary incidence matrix of cut sets.
			- ``edge_labels``:
				Ordered list of graph edge names.
			- ``disconnecting_sets``:
				Alias of the minimal cut sets.

	"""
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

	cut_matrix = [
		[1 if edge in cut_set else 0 for edge in edge_labels] for cut_set in minimal_cut_sets
	]
	return {
		'cut_sets': minimal_cut_sets,
		'cut_matrix': cut_matrix,
		'edge_labels': edge_labels,
		'disconnecting_sets': minimal_cut_sets,
	}


def fundamental_cut_sets(graph: Graph, branches: List[str]) -> Dict[str, object]:
	"""Compute fundamental cut sets from a spanning tree.

	Generate the fundamental cut set associated with each branch
	of a spanning tree. Removing a branch divides the tree into
	two connected components, and the corresponding fundamental
	cut set contains all graph edges connecting those components.

	For every branch:
		1. Remove the branch from the spanning tree.
		2. Compute the resulting connected components.
		3. Find all boundary edges crossing between components.
		4. Build the corresponding cut set and matrix row.

	The resulting incidence matrix represents which edges belong
	to each fundamental cut set.

	Args:
		graph: Original graph containing the spanning tree.
		branches: List of edge names belonging to the spanning tree.

	Returns:
		Dict[str, object]: Dictionary containing:
			- ``cut_sets``:
				List of fundamental cut sets.
			- ``cut_matrix``:
				Binary incidence matrix of fundamental cut sets.
			- ``edge_labels``:
				Ordered list of graph edge names.
			- ``branches``:
				Branch associated with each cut set.
			- ``chords``:
				Chord edges associated with each cut set.

	"""
	edge_labels = sorted_edges(graph)
	fundamental_sets: List[List[str]] = []
	branch_groups: List[List[str]] = []
	chord_groups: List[List[str]] = []

	for branch_name in branches:
		branch_edge = graph.edges[branch_name]
		tree_graph = Graph(
			graph_id=f'{graph.graph_id}_tree', directed=False, weighted=graph.weighted
		)
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

	cut_matrix = [
		[1 if edge in cut_set else 0 for edge in edge_labels] for cut_set in fundamental_sets
	]
	return {
		'cut_sets': fundamental_sets,
		'cut_matrix': cut_matrix,
		'edge_labels': edge_labels,
		'branches': branch_groups,
		'chords': chord_groups,
	}
