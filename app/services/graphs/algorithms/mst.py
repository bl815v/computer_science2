"""Tree-center and minimum spanning tree algorithms.

Author: Juan Esteban Bedoya <jebedoyal@udistrital.edu.co>
"""

from __future__ import annotations

from collections import deque
from typing import Dict, List, Tuple

from app.services.graphs.models import Graph, MSTResult
from app.services.graphs.validators import GraphValidationError


class _DisjointSet:
	"""Disjoint-set data structure for Kruskal algorithm."""

	def __init__(self, elements: List[str]) -> None:
		self.parent = {element: element for element in elements}
		self.rank = {element: 0 for element in elements}

	def find(self, value: str) -> str:
		"""Find representative with path compression."""
		if self.parent[value] != value:
			self.parent[value] = self.find(self.parent[value])
		return self.parent[value]

	def union(self, left: str, right: str) -> bool:
		"""Union sets by rank."""
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
	"""Build undirected neighborhood regardless of edge direction."""
	adjacency = {name: [] for name in graph.vertices}
	for edge in graph.edges.values():
		adjacency[edge.source].append(edge.target)
		adjacency[edge.target].append(edge.source)
	return adjacency


def _is_connected(graph: Graph) -> bool:
	"""Check graph connectivity using BFS."""
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
	"""Validate that graph is a tree under undirected interpretation."""
	if not _is_connected(graph):
		raise GraphValidationError('Graph must be connected to be a tree')
	if len(graph.edges) != max(0, len(graph.vertices) - 1):
		raise GraphValidationError('Graph is not a tree: invalid edge count')


def center_or_bicenter(graph: Graph) -> Dict[str, object]:
	"""Compute center or bicenter of a tree."""
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


def minimum_spanning_tree(graph: Graph) -> MSTResult:
	"""Compute minimum spanning tree using Kruskal algorithm."""
	if graph.directed:
		raise GraphValidationError('MST requires an undirected graph')
	if not _is_connected(graph):
		raise GraphValidationError('MST requires a connected graph')

	weighted_edges: List[Tuple[float, str, str, str]] = []
	for edge in graph.edges.values():
		if edge.weight is None:
			raise GraphValidationError('MST requires weighted edges')
		weighted_edges.append((float(edge.weight), edge.name, edge.source, edge.target))

	weighted_edges.sort(key=lambda item: (item[0], item[1]))
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
