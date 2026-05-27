"""Independent set algorithms for graphs.

Provide utilities to compute independent vertex sets in an undirected
interpretation of a graph. The module includes exhaustive generation of
all independent sets, identification of maximal and maximum independent
sets, and computation of the graph independence number.

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

from itertools import combinations
from typing import Dict, List, Set

from app.services.graphs.models import Graph, IndependentSetsResult


def _neighbors(graph: Graph) -> Dict[str, Set[str]]:
	"""Build an undirected neighborhood map for each vertex.

	Create a dictionary where every vertex is associated with the set
	of adjacent vertices. Edges are treated as undirected regardless
	of the graph orientation.

	Args:
		graph: Graph whose adjacency relationships will be analyzed.

	Returns:
		Dict[str, Set[str]]: Mapping from each vertex name to the
		set of neighboring vertices.

	"""
	neighbors: Dict[str, Set[str]] = {name: set() for name in graph.vertices}
	for edge in graph.edges.values():
		neighbors[edge.source].add(edge.target)
		neighbors[edge.target].add(edge.source)
	return neighbors


def independent_sets(graph: Graph) -> IndependentSetsResult:
	"""Compute all independent-set families of a graph.

	Enumerate every subset of vertices and determine whether it forms
	an independent set, meaning that no two vertices in the subset are
	adjacent. From the complete collection, derive:

	- All independent sets.
	- Maximum independent sets.
	- Maximal independent sets.
	- The independence number.

	Args:
		graph: Graph whose independent sets will be computed.

	Returns:
		IndependentSetsResult: Object containing all independent sets,
		maximal independent sets, maximum independent sets, and the
		independence number.

	"""
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
