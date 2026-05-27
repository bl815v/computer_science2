"""Domination algorithms for graphs.

Provide algorithms to compute dominating sets, minimum dominating
sets, and independent dominating sets in graphs.

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
from typing import Dict, List, Set

from app.services.graphs.algorithms.independent_sets import independent_sets
from app.services.graphs.algorithms.shared import sorted_vertices, undirected_neighbors
from app.services.graphs.models import DominationResult, Graph


def domination(graph: Graph) -> DominationResult:
	"""Compute dominating-set families and domination metrics.

	A dominating set is a subset of vertices such that every vertex
	in the graph either belongs to the subset or is adjacent to at
	least one vertex in the subset.

	This function exhaustively evaluates all vertex subsets to:
		- Identify every dominating set.
		- Determine the minimum dominating sets.
		- Detect independent dominating sets by comparing against
		  the graph independent sets.
		- Compute the domination number.

	Args:
		graph: Graph to analyze.

	Returns:
		DominationResult: Object containing:
			- ``dominating_sets``:
				All dominating sets of the graph.
			- ``minimum_dominating_sets``:
				Dominating sets with minimum cardinality.
			- ``independent_dominating_sets``:
				Dominating sets that are also independent sets.
			- ``domination_number``:
				Minimum number of vertices required to dominate
				the graph.

	"""
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
	minimum_dominating_sets = sorted(
		[item for item in dominating_sets if len(item) == minimum_size]
	)
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
