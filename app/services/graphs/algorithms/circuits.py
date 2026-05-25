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
	"""Detect all simple circuits ignoring edge direction."""
	g = nx.Graph()
	g.add_nodes_from(graph.vertices)
	for edge in graph.edges.values():
		g.add_edge(edge.source, edge.target, name=edge.name)

	cycles = nx.cycle_basis(g)
	edge_map = _edge_name_map(graph)
	circuit_edges: List[List[str]] = []

	for cycle in cycles:
		edges: List[str] = []
		for idx in range(len(cycle)):
			u = cycle[idx]
			v = cycle[(idx + 1) % len(cycle)]
			key = tuple(sorted((u, v)))
			names = sorted(edge_map.get(key, []))
			if names:
				edges.append(names[0])
		circuit_edges.append(sorted(set(edges)))

	edge_labels = sorted(graph.edges)
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
