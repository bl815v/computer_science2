"""Matching algorithms for graphs.

Provide exhaustive matching analysis utilities for graphs. The module
computes all valid matchings, maximal matchings, maximum matchings,
and the matching number of a graph.

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
from typing import List, Set

from app.services.graphs.algorithms.shared import sorted_edges
from app.services.graphs.models import Graph, MatchingResult


def matching(graph: Graph) -> MatchingResult:
	"""Compute all, maximal, and maximum matchings of a graph.

	A matching is a set of edges such that no two edges share a common
	vertex. This function exhaustively enumerates every valid matching
	and derives:

	- All valid matchings.
	- Maximal matchings.
	- Maximum matchings.
	- The matching number.

	Args:
		graph: Graph whose matchings will be analyzed.

	Returns:
		MatchingResult: Object containing all matchings, maximal
		matchings, maximum matchings, and the matching number.

	"""
	edge_labels = sorted_edges(graph)
	edge_endpoints = {
		name: {graph.edges[name].source, graph.edges[name].target} for name in edge_labels
	}
	all_matchings: List[List[str]] = []

	for size in range(0, len(edge_labels) + 1):
		for subset in combinations(edge_labels, size):
			valid = True
			for index, left in enumerate(subset):
				for right in subset[index + 1 :]:
					if edge_endpoints[left].intersection(edge_endpoints[right]):
						valid = False
						break
				if not valid:
					break
			if valid:
				all_matchings.append(list(subset))

	maximum_size = max((len(item) for item in all_matchings), default=0)
	maximum_matchings = sorted([item for item in all_matchings if len(item) == maximum_size])

	maximal_matchings: List[List[str]] = []
	for candidate in all_matchings:
		candidate_set = set(candidate)
		is_maximal = True
		for other in all_matchings:
			other_set = set(other)
			if candidate_set < other_set:
				is_maximal = False
				break
		if is_maximal:
			maximal_matchings.append(candidate)

	return MatchingResult(
		matchings=sorted(all_matchings),
		maximal_matchings=sorted(maximal_matchings),
		maximum_matchings=maximum_matchings,
		matching_number=maximum_size,
	)
