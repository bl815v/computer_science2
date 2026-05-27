"""Tree-center and minimum spanning tree algorithms.

Provide utilities for tree validation, center and bicenter detection,
and spanning-tree computation using Kruskal's algorithm. The module
supports both minimum and maximum spanning trees for connected,
weighted, undirected graphs.

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
from typing import Dict, List, Tuple

from app.services.graphs.models import Graph, MSTResult
from app.services.graphs.validators import GraphValidationError


class _DisjointSet:
	"""Implement a disjoint-set structure for Kruskal algorithm.

	Manage connected components efficiently using path compression
	and union-by-rank heuristics.

	Attributes:
		parent (Dict[str, str]): Representative parent for each element.
		rank (Dict[str, int]): Rank heuristic used to balance unions.

	"""

	def __init__(self, elements: List[str]) -> None:
		"""Initialize singleton sets for all elements.

		Args:
			elements: Collection of vertex identifiers.

		"""
		self.parent = {element: element for element in elements}
		self.rank = {element: 0 for element in elements}

	def find(self, value: str) -> str:
		"""Find the representative of a set using path compression.

		Args:
			value: Element whose representative will be located.

		Returns:
			str: Representative element of the corresponding set.

		"""
		if self.parent[value] != value:
			self.parent[value] = self.find(self.parent[value])
		return self.parent[value]

	def union(self, left: str, right: str) -> bool:
		"""Merge two sets using union by rank.

		Args:
			left: First element.
			right: Second element.

		Returns:
			bool: True if the sets were merged successfully,
			False if both elements already belong to the same set.

		"""
		root_left = self.find(left)
		root_right = self.find(right)
		if root_left == root_right:
			return False
		if self.rank[root_left] < self.rank[root_right]:
			self.parent[root_left] = root_right
		elif self.rank[root_left] > self.rank[root_right]:
			self.parent[root_right] = root_left
		else:
			self.parent[root_right] = root_left
			self.rank[root_left] += 1
		return True


def _undirected_neighbors(graph: Graph) -> Dict[str, List[str]]:
	"""Build an undirected adjacency representation of a graph.

	Ignore edge orientation and create a neighborhood list for
	each vertex.

	Args:
		graph: Graph whose adjacency structure will be generated.

	Returns:
		Dict[str, List[str]]: Mapping from vertex names to lists
		of adjacent vertices.

	"""
	adjacency = {name: [] for name in graph.vertices}
	for edge in graph.edges.values():
		adjacency[edge.source].append(edge.target)
		adjacency[edge.target].append(edge.source)
	return adjacency


def _is_connected(graph: Graph) -> bool:
	"""Check whether a graph is connected using BFS traversal.

	Connectivity is evaluated under an undirected interpretation.

	Args:
		graph: Graph to validate.

	Returns:
		bool: True if all vertices are reachable from any starting
		vertex, otherwise False.

	"""
	if not graph.vertices:
		return True
	adjacency = _undirected_neighbors(graph)
	start = next(iter(graph.vertices))
	seen = {start}
	queue = deque([start])
	while queue:
		current = queue.popleft()
		for neighbor in adjacency[current]:
			if neighbor not in seen:
				seen.add(neighbor)
				queue.append(neighbor)
	return len(seen) == len(graph.vertices)


def validate_tree(graph: Graph) -> None:
	"""Validate that a graph satisfies tree properties.

	A valid tree must be connected and contain exactly
	|V| - 1 edges.

	Args:
		graph: Graph to validate.

	Raises:
		GraphValidationError: If the graph is disconnected or
			does not satisfy the edge-count property of trees.

	"""
	if not _is_connected(graph):
		raise GraphValidationError('Graph must be connected to be a tree')
	if len(graph.edges) != max(0, len(graph.vertices) - 1):
		raise GraphValidationError('Graph is not a tree: invalid edge count')


def center_or_bicenter(graph: Graph) -> Dict[str, object]:
	"""Compute the center or bicenter of a tree.

	Repeatedly remove leaves from the tree until one or two
	central vertices remain.

	Args:
		graph: Tree whose center structure will be computed.

	Returns:
		Dict[str, object]: Dictionary containing the central
		vertices and the detected type ("center" or "bicenter").

	Raises:
		GraphValidationError: If the graph is not a valid tree.

	"""
	validate_tree(graph)
	adjacency = _undirected_neighbors(graph)
	remaining = set(graph.vertices)
	leaves = [name for name in remaining if len(adjacency[name]) <= 1]

	while len(remaining) > 2:
		next_leaves: List[str] = []
		for leaf in leaves:
			remaining.remove(leaf)
			for neighbor in adjacency[leaf]:
				adjacency[neighbor] = [item for item in adjacency[neighbor] if item != leaf]
				if len(adjacency[neighbor]) == 1:
					next_leaves.append(neighbor)
		leaves = next_leaves

	centers = sorted(remaining)
	return {
		'centers': centers,
		'type': 'center' if len(centers) == 1 else 'bicenter',
	}


def _spanning_tree(graph: Graph, maximize: bool = False) -> MSTResult:
	"""Compute a spanning tree using Kruskal algorithm.

	Generate either a minimum or maximum spanning tree depending
	on the maximize flag.

	Args:
		graph: Weighted undirected graph to process.
		maximize: If True, compute a maximum spanning tree.
			Otherwise compute a minimum spanning tree.

	Returns:
		MSTResult: Object containing spanning-tree edges,
		complement edges, rank, nullity, and total weight.

	Raises:
		GraphValidationError: If the graph is directed,
			disconnected, or contains unweighted edges.

	"""
	if graph.directed:
		operation_name = 'maximum spanning tree' if maximize else 'MST'
		raise GraphValidationError(f'{operation_name} requires an undirected graph')
	if not _is_connected(graph):
		operation_name = 'maximum spanning tree' if maximize else 'MST'
		raise GraphValidationError(f'{operation_name} requires a connected graph')

	weighted_edges: List[Tuple[float, str, str, str]] = []
	for edge in graph.edges.values():
		if edge.weight is None:
			operation_name = 'maximum spanning tree' if maximize else 'MST'
			raise GraphValidationError(f'{operation_name} requires weighted edges')
		weighted_edges.append((float(edge.weight), edge.name, edge.source, edge.target))

	weighted_edges.sort(key=lambda item: (-item[0], item[1]) if maximize else (item[0], item[1]))
	dsu = _DisjointSet(list(graph.vertices))
	mst_edge_names: List[str] = []
	total_weight = 0.0

	for weight, edge_name, source, target in weighted_edges:
		if dsu.union(source, target):
			mst_edge_names.append(edge_name)
			total_weight += weight

	if len(mst_edge_names) != len(graph.vertices) - 1:
		raise GraphValidationError('Invalid MST result: tree does not span all vertices')

	branches = sorted(mst_edge_names)
	chords = sorted([name for name in graph.edges if name not in mst_edge_names])
	rank = len(graph.vertices) - 1
	nullity = len(graph.edges) - rank

	return MSTResult(
		edges=sorted(mst_edge_names),
		complement_edges=chords,
		branches=branches,
		chords=chords,
		rank=rank,
		nullity=nullity,
		total_weight=total_weight,
	)


def minimum_spanning_tree(graph: Graph) -> MSTResult:
	"""Compute a minimum spanning tree using Kruskal algorithm.

	Args:
		graph: Weighted undirected graph to process.

	Returns:
		MSTResult: Result object describing the minimum
		spanning tree.

	"""
	return _spanning_tree(graph, maximize=False)


def maximum_spanning_tree(graph: Graph) -> MSTResult:
	"""Compute a maximum spanning tree using Kruskal algorithm.

	Args:
		graph: Weighted undirected graph to process.

	Returns:
		MSTResult: Result object describing the maximum
		spanning tree.

	"""
	return _spanning_tree(graph, maximize=True)
