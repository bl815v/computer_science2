"""Matrix utility functions for graph representations.

Provide reusable matrix builders for graph structures, including
incidence matrices, vertex adjacency matrices, and edge adjacency
matrices. These utilities standardize graph representations used by
algorithms, analysis modules, and visualization layers.

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

from typing import Dict, List

from app.services.graphs.models import Graph


def incidence_matrix(graph: Graph) -> Dict[str, List[List[int]] | List[str]]:
	"""Build the vertex-edge incidence matrix of a graph.

	Construct a matrix representation describing the relationship
	between vertices and edges. Each row corresponds to a vertex and
	each column corresponds to an edge.

	For directed graphs:
		- Outgoing incidence is represented with ``-1``.
		- Incoming incidence is represented with ``+1``.

	For undirected graphs:
		- Both incident vertices receive ``+1``.

	Args:
		graph (Graph): Input graph.

	Returns:
		Dict[str, List[List[int]] | List[str]]: Dictionary containing:
			- ``rows``: Ordered vertex labels.
			- ``cols``: Ordered edge labels.
			- ``matrix``: Incidence matrix values.

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
	"""Build the vertex adjacency matrix of a graph.

	Construct a square matrix describing adjacency relationships between
	vertices. Each matrix position ``(i, j)`` stores the number of edges
	connecting vertex ``i`` to vertex ``j``.

	For undirected graphs, adjacency is mirrored symmetrically across
	the diagonal.

	Args:
		graph (Graph): Input graph.

	Returns:
		Dict[str, List[List[int]] | List[str]]: Dictionary containing:
			- ``rows``: Ordered vertex labels.
			- ``cols``: Ordered vertex labels.
			- ``matrix``: Vertex adjacency matrix.

	"""
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
	"""Build the edge adjacency matrix of a graph.

	Construct a square matrix describing adjacency relationships between
	edges. Two edges are considered adjacent if they share at least one
	common endpoint vertex.

	Args:
		graph (Graph): Input graph.

	Returns:
		Dict[str, List[List[int]] | List[str]]: Dictionary containing:
			- ``rows``: Ordered edge labels.
			- ``cols``: Ordered edge labels.
			- ``matrix``: Edge adjacency matrix.

	"""
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
