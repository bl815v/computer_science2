"""Matching algorithms for graphs.

Author: Juan Esteban Bedoya <jebedoyal@udistrital.edu.co>
"""

from __future__ import annotations

from itertools import combinations
from typing import List, Set

from app.services.graphs.algorithms.shared import sorted_edges
from app.services.graphs.models import Graph, MatchingResult


def matching(graph: Graph) -> MatchingResult:
	"""Compute all, maximal, and maximum matchings."""
	edge_labels = sorted_edges(graph)
	edge_endpoints = {name: {graph.edges[name].source, graph.edges[name].target} for name in edge_labels}
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
