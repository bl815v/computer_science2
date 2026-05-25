"""Independent set algorithms.

Author: Juan Esteban Bedoya <jebedoyal@udistrital.edu.co>
"""

from __future__ import annotations

from itertools import combinations
from typing import Dict, List, Set

from app.services.graphs.models import Graph, IndependentSetsResult


def _neighbors(graph: Graph) -> Dict[str, Set[str]]:
	"""Build undirected neighbor sets."""
	neighbors: Dict[str, Set[str]] = {name: set() for name in graph.vertices}
	for edge in graph.edges.values():
		neighbors[edge.source].add(edge.target)
		neighbors[edge.target].add(edge.source)
	return neighbors


def independent_sets(graph: Graph) -> IndependentSetsResult:
	"""Compute all, maximal, and maximum independent sets."""
	vertices = sorted(graph.vertices)
	neighbors = _neighbors(graph)
	all_sets: List[List[str]] = []

	for size in range(0, len(vertices) + 1):
		for subset in combinations(vertices, size):
			ok = True
			for idx, left in enumerate(subset):
				for right in subset[idx + 1 :]:
					if right in neighbors[left]:
						ok = False
						break
				if not ok:
					break
			if ok:
				all_sets.append(list(subset))

	max_size = max((len(item) for item in all_sets), default=0)
	maximum_sets = sorted([item for item in all_sets if len(item) == max_size])

	maximal_sets: List[List[str]] = []
	for candidate in all_sets:
		candidate_set = set(candidate)
		is_maximal = True
		for other in all_sets:
			other_set = set(other)
			if candidate_set < other_set:
				is_maximal = False
				break
		if is_maximal:
			maximal_sets.append(candidate)

	maximal_sets = sorted(maximal_sets)

	return IndependentSetsResult(
		all_sets=sorted(all_sets),
		independence_number=max_size,
		maximum_sets=maximum_sets,
		maximal_sets=maximal_sets,
	)
