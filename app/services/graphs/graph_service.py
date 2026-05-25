"""Main graph service orchestrating graph operations and algorithms.

Author: Juan Esteban Bedoya <jebedoyal@udistrital.edu.co>
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional

from app.services.graphs.algorithms.circuits import all_circuits, fundamental_circuits
from app.services.graphs.algorithms.coloring import edge_coloring, vertex_coloring
from app.services.graphs.algorithms.independent_sets import independent_sets
from app.services.graphs.algorithms.mst import center_or_bicenter, minimum_spanning_tree, validate_tree
from app.services.graphs.algorithms.operations import (
	add_edge,
	add_vertex,
	cartesian_product,
	composition,
	complement_graph,
	copy_graph,
	edge_contraction,
	intersection_graphs,
	remove_edge,
	remove_vertex,
	ring_sum_graphs,
	sum_graphs,
	tensor_product,
	union_graphs,
	vertex_fusion,
)
from app.services.graphs.algorithms.ordinal import ordinal_function
from app.services.graphs.algorithms.paths import bellman_lambda, dijkstra, tree_distance
from app.services.graphs.matrix_utils import (
	edge_adjacency_matrix,
	incidence_matrix,
	vertex_adjacency_matrix,
)
from app.services.graphs.models import Graph
from app.services.graphs.serializer import (
	GraphSnapshotError,
	from_snapshot,
	to_snapshot,
	validate_snapshot,
)
from app.services.graphs.validators import (
	GraphValidationError,
	ensure_edge_exists,
	ensure_graph_compatibility,
	ensure_graph_exists,
	ensure_has_direction,
	ensure_non_empty_vertices,
	ensure_unique_edge,
	ensure_unique_vertex,
	ensure_vertex_exists,
	ensure_weight,
)


class GraphService:
	"""Provide graph CRUD, algebra, and algorithm operations."""

	def __init__(self) -> None:
		"""Initialize in-memory graph registry."""
		self._graphs: Dict[str, Graph] = {}

	def create_graph(self, graph_id: str, directed: bool, weighted: bool) -> Dict[str, Any]:
		"""Create and register a graph.

		Args:
			graph_id (str): Graph identifier.
			directed (bool): Direction mode.
			weighted (bool): Weight mode.

		Returns:
			Dict[str, Any]: Serialized graph.

		Raises:
			GraphValidationError: If graph already exists.

		"""
		if graph_id in self._graphs:
			raise GraphValidationError(f"Graph '{graph_id}' already exists")
		self._graphs[graph_id] = Graph(graph_id=graph_id, directed=directed, weighted=weighted)
		return self.get_graph(graph_id)

	def get_graph_model(self, graph_id: str) -> Graph:
		"""Return graph model by id."""
		return ensure_graph_exists(self._graphs.get(graph_id), graph_id)

	def get_graph(self, graph_id: str) -> Dict[str, Any]:
		"""Return serialized graph by id."""
		graph = self.get_graph_model(graph_id)
		return self._serialize_graph(graph)

	def list_graphs(self) -> Dict[str, Any]:
		"""Return all registered graphs."""
		return {
			'graphs': [self._serialize_graph(graph) for graph in sorted(self._graphs.values(), key=lambda x: x.graph_id)]
		}

	def add_vertex(self, graph_id: str, vertex_name: str) -> Dict[str, Any]:
		"""Add vertex to graph."""
		graph = self.get_graph_model(graph_id)
		ensure_non_empty_vertices([vertex_name])
		ensure_unique_vertex(graph, vertex_name)
		add_vertex(graph, vertex_name)
		self._refresh_matrices(graph)
		return self._serialize_graph(graph)

	def remove_vertex(self, graph_id: str, vertex_name: str) -> Dict[str, Any]:
		"""Remove vertex from graph."""
		graph = self.get_graph_model(graph_id)
		ensure_vertex_exists(graph, vertex_name)
		remove_vertex(graph, vertex_name)
		self._refresh_matrices(graph)
		return self._serialize_graph(graph)

	def add_edge(
		self,
		graph_id: str,
		edge_name: str,
		source: str,
		target: str,
		directed: Optional[bool] = None,
		weight: Optional[float] = None,
	) -> Dict[str, Any]:
		"""Add edge to graph."""
		graph = self.get_graph_model(graph_id)
		ensure_unique_edge(graph, edge_name)
		ensure_vertex_exists(graph, source)
		ensure_vertex_exists(graph, target)
		effective_directed = graph.directed if directed is None else directed
		ensure_weight(weight, graph.weighted, edge_name)
		add_edge(graph, edge_name, source, target, effective_directed, weight)
		self._refresh_matrices(graph)
		return self._serialize_graph(graph)

	def remove_edge(self, graph_id: str, edge_name: str) -> Dict[str, Any]:
		"""Remove edge from graph."""
		graph = self.get_graph_model(graph_id)
		ensure_edge_exists(graph, edge_name)
		remove_edge(graph, edge_name)
		self._refresh_matrices(graph)
		return self._serialize_graph(graph)

	def union(self, graph_a_id: str, graph_b_id: str, result_id: str = 'result_graph') -> Dict[str, Any]:
		"""Compute graph union."""
		return self._store_result(
			union_graphs,
			graph_a_id,
			graph_b_id,
			result_id,
		)

	def intersection(self, graph_a_id: str, graph_b_id: str, result_id: str = 'result_graph') -> Dict[str, Any]:
		"""Compute graph intersection."""
		return self._store_result(
			intersection_graphs,
			graph_a_id,
			graph_b_id,
			result_id,
		)

	def ring_sum(self, graph_a_id: str, graph_b_id: str, result_id: str = 'result_graph') -> Dict[str, Any]:
		"""Compute graph ring sum."""
		return self._store_result(
			ring_sum_graphs,
			graph_a_id,
			graph_b_id,
			result_id,
		)

	def sum(self, graph_a_id: str, graph_b_id: str, result_id: str = 'result_graph') -> Dict[str, Any]:
		"""Compute graph sum."""
		return self._store_result(
			sum_graphs,
			graph_a_id,
			graph_b_id,
			result_id,
		)

	def complement(self, graph_id: str, result_id: str = 'result_graph') -> Dict[str, Any]:
		"""Compute graph complement."""
		graph = self.get_graph_model(graph_id)
		result = complement_graph(graph, result_id)
		self._finalize_result_graph(result)
		return self._serialize_graph(result)

	def cartesian_product(self, graph_a_id: str, graph_b_id: str, result_id: str = 'result_graph') -> Dict[str, Any]:
		"""Compute cartesian product."""
		return self._store_result(
			cartesian_product,
			graph_a_id,
			graph_b_id,
			result_id,
		)

	def tensor_product(self, graph_a_id: str, graph_b_id: str, result_id: str = 'result_graph') -> Dict[str, Any]:
		"""Compute tensor product."""
		return self._store_result(
			tensor_product,
			graph_a_id,
			graph_b_id,
			result_id,
		)

	def composition(self, graph_a_id: str, graph_b_id: str, result_id: str = 'result_graph') -> Dict[str, Any]:
		"""Compute composition product."""
		return self._store_result(
			composition,
			graph_a_id,
			graph_b_id,
			result_id,
		)

	def vertex_fusion(
		self,
		graph_id: str,
		left_vertex: str,
		right_vertex: str,
		new_vertex: str,
	) -> Dict[str, Any]:
		"""Fuse two vertices in graph."""
		graph = self.get_graph_model(graph_id)
		ensure_vertex_exists(graph, left_vertex)
		ensure_vertex_exists(graph, right_vertex)
		if new_vertex not in (left_vertex, right_vertex):
			ensure_unique_vertex(graph, new_vertex)
		vertex_fusion(graph, left_vertex, right_vertex, new_vertex)
		self._refresh_matrices(graph)
		return self._serialize_graph(graph)

	def edge_contraction(self, graph_id: str, edge_name: str, new_vertex: str) -> Dict[str, Any]:
		"""Contract edge and merge its endpoints."""
		graph = self.get_graph_model(graph_id)
		ensure_edge_exists(graph, edge_name)
		if new_vertex not in graph.vertices:
			ensure_unique_vertex(graph, new_vertex)
		edge_contraction(graph, edge_name, new_vertex)
		self._refresh_matrices(graph)
		return self._serialize_graph(graph)

	def center(self, graph_id: str) -> Dict[str, Any]:
		"""Compute center or bicenter for tree graph."""
		graph = self.get_graph_model(graph_id)
		ensure_has_direction(graph)
		result = center_or_bicenter(graph)
		graph.derived['center'] = result
		return result

	def mst(self, graph_id: str) -> Dict[str, Any]:
		"""Compute minimum spanning tree and complement data."""
		graph = self.get_graph_model(graph_id)
		ensure_has_direction(graph)
		result = minimum_spanning_tree(graph)
		payload = {
			'mst_edges': result.edges,
			'complement_tree_edges': result.complement_edges,
			'branches': result.branches,
			'chords': result.chords,
			'rank': result.rank,
			'nullity': result.nullity,
			'total_weight': result.total_weight,
		}
		graph.derived['mst'] = payload
		return payload

	def tree_distance(self, graph_a_id: str, graph_b_id: str) -> Dict[str, Any]:
		"""Compute weighted tree distance between two trees."""
		graph_a = self.get_graph_model(graph_a_id)
		graph_b = self.get_graph_model(graph_b_id)
		validate_tree(graph_a)
		validate_tree(graph_b)
		result = tree_distance(graph_a, graph_b)
		return result

	def ordinal(self, graph_id: str) -> Dict[str, Any]:
		"""Compute ordinal labels for graph vertices."""
		graph = self.get_graph_model(graph_id)
		result = ordinal_function(graph)
		graph.derived['ordinal'] = result
		return result

	def bellman(self, graph_id: str, source: str, target: Optional[str] = None) -> Dict[str, Any]:
		"""Compute Bellman lambda values using ordinal order."""
		graph = self.get_graph_model(graph_id)
		ordinal_data = graph.derived.get('ordinal')
		if not ordinal_data:
			ordinal_data = self.ordinal(graph_id)
		order = ordinal_data.get('traversal_order', [])
		result = bellman_lambda(graph, source, order, target)
		payload = {
			'source': result.source,
			'target': result.target,
			'lambda_values': result.lambda_values,
			'intermediate_steps': result.intermediate_steps,
			'path': result.path,
		}
		graph.derived['bellman'] = payload
		return payload

	def dijkstra(self, graph_id: str, source: str, target: Optional[str] = None) -> Dict[str, Any]:
		"""Compute Dijkstra shortest paths."""
		graph = self.get_graph_model(graph_id)
		result = dijkstra(graph, source, target)
		payload = {
			'source': result.source,
			'target': result.target,
			'pairs': result.pairs,
			'definitive_order': result.definitive_order,
			'distances': result.distances,
			'path': result.path,
		}
		graph.derived['dijkstra'] = payload
		return payload

	def circuits(self, graph_id: str) -> Dict[str, Any]:
		"""Detect all circuits and build circuit matrix."""
		graph = self.get_graph_model(graph_id)
		result = all_circuits(graph)
		payload = {
			'circuits': result.circuits,
			'edge_labels': result.edge_labels,
			'matrix': result.matrix,
		}
		graph.derived['circuits'] = payload
		return payload

	def fundamental_circuits(self, graph_id: str) -> Dict[str, Any]:
		"""Build fundamental circuits using nullity and chords."""
		graph = self.get_graph_model(graph_id)
		mst_data = graph.derived.get('mst')
		if not mst_data:
			mst_data = self.mst(graph_id)
		result = fundamental_circuits(graph, mst_data.get('branches', []), mst_data.get('chords', []))
		payload = {
			'circuits': result.circuits,
			'edge_labels': result.edge_labels,
			'matrix': result.matrix,
		}
		graph.derived['fundamental_circuits'] = payload
		return payload

	def incidence_matrix(self, graph_id: str) -> Dict[str, Any]:
		"""Return incidence matrix for graph."""
		graph = self.get_graph_model(graph_id)
		matrix = incidence_matrix(graph)
		graph.derived['matrices'] = graph.derived.get('matrices', {})
		graph.derived['matrices']['incidence'] = matrix
		return matrix

	def vertex_adjacency_matrix(self, graph_id: str) -> Dict[str, Any]:
		"""Return vertex adjacency matrix for graph."""
		graph = self.get_graph_model(graph_id)
		matrix = vertex_adjacency_matrix(graph)
		graph.derived['matrices'] = graph.derived.get('matrices', {})
		graph.derived['matrices']['vertex_adjacency'] = matrix
		return matrix

	def edge_adjacency_matrix(self, graph_id: str) -> Dict[str, Any]:
		"""Return edge adjacency matrix for graph."""
		graph = self.get_graph_model(graph_id)
		matrix = edge_adjacency_matrix(graph)
		graph.derived['matrices'] = graph.derived.get('matrices', {})
		graph.derived['matrices']['edge_adjacency'] = matrix
		return matrix

	def vertex_coloring(self, graph_id: str) -> Dict[str, Any]:
		"""Compute vertex coloring."""
		graph = self.get_graph_model(graph_id)
		result = vertex_coloring(graph)
		payload = {
			'chromatic_number': result.chromatic_number,
			'chromatic_polynomial': result.chromatic_polynomial,
			'chromatic_classes': result.classes,
		}
		graph.derived['vertex_coloring'] = payload
		return payload

	def edge_coloring(self, graph_id: str) -> Dict[str, Any]:
		"""Compute edge coloring."""
		graph = self.get_graph_model(graph_id)
		result = edge_coloring(graph)
		payload = {
			'chromatic_index': result.chromatic_index,
			'edge_chromatic_classes': result.edge_classes,
		}
		graph.derived['edge_coloring'] = payload
		return payload

	def independent_sets(self, graph_id: str) -> Dict[str, Any]:
		"""Compute independent-set families and metrics."""
		graph = self.get_graph_model(graph_id)
		result = independent_sets(graph)
		payload = {
			'all_independent_sets': result.all_sets,
			'independence_number': result.independence_number,
			'maximum_independent_sets': result.maximum_sets,
			'maximal_independent_sets': result.maximal_sets,
		}
		graph.derived['independent_sets'] = payload
		return payload

	def validate_snapshot(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
		"""Validate graph snapshot envelope."""
		return validate_snapshot(snapshot)

	def to_snapshot(self) -> Dict[str, Any]:
		"""Export all graphs into a versioned snapshot."""
		return to_snapshot(self._graphs.values())

	def from_snapshot(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
		"""Restore graph registry from snapshot."""
		graphs = from_snapshot(snapshot)
		self._graphs = {graph.graph_id: graph for graph in graphs}
		for graph in self._graphs.values():
			self._refresh_matrices(graph)
		return self.list_graphs()

	def _store_result(
		self,
		operation,
		graph_a_id: str,
		graph_b_id: str,
		result_id: str,
	) -> Dict[str, Any]:
		"""Store result of binary graph operation."""
		graph_a = self.get_graph_model(graph_a_id)
		graph_b = self.get_graph_model(graph_b_id)
		ensure_graph_compatibility(graph_a, graph_b)
		result = operation(graph_a, graph_b, result_id)
		self._finalize_result_graph(result)
		return self._serialize_graph(result)

	def _finalize_result_graph(self, graph: Graph) -> None:
		"""Persist operation result and recalculate dynamic matrices."""
		self._refresh_matrices(graph)
		self._graphs[graph.graph_id] = graph

	def _refresh_matrices(self, graph: Graph) -> None:
		"""Refresh all matrix representations in derived state."""
		graph.derived['matrices'] = {
			'incidence': incidence_matrix(graph),
			'vertex_adjacency': vertex_adjacency_matrix(graph),
			'edge_adjacency': edge_adjacency_matrix(graph),
		}

	def _serialize_graph(self, graph: Graph) -> Dict[str, Any]:
		"""Serialize graph using snapshot serializer and append metadata."""
		snapshot = to_snapshot([graph])
		graph_payload = snapshot['state']['graphs'][0]
		return deepcopy(graph_payload)
