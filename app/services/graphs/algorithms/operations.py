"""Graph algebra and structural operations.

Provide utility functions and graph-algebra operations used by the graph
service layer. The module includes support for graph copying, structural
modification, graph complement generation, and several algebraic graph
products such as union, intersection, cartesian product, tensor product,
and composition.

All operations work directly with the Graph, Vertex, and Edge domain
models and preserve graph metadata whenever possible.

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

from copy import deepcopy
from itertools import product
from typing import Dict, Iterable, Tuple

from app.services.graphs.models import Edge, Graph, Vertex


def copy_graph(graph: Graph, graph_id: str) -> Graph:
	"""Create a deep copy of a graph with a new identifier.

	The copied graph preserves all vertices, edges, weights,
	direction configuration, and derived metadata.

	Args:
		graph (Graph): Source graph to duplicate.
		graph_id (str): Identifier assigned to the copied graph.

	Returns:
		Graph: A deep copy of the original graph.

	"""
	new_graph = Graph(graph_id=graph_id, directed=graph.directed, weighted=graph.weighted)
	new_graph.vertices = {
		name: Vertex(name=v.name, ordinal=v.ordinal) for name, v in graph.vertices.items()
	}
	new_graph.edges = {
		name: Edge(
			name=edge.name,
			source=edge.source,
			target=edge.target,
			directed=edge.directed,
			weight=edge.weight,
		)
		for name, edge in graph.edges.items()
	}
	new_graph.derived = deepcopy(graph.derived)
	return new_graph


def _edge_signature(edge: Edge, directed: bool) -> Tuple[str, str, float | None]:
	"""Build a canonical edge signature for comparisons.

	For directed graphs the signature preserves orientation.
	For undirected graphs the vertex pair is normalized
	alphabetically to ensure consistent comparison.

	Args:
		edge (Edge): Edge to normalize.
		directed (bool): Indicates whether orientation matters.

	Returns:
		Tuple[str, str, float | None]:
			Canonical edge representation.

	"""
	if directed:
		return (edge.source, edge.target, edge.weight)
	ordered = tuple(sorted((edge.source, edge.target)))
	return (ordered[0], ordered[1], edge.weight)


def _edge_by_signature(graph: Graph, directed: bool) -> Dict[Tuple[str, str, float | None], Edge]:
	"""Index graph edges by canonical signature.

	Args:
		graph (Graph): Graph whose edges will be indexed.
		directed (bool): Indicates whether edge orientation
			should be preserved.

	Returns:
		Dict[Tuple[str, str, float | None], Edge]:
			Dictionary mapping canonical signatures to edges.

	"""
	return {_edge_signature(edge, directed): edge for edge in graph.edges.values()}


def _merge_edges(
	result: Graph,
	edges: Iterable[Edge],
	used_names: set[str],
	prefix: str,
) -> None:
	"""Merge edges into a graph while preserving unique names.

	If an edge name already exists in the destination graph,
	a new unique name is generated automatically using the
	provided prefix.

	Args:
		result (Graph): Destination graph.
		edges (Iterable[Edge]): Edges to insert.
		used_names (set[str]): Set of names already used.
		prefix (str): Prefix used to generate replacement names.

	"""
	counter = 1
	for edge in edges:
		edge_name = edge.name
		while edge_name in used_names:
			edge_name = f'{prefix}_{counter}'
			counter += 1
		used_names.add(edge_name)
		result.edges[edge_name] = Edge(
			name=edge_name,
			source=edge.source,
			target=edge.target,
			directed=edge.directed,
			weight=edge.weight,
		)


def union_graphs(graph_a: Graph, graph_b: Graph, result_id: str) -> Graph:
	"""Compute the union of two graphs.

	The resulting graph contains all vertices and all edges
	from both input graphs.

	Args:
		graph_a (Graph): First graph operand.
		graph_b (Graph): Second graph operand.
		result_id (str): Identifier for the resulting graph.

	Returns:
		Graph: Union graph.

	"""
	result = Graph(graph_id=result_id, directed=graph_a.directed, weighted=graph_a.weighted)
	for name in sorted(set(graph_a.vertices).union(graph_b.vertices)):
		result.vertices[name] = Vertex(name=name)

	used_names: set[str] = set()
	_merge_edges(result, graph_a.edges.values(), used_names, 'u')
	_merge_edges(result, graph_b.edges.values(), used_names, 'u')

	result.derived['operation'] = {
		'name': 'union',
		'left': graph_a.graph_id,
		'right': graph_b.graph_id,
	}
	return result


def intersection_graphs(graph_a: Graph, graph_b: Graph, result_id: str) -> Graph:
	"""Compute the intersection of two graphs.

	The resulting graph contains only vertices and edges
	present in both graphs.

	Args:
		graph_a (Graph): First graph operand.
		graph_b (Graph): Second graph operand.
		result_id (str): Identifier for the resulting graph.

	Returns:
		Graph: Intersection graph.

	"""
	result = Graph(graph_id=result_id, directed=graph_a.directed, weighted=graph_a.weighted)
	common_vertices = sorted(set(graph_a.vertices).intersection(graph_b.vertices))
	for name in common_vertices:
		result.vertices[name] = Vertex(name=name)

	lookup_b = _edge_by_signature(graph_b, graph_a.directed)
	for edge in graph_a.edges.values():
		signature = _edge_signature(edge, graph_a.directed)
		if (
			signature in lookup_b
			and edge.source in result.vertices
			and edge.target in result.vertices
		):
			result.edges[edge.name] = Edge(
				name=edge.name,
				source=edge.source,
				target=edge.target,
				directed=edge.directed,
				weight=edge.weight,
			)

	result.derived['operation'] = {
		'name': 'intersection',
		'left': graph_a.graph_id,
		'right': graph_b.graph_id,
	}
	return result


def ring_sum_graphs(graph_a: Graph, graph_b: Graph, result_id: str) -> Graph:
	"""Compute the ring sum (symmetric difference) of two graphs.

	The resulting graph contains all edges that belong to
	exactly one of the two graphs.

	Args:
		graph_a (Graph): First graph operand.
		graph_b (Graph): Second graph operand.
		result_id (str): Identifier for the resulting graph.

	Returns:
		Graph: Ring-sum graph.

	"""
	union = union_graphs(graph_a, graph_b, result_id)
	inter = intersection_graphs(graph_a, graph_b, f'{result_id}_intermediate_intersection')

	inter_signatures = {_edge_signature(edge, graph_a.directed) for edge in inter.edges.values()}
	filtered_edges: Dict[str, Edge] = {}
	for edge in union.edges.values():
		if _edge_signature(edge, graph_a.directed) not in inter_signatures:
			filtered_edges[edge.name] = edge

	union.edges = filtered_edges
	union.derived['operation'] = {
		'name': 'ring_sum',
		'left': graph_a.graph_id,
		'right': graph_b.graph_id,
	}
	return union


def sum_graphs(graph_a: Graph, graph_b: Graph, result_id: str) -> Graph:
	"""Compute the graph sum of two graphs.

	This operation behaves as a structural merge preserving
	all vertices and edges from both operands.

	Args:
		graph_a (Graph): First graph operand.
		graph_b (Graph): Second graph operand.
		result_id (str): Identifier for the resulting graph.

	Returns:
		Graph: Sum graph.

	"""
	result = union_graphs(graph_a, graph_b, result_id)
	result.derived['operation']['name'] = 'sum'
	return result


def add_vertex(graph: Graph, vertex_name: str) -> None:
	"""Add a vertex to a graph.

	Args:
		graph (Graph): Target graph.
		vertex_name (str): Vertex identifier.

	"""
	graph.vertices[vertex_name] = Vertex(name=vertex_name)


def remove_vertex(graph: Graph, vertex_name: str) -> None:
	"""Remove a vertex and all incident edges.

	Args:
		graph (Graph): Target graph.
		vertex_name (str): Vertex identifier.

	"""
	graph.vertices.pop(vertex_name, None)
	for edge_name in list(graph.edges):
		edge = graph.edges[edge_name]
		if edge.source == vertex_name or edge.target == vertex_name:
			del graph.edges[edge_name]


def add_edge(
	graph: Graph,
	edge_name: str,
	source: str,
	target: str,
	directed: bool,
	weight: float | None,
) -> None:
	"""Add an edge to a graph.

	Args:
		graph (Graph): Target graph.
		edge_name (str): Edge identifier.
		source (str): Source vertex.
		target (str): Target vertex.
		directed (bool): Indicates whether the edge is directed.
		weight (float | None): Optional edge weight.

	"""
	graph.edges[edge_name] = Edge(
		name=edge_name,
		source=source,
		target=target,
		directed=directed,
		weight=weight,
	)


def remove_edge(graph: Graph, edge_name: str) -> None:
	"""Remove an edge from a graph.

	Args:
		graph (Graph): Target graph.
		edge_name (str): Edge identifier.

	"""
	graph.edges.pop(edge_name, None)


def vertex_fusion(graph: Graph, left_vertex: str, right_vertex: str, new_vertex: str) -> None:
	"""Fuse two vertices into a single vertex.

	All incident edges are redirected to the new vertex.
	Self-loops generated by the fusion are removed.

	Args:
		graph (Graph): Target graph.
		left_vertex (str): First vertex to merge.
		right_vertex (str): Second vertex to merge.
		new_vertex (str): Resulting fused vertex.

	"""
	if new_vertex not in graph.vertices:
		graph.vertices[new_vertex] = Vertex(name=new_vertex)
	for edge in graph.edges.values():
		if edge.source in (left_vertex, right_vertex):
			edge.source = new_vertex
		if edge.target in (left_vertex, right_vertex):
			edge.target = new_vertex

	if left_vertex != new_vertex:
		graph.vertices.pop(left_vertex, None)
	if right_vertex != new_vertex:
		graph.vertices.pop(right_vertex, None)

	for edge_name in list(graph.edges):
		edge = graph.edges[edge_name]
		if edge.source == edge.target:
			del graph.edges[edge_name]


def edge_contraction(graph: Graph, edge_name: str, new_vertex: str) -> None:
	"""Contract an edge by fusing its endpoints.

	Args:
		graph (Graph): Target graph.
		edge_name (str): Edge to contract.
		new_vertex (str): Resulting fused vertex.

	"""
	edge = graph.edges[edge_name]
	vertex_fusion(graph, edge.source, edge.target, new_vertex)
	if edge_name in graph.edges:
		del graph.edges[edge_name]


def complement_graph(graph: Graph, result_id: str) -> Graph:
	"""Build the complement graph.

	The complement contains every missing edge between
	vertices under the same direction mode.

	Args:
		graph (Graph): Base graph.
		result_id (str): Identifier for the resulting graph.

	Returns:
		Graph: Complement graph.

	"""
	result = Graph(graph_id=result_id, directed=graph.directed, weighted=graph.weighted)
	for name in sorted(graph.vertices):
		result.vertices[name] = Vertex(name=name)

	if graph.directed:
		existing = {(edge.source, edge.target) for edge in graph.edges.values()}
	else:
		existing = {tuple(sorted((edge.source, edge.target))) for edge in graph.edges.values()}
	edge_counter = 1
	vertex_names = sorted(graph.vertices)

	if graph.directed:
		for src in vertex_names:
			for tgt in vertex_names:
				if src == tgt:
					continue
				signature = (src, tgt)
				if signature in existing:
					continue
				edge_name = f'c{edge_counter}'
				edge_counter += 1
				result.edges[edge_name] = Edge(
					name=edge_name,
					source=src,
					target=tgt,
					directed=True,
					weight=None if not graph.weighted else 1.0,
				)
	else:
		for i, src in enumerate(vertex_names):
			for tgt in vertex_names[i + 1 :]:
				signature = (src, tgt)
				if signature in existing:
					continue
				edge_name = f'c{edge_counter}'
				edge_counter += 1
				result.edges[edge_name] = Edge(
					name=edge_name,
					source=src,
					target=tgt,
					directed=False,
					weight=None if not graph.weighted else 1.0,
				)

	result.derived['operation'] = {'name': 'complement', 'base': graph.graph_id}
	return result


def cartesian_product(graph_a: Graph, graph_b: Graph, result_id: str) -> Graph:
	"""Build the cartesian product graph G □ H.

	Vertices are ordered pairs formed from both graphs.
	Edges preserve adjacency in one factor while the
	other factor remains fixed.

	Args:
		graph_a (Graph): First graph operand.
		graph_b (Graph): Second graph operand.
		result_id (str): Identifier for the resulting graph.

	Returns:
		Graph: Cartesian-product graph.

	"""
	result = Graph(graph_id=result_id, directed=graph_a.directed, weighted=graph_a.weighted)
	for va, vb in product(sorted(graph_a.vertices), sorted(graph_b.vertices)):
		name = f'({va},{vb})'
		result.vertices[name] = Vertex(name=name)

	edge_counter = 1
	for edge in graph_a.edges.values():
		for vb in graph_b.vertices:
			source = f'({edge.source},{vb})'
			target = f'({edge.target},{vb})'
			name = f'cp{edge_counter}'
			edge_counter += 1
			result.edges[name] = Edge(
				name=name, source=source, target=target, directed=edge.directed, weight=edge.weight
			)

	for edge in graph_b.edges.values():
		for va in graph_a.vertices:
			source = f'({va},{edge.source})'
			target = f'({va},{edge.target})'
			name = f'cp{edge_counter}'
			edge_counter += 1
			result.edges[name] = Edge(
				name=name, source=source, target=target, directed=edge.directed, weight=edge.weight
			)

	result.derived['operation'] = {
		'name': 'cartesian_product',
		'left': graph_a.graph_id,
		'right': graph_b.graph_id,
	}
	return result


def tensor_product(graph_a: Graph, graph_b: Graph, result_id: str) -> Graph:
	"""Build the tensor (direct) product graph G × H.

	Two vertices are adjacent only if their corresponding
	components are adjacent in both graphs.

	Args:
		graph_a (Graph): First graph operand.
		graph_b (Graph): Second graph operand.
		result_id (str): Identifier for the resulting graph.

	Returns:
		Graph: Tensor-product graph.

	"""
	result = Graph(graph_id=result_id, directed=graph_a.directed, weighted=graph_a.weighted)
	for va, vb in product(sorted(graph_a.vertices), sorted(graph_b.vertices)):
		name = f'({va},{vb})'
		result.vertices[name] = Vertex(name=name)

	edge_counter = 1
	for edge_a in graph_a.edges.values():
		for edge_b in graph_b.edges.values():
			source = f'({edge_a.source},{edge_b.source})'
			target = f'({edge_a.target},{edge_b.target})'
			name = f'tp{edge_counter}'
			edge_counter += 1
			weight = None
			if graph_a.weighted:
				weight = float(edge_a.weight or 0.0) + float(edge_b.weight or 0.0)
			result.edges[name] = Edge(
				name=name,
				source=source,
				target=target,
				directed=edge_a.directed or edge_b.directed,
				weight=weight,
			)

	result.derived['operation'] = {
		'name': 'tensor_product',
		'left': graph_a.graph_id,
		'right': graph_b.graph_id,
	}
	return result


def composition(graph_a: Graph, graph_b: Graph, result_id: str) -> Graph:
	"""Build the graph composition G[H].

	The composition connects copies of H according to
	the adjacency structure of G.

	Args:
		graph_a (Graph): First graph operand.
		graph_b (Graph): Second graph operand.
		result_id (str): Identifier for the resulting graph.

	Returns:
		Graph: Composition graph.

	"""
	result = Graph(graph_id=result_id, directed=graph_a.directed, weighted=graph_a.weighted)
	for va, vb in product(sorted(graph_a.vertices), sorted(graph_b.vertices)):
		name = f'({va},{vb})'
		result.vertices[name] = Vertex(name=name)

	edge_counter = 1
	for va in graph_a.vertices:
		for edge_b in graph_b.edges.values():
			source = f'({va},{edge_b.source})'
			target = f'({va},{edge_b.target})'
			name = f'co{edge_counter}'
			edge_counter += 1
			result.edges[name] = Edge(
				name=name,
				source=source,
				target=target,
				directed=edge_b.directed,
				weight=edge_b.weight,
			)

	for edge_a in graph_a.edges.values():
		for vb1, vb2 in product(graph_b.vertices, graph_b.vertices):
			source = f'({edge_a.source},{vb1})'
			target = f'({edge_a.target},{vb2})'
			name = f'co{edge_counter}'
			edge_counter += 1
			result.edges[name] = Edge(
				name=name,
				source=source,
				target=target,
				directed=edge_a.directed,
				weight=edge_a.weight,
			)

	result.derived['operation'] = {
		'name': 'composition',
		'left': graph_a.graph_id,
		'right': graph_b.graph_id,
	}
	return result
