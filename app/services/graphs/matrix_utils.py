"""Matrix utility functions for graph representations.

Author: Juan Esteban Bedoya <jebedoyal@udistrital.edu.co>
"""

from __future__ import annotations

from typing import Dict, List

from app.services.graphs.models import Graph


def incidence_matrix(graph: Graph) -> Dict[str, List[List[int]] | List[str]]:
	"""Build vertex-vs-edge incidence matrix.

	For directed edges, outgoing incidence is -1 and incoming is +1.
	For undirected edges, both endpoints receive +1.
	
	Args:
		graph (Graph): Input graph.

	Returns:
		Dict[str, List[List[int]] | List[str]]: Matrix and labels.

	"""
	vertex_labels = sorted(graph.vertices)
	edge_labels = sorted(graph.edges)
	vertex_index = {name: idx for idx, name in enumerate(vertex_labels)}
	matrix = [[0 for _ in edge_labels] for _ in vertex_labels]

	for edge_idx, edge_name in enumerate(edge_labels):
		edge = graph.edges[edge_name]
		src_idx = vertex_index[edge.source]
		tgt_idx = vertex_index[edge.target]
		if edge.directed:
			matrix[src_idx][edge_idx] = -1
			matrix[tgt_idx][edge_idx] = 1
		else:
			matrix[src_idx][edge_idx] = 1
			matrix[tgt_idx][edge_idx] = 1

	return {
		'rows': vertex_labels,
		'cols': edge_labels,
		'matrix': matrix,
	}


def vertex_adjacency_matrix(graph: Graph) -> Dict[str, List[List[int]] | List[str]]:
	"""Build vertex-vs-vertex adjacency matrix."""
	labels = sorted(graph.vertices)
	index = {name: idx for idx, name in enumerate(labels)}
	matrix = [[0 for _ in labels] for _ in labels]

	for edge in graph.edges.values():
		u = index[edge.source]
		v = index[edge.target]
		matrix[u][v] += 1
		if not edge.directed:
			matrix[v][u] += 1

	return {
		'rows': labels,
		'cols': labels,
		'matrix': matrix,
	}


def edge_adjacency_matrix(graph: Graph) -> Dict[str, List[List[int]] | List[str]]:
	"""Build edge-vs-edge adjacency matrix."""
	edge_labels = sorted(graph.edges)
	edges = [graph.edges[name] for name in edge_labels]
	matrix = [[0 for _ in edge_labels] for _ in edge_labels]

	for i, left in enumerate(edges):
		for j, right in enumerate(edges):
			if i == j:
				continue
			left_vertices = {left.source, left.target}
			right_vertices = {right.source, right.target}
			if left_vertices.intersection(right_vertices):
				matrix[i][j] = 1

	return {
		'rows': edge_labels,
		'cols': edge_labels,
		'matrix': matrix,
	}
