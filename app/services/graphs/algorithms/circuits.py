"""Circuit and fundamental-circuit algorithms.

Author: Juan Esteban Bedoya <jebedoyal@udistrital.edu.co>
"""

from __future__ import annotations

from collections import deque
from typing import Dict, List, Set, Tuple

import networkx as nx

from app.services.graphs.models import CircuitResult, Graph


def _edge_name_map(graph: Graph) -> Dict[Tuple[str, str], List[str]]:
	"""Map undirected vertex pairs to edge names."""
	mapping: Dict[Tuple[str, str], List[str]] = {}
	for edge in graph.edges.values():
		key = tuple(sorted((edge.source, edge.target)))
		mapping.setdefault(key, []).append(edge.name)
	return mapping


def all_circuits(graph: Graph) -> CircuitResult:
	"""Detect all simple circuits in the graph."""
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
	"""Find edge path between two vertices in a tree."""
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
	"""Build fundamental circuits from branches and chords.

	Each resulting circuit contains exactly one chord.
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
