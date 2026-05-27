"""Domination algorithms for graphs.

Author: Juan Esteban Bedoya <jebedoyal@udistrital.edu.co>
"""

from __future__ import annotations

from itertools import combinations
from typing import Dict, List, Set

from app.services.graphs.algorithms.independent_sets import independent_sets
from app.services.graphs.algorithms.shared import sorted_vertices, undirected_neighbors
from app.services.graphs.models import DominationResult, Graph


def domination(graph: Graph) -> DominationResult:
	"""Compute dominating sets, minimum dominating sets, and independence overlap."""
	vertices = sorted_vertices(graph)
	neighbors = undirected_neighbors(graph)
	all_vertices = set(vertices)
	dominating_sets: List[List[str]] = []

	for size in range(0, len(vertices) + 1):
		for subset in combinations(vertices, size):
			dominated = set(subset)
			for vertex in subset:
				dominated.update(neighbors[vertex])
			if dominated == all_vertices:
				dominating_sets.append(list(subset))

	minimum_size = min((len(item) for item in dominating_sets), default=0)
	minimum_dominating_sets = sorted([item for item in dominating_sets if len(item) == minimum_size])
	independent_lookup = {frozenset(item) for item in independent_sets(graph).all_sets}
	independent_dominating_sets = sorted(
		[item for item in dominating_sets if frozenset(item) in independent_lookup]
	)

	return DominationResult(
		dominating_sets=sorted(dominating_sets),
		minimum_dominating_sets=minimum_dominating_sets,
		independent_dominating_sets=independent_dominating_sets,
		domination_number=minimum_size,
	)
