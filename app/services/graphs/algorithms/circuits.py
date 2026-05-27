"""Circuit and fundamental-circuit algorithms.

Implement graph algorithms related to circuit detection and
fundamental circuit generation. Support both directed and
undirected graphs by combining NetworkX algorithms with
custom traversal logic.

The module provides utilities for:

	- Detecting all simple circuits in a graph.
	- Building incidence matrices for detected circuits.
	- Computing edge mappings for graph traversal.
	- Finding paths inside spanning trees.
	- Generating fundamental circuits using branches and chords.

Functions:
	_edge_name_map:
		Map undirected edge endpoints to edge identifiers.

	all_circuits:
		Detect all simple circuits in a graph and generate
		the corresponding circuit matrix.

	_tree_path:
		Find the unique edge path between two vertices
		inside a tree structure.

	fundamental_circuits:
		Generate fundamental circuits from spanning-tree
		branches and graph chords.

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
from typing import Dict, List, Set, Tuple

import networkx as nx

from app.services.graphs.models import CircuitResult, Graph


def _edge_name_map(graph: Graph) -> Dict[Tuple[str, str], List[str]]:
	(
		"""Map undirected vertex pairs to edge identifiers.

	Create a dictionary where each key represents an
	undirected vertex pair and each value contains the
	list of edge names connecting those vertices.

	This utility simplifies edge retrieval during
	circuit detection in undirected graphs.

	Args:
		graph (Graph):
			Graph instance containing vertices and edges.

	Returns:
		Dict[Tuple[str, str], List[str]]:
			Dictionary mapping sorted vertex pairs
			to edge-name lists.

	"""
		"""Map undirected vertex pairs to edge identifiers.

	Create a dictionary where each key represents an
	undirected vertex pair and each value contains the
	list of edge names connecting those vertices.

	This utility simplifies edge retrieval during
	circuit detection in undirected graphs.

	Args:
		graph (Graph):
			Graph instance containing vertices and edges.

	Returns:
		Dict[Tuple[str, str], List[str]]:
			Dictionary mapping sorted vertex pairs
			to edge-name lists.

	"""
	)
	mapping: Dict[Tuple[str, str], List[str]] = {}
	for edge in graph.edges.values():
		key = tuple(sorted((edge.source, edge.target)))
		mapping.setdefault(key, []).append(edge.name)
	return mapping


def all_circuits(graph: Graph) -> CircuitResult:
	"""Detect all simple circuits in the graph.

	Support both directed and undirected graphs:

		- Directed graphs use NetworkX simple-cycle detection.
		- Undirected graphs use a depth-first traversal
		  with duplicate avoidance.

		The resulting circuits are transformed into
		a binary incidence matrix where rows represent
		circuits and columns represent graph edges.

	Args:
		graph (Graph):
			Graph instance to analyze.

	Returns:
		CircuitResult:
			Object containing:

				- circuits:
				  List of detected circuits represented
				  by edge names.

				- matrix:
				  Binary circuit-edge incidence matrix.

				- edge_labels:
				  Ordered list of graph edge identifiers.

	"""
	edge_map = _edge_name_map(graph)
	edge_labels = sorted(graph.edges)
	circuit_set: Set[Tuple[str, ...]] = set()

	if graph.directed:
		digraph = nx.DiGraph()
		digraph.add_nodes_from(graph.vertices)
		directed_edge_map: Dict[Tuple[str, str], List[str]] = {}
		for edge in graph.edges.values():
			digraph.add_edge(edge.source, edge.target, name=edge.name)
			directed_edge_map.setdefault((edge.source, edge.target), []).append(edge.name)
		for cycle in nx.simple_cycles(digraph):
			edges: List[str] = []
			for index, vertex in enumerate(cycle):
				neighbor = cycle[(index + 1) % len(cycle)]
				names = sorted(directed_edge_map.get((vertex, neighbor), []))
				if names:
					edges.append(names[0])
			if len(edges) >= 2:
				circuit_set.add(tuple(sorted(set(edges))))
	else:
		adjacency: Dict[str, List[str]] = {name: [] for name in graph.vertices}
		for edge in graph.edges.values():
			adjacency[edge.source].append(edge.target)
			adjacency[edge.target].append(edge.source)
		for name in adjacency:
			adjacency[name] = sorted(set(adjacency[name]))

		vertices = sorted(graph.vertices)

		def dfs(start: str, current: str, path: List[str], seen: Set[str]) -> None:
			"""Perform DFS traversal for undirected cycle detection.

			Args:
				start (str):
					Starting vertex of the traversal.

				current (str):
					Current vertex being explored.

				path (List[str]):
					Ordered traversal path.

				seen (Set[str]):
					Set of visited vertices.

			"""
			for neighbor in adjacency[current]:
				if neighbor == start and len(path) >= 3:
					edges: List[str] = []
					cycle_vertices = path + [start]
					for index, vertex in enumerate(cycle_vertices[:-1]):
						next_vertex = cycle_vertices[index + 1]
						key = tuple(sorted((vertex, next_vertex)))
						names = sorted(edge_map.get(key, []))
						if names:
							edges.append(names[0])
					if len(edges) >= 3:
						circuit_set.add(tuple(sorted(set(edges))))
				continue
				if neighbor in seen or neighbor < start:
					continue
				dfs(start, neighbor, path + [neighbor], seen | {neighbor})

		for start in vertices:
			dfs(start, start, [start], {start})

	circuit_edges = [list(circuit) for circuit in sorted(circuit_set)]

	matrix = [[1 if edge in circuit else 0 for edge in edge_labels] for circuit in circuit_edges]

	return CircuitResult(circuits=circuit_edges, matrix=matrix, edge_labels=edge_labels)


def _tree_path(
	tree_adjacency: Dict[str, List[Tuple[str, str]]],
	source: str,
	target: str,
) -> List[str]:
	"""Find the edge path between two vertices in a tree.

	Perform a breadth-first traversal over a tree adjacency
	structure to recover the unique edge sequence connecting
	the source and target vertices.

	Args:
		tree_adjacency (Dict[str, List[Tuple[str, str]]]):
			Tree adjacency list where each entry contains
			neighbor vertices and edge identifiers.

		source (str):
			Starting vertex identifier.

		target (str):
			Destination vertex identifier.

	Returns:
		List[str]:
			Ordered list of edge identifiers forming
			the path between the two vertices.

			Returns an empty list if no path exists.

	"""
	queue = deque([(source, [])])
	seen: Set[str] = {source}
	while queue:
		current, path = queue.popleft()
		if current == target:
			return path
		for neighbor, edge_name in tree_adjacency.get(current, []):
			if neighbor in seen:
				continue
			seen.add(neighbor)
			queue.append((neighbor, path + [edge_name]))
	return []


def fundamental_circuits(graph: Graph, branches: List[str], chords: List[str]) -> CircuitResult:
	"""Generate fundamental circuits from branches and chords.

	Construct a spanning-tree adjacency representation
	using the provided branch edges. For each chord,
	find the unique path inside the tree and combine
	it with the chord to form a fundamental circuit.

	Each generated circuit contains exactly one chord.

	The resulting circuits are also converted into
	a binary incidence matrix.

	Args:
		graph (Graph):
			Original graph instance.

		branches (List[str]):
			Edge names belonging to the spanning tree.

		chords (List[str]):
			Edge names not included in the spanning tree.

	Returns:
		CircuitResult:
			Object containing:

				- circuits:
				  Fundamental circuits represented
				  as edge-name lists.

				- matrix:
				  Binary incidence matrix relating
				  circuits and edges.

				- edge_labels:
				  Ordered list of graph edge identifiers.

	"""
	tree_adjacency: Dict[str, List[Tuple[str, str]]] = {name: [] for name in graph.vertices}
	for edge_name in branches:
		edge = graph.edges[edge_name]
		tree_adjacency[edge.source].append((edge.target, edge_name))
		tree_adjacency[edge.target].append((edge.source, edge_name))

	circuits: List[List[str]] = []
	for chord_name in chords:
		chord = graph.edges[chord_name]
		path_edges = _tree_path(tree_adjacency, chord.source, chord.target)
		if not path_edges:
			continue
		circuits.append(sorted(set(path_edges + [chord_name])))

	edge_labels = sorted(graph.edges)
	matrix = [[1 if edge in circuit else 0 for edge in edge_labels] for circuit in circuits]
	return CircuitResult(circuits=circuits, matrix=matrix, edge_labels=edge_labels)
