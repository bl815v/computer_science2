"""Main graph service orchestrating graph operations and algorithms.

Provide a centralized service layer responsible for graph lifecycle
management, graph algebra operations, matrix generation, serialization,
and execution of graph-theory algorithms. The service acts as the main
integration point between controllers, validators, serializers,
algorithm modules, and visualization payload builders.

Supported features include:
    - Graph CRUD operations.
    - Graph algebra and structural transformations.
    - Minimum and maximum spanning trees.
    - Path and shortest-path algorithms.
    - Circuit and cut-set analysis.
    - Coloring, domination, matching, and independence algorithms.
    - Matrix generation utilities.
    - Visualization payload generation.
    - Snapshot export and restoration.

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
along with ComputerScience2. If not, see
<https://www.gnu.org/licenses/>.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional

from app.services.graphs.algorithms.circuits import all_circuits, fundamental_circuits
from app.services.graphs.algorithms.coloring import edge_coloring, vertex_coloring
from app.services.graphs.algorithms.cut_sets import cut_sets as detect_cut_sets
from app.services.graphs.algorithms.cut_sets import fundamental_cut_sets
from app.services.graphs.algorithms.domination import domination
from app.services.graphs.algorithms.floyd_warshall import floyd_warshall
from app.services.graphs.algorithms.independent_sets import independent_sets
from app.services.graphs.algorithms.matching import matching
from app.services.graphs.algorithms.mst import (
	center_or_bicenter,
	maximum_spanning_tree,
	minimum_spanning_tree,
	validate_tree,
)
from app.services.graphs.algorithms.operations import (
	add_edge,
	add_vertex,
	cartesian_product,
	complement_graph,
	composition,
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
from app.services.graphs.algorithms.visualization import (
	build_family_groups,
	build_visualization_payload,
)
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
	"""Provide graph CRUD, algebra, and algorithm operations.

	This service stores graph instances in memory and exposes a unified API
	for graph manipulation, analysis, matrix generation, serialization,
	and visualization payload creation.

	Attributes:
		_graphs (Dict[str, Graph]): In-memory graph registry indexed by
			graph identifier.

	"""

	def __init__(self) -> None:
		"""Initialize in-memory graph registry."""
		self._graphs: Dict[str, Graph] = {}

	def create_graph(self, graph_id: str, directed: bool, weighted: bool) -> Dict[str, Any]:
		"""Create and register a graph.

		Args:
			graph_id (str): Unique graph identifier.
			directed (bool): Whether the graph is directed.
			weighted (bool): Whether the graph supports weighted edges.

		Returns:
			Dict[str, Any]: Serialized graph representation.

		Raises:
			GraphValidationError: If the graph identifier already exists.

		"""
		if graph_id in self._graphs:
			raise GraphValidationError(f"Graph '{graph_id}' already exists")
		self._graphs[graph_id] = Graph(graph_id=graph_id, directed=directed, weighted=weighted)
		return self.get_graph(graph_id)

	def get_graph_model(self, graph_id: str) -> Graph:
		"""Return graph model by identifier.

		Args:
			graph_id (str): Graph identifier.

		Returns:
			Graph: Stored graph model.

		Raises:
			GraphValidationError: If graph does not exist.

		"""
		return ensure_graph_exists(self._graphs.get(graph_id), graph_id)

	def get_graph(self, graph_id: str) -> Dict[str, Any]:
		"""Return serialized graph by identifier.

		Args:
			graph_id (str): Graph identifier.

		Returns:
			Dict[str, Any]: Serialized graph payload.

		"""
		graph = self.get_graph_model(graph_id)
		return self._serialize_graph(graph)

	def list_graphs(self) -> Dict[str, Any]:
		"""Return all registered graphs.

		Returns:
			Dict[str, Any]: Collection of serialized graphs ordered by id.

		"""
		return {
			'graphs': [
				self._serialize_graph(graph)
				for graph in sorted(self._graphs.values(), key=lambda x: x.graph_id)
			]
		}

	def add_vertex(self, graph_id: str, vertex_name: str) -> Dict[str, Any]:
		"""Add a vertex to a graph.

		Args:
			graph_id (str): Graph identifier.
			vertex_name (str): Vertex name.

		Returns:
			Dict[str, Any]: Updated serialized graph.

		Raises:
			GraphValidationError: If vertex already exists or is invalid.

		"""
		graph = self.get_graph_model(graph_id)
		ensure_non_empty_vertices([vertex_name])
		ensure_unique_vertex(graph, vertex_name)
		add_vertex(graph, vertex_name)
		self._refresh_matrices(graph)
		return self._serialize_graph(graph)

	def remove_vertex(self, graph_id: str, vertex_name: str) -> Dict[str, Any]:
		"""Remove a vertex from a graph.

		Also removes all incident edges connected to the vertex.

		Args:
			graph_id (str): Graph identifier.
			vertex_name (str): Vertex to remove.

		Returns:
			Dict[str, Any]: Updated serialized graph.

		Raises:
			GraphValidationError: If vertex does not exist.

		"""
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
		"""Add an edge to a graph.

		Args:
			graph_id (str): Graph identifier.
			edge_name (str): Unique edge name.
			source (str): Source vertex name.
			target (str): Target vertex name.
			directed (Optional[bool]): Edge direction override.
			weight (Optional[float]): Edge weight.

		Returns:
			Dict[str, Any]: Updated serialized graph.

		Raises:
			GraphValidationError: If edge or vertices are invalid.

		"""
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
		"""Remove an edge from a graph.

		Args:
			graph_id (str): Graph identifier.
			edge_name (str): Edge name.

		Returns:
			Dict[str, Any]: Updated serialized graph.

		Raises:
			GraphValidationError: If edge does not exist.

		"""
		graph = self.get_graph_model(graph_id)
		ensure_edge_exists(graph, edge_name)
		remove_edge(graph, edge_name)
		self._refresh_matrices(graph)
		return self._serialize_graph(graph)

	def union(
		self, graph_a_id: str, graph_b_id: str, result_id: str = 'result_graph'
	) -> Dict[str, Any]:
		"""Compute graph union.

		Args:
			graph_a_id (str): Left graph identifier.
			graph_b_id (str): Right graph identifier.
			result_id (str): Result graph identifier.

		Returns:
			Dict[str, Any]: Serialized resulting graph.

		"""
		return self._store_result(
			union_graphs,
			graph_a_id,
			graph_b_id,
			result_id,
		)

	def intersection(
		self, graph_a_id: str, graph_b_id: str, result_id: str = 'result_graph'
	) -> Dict[str, Any]:
		"""Compute graph intersection.

		Args:
			graph_a_id (str): Left graph identifier.
			graph_b_id (str): Right graph identifier.
			result_id (str): Result graph identifier.

		Returns:
			Dict[str, Any]: Serialized resulting graph.

		"""
		return self._store_result(
			intersection_graphs,
			graph_a_id,
			graph_b_id,
			result_id,
		)

	def ring_sum(
		self, graph_a_id: str, graph_b_id: str, result_id: str = 'result_graph'
	) -> Dict[str, Any]:
		"""Compute graph ring sum.

		The ring sum corresponds to the symmetric difference between
		the edge sets of two graphs.

		Args:
			graph_a_id (str): Left graph identifier.
			graph_b_id (str): Right graph identifier.
			result_id (str): Result graph identifier.

		Returns:
			Dict[str, Any]: Serialized resulting graph.

		"""
		return self._store_result(
			ring_sum_graphs,
			graph_a_id,
			graph_b_id,
			result_id,
		)

	def sum(
		self, graph_a_id: str, graph_b_id: str, result_id: str = 'result_graph'
	) -> Dict[str, Any]:
		"""Compute graph sum.

		Args:
			graph_a_id (str): Left graph identifier.
			graph_b_id (str): Right graph identifier.
			result_id (str): Result graph identifier.

		Returns:
			Dict[str, Any]: Serialized resulting graph.

		"""
		return self._store_result(
			sum_graphs,
			graph_a_id,
			graph_b_id,
			result_id,
		)

	def complement(self, graph_id: str, result_id: str = 'result_graph') -> Dict[str, Any]:
		"""Compute graph complement.

		Args:
			graph_id (str): Base graph identifier.
			result_id (str): Result graph identifier.

		Returns:
			Dict[str, Any]: Serialized complement graph.

		"""
		graph = self.get_graph_model(graph_id)
		result = complement_graph(graph, result_id)
		self._finalize_result_graph(result)
		return self._serialize_graph(result)

	def cartesian_product(
		self, graph_a_id: str, graph_b_id: str, result_id: str = 'result_graph'
	) -> Dict[str, Any]:
		"""Compute the cartesian product between two graphs.

		Build a graph where vertices represent ordered pairs of vertices
		from the input graphs and edges follow cartesian adjacency rules.

		Args:
			graph_a_id (str): Identifier of the first graph.
			graph_b_id (str): Identifier of the second graph.
			result_id (str, optional): Identifier of the resulting graph.
				Defaults to ``'result_graph'``.

		Returns:
			Dict[str, Any]: Serialized product graph.

		Raises:
			GraphValidationError: If graphs are incompatible.

		"""
		return self._store_result(
			cartesian_product,
			graph_a_id,
			graph_b_id,
			result_id,
		)

	def tensor_product(
		self, graph_a_id: str, graph_b_id: str, result_id: str = 'result_graph'
	) -> Dict[str, Any]:
		"""Compute the tensor (direct) product of two graphs.

		The tensor product connects vertex pairs only when both original
		graphs contain compatible edges between their corresponding
		vertices.

		Args:
			graph_a_id (str): Identifier of the first graph.
			graph_b_id (str): Identifier of the second graph.
			result_id (str, optional): Identifier of the resulting graph.
				Defaults to ``'result_graph'``.

		Returns:
			Dict[str, Any]: Serialized tensor product graph.

		Raises:
			GraphValidationError: If graphs are incompatible.

		"""
		return self._store_result(
			tensor_product,
			graph_a_id,
			graph_b_id,
			result_id,
		)

	def composition(
		self, graph_a_id: str, graph_b_id: str, result_id: str = 'result_graph'
	) -> Dict[str, Any]:
		"""Compute the composition product of two graphs.

		The composition graph combines internal connections of the second
		graph with adjacency induced by the first graph.

		Args:
			graph_a_id (str): Identifier of the first graph.
			graph_b_id (str): Identifier of the second graph.
			result_id (str, optional): Identifier of the resulting graph.
				Defaults to ``'result_graph'``.

		Returns:
			Dict[str, Any]: Serialized composition graph.

		Raises:
			GraphValidationError: If graphs are incompatible.

		"""
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
		"""Fuse two vertices into a single vertex.

		All incident edges connected to the original vertices are
		redirected to the new fused vertex. Self-loops generated by the
		fusion are removed automatically.

		Args:
			graph_id (str): Identifier of the graph.
			left_vertex (str): First vertex to merge.
			right_vertex (str): Second vertex to merge.
			new_vertex (str): Name of the resulting fused vertex.

		Returns:
			Dict[str, Any]: Serialized updated graph.

		Raises:
			GraphValidationError: If vertices do not exist or the new
				vertex name is already in use.

		"""
		graph = self.get_graph_model(graph_id)
		ensure_vertex_exists(graph, left_vertex)
		ensure_vertex_exists(graph, right_vertex)
		if new_vertex not in (left_vertex, right_vertex):
			ensure_unique_vertex(graph, new_vertex)
		vertex_fusion(graph, left_vertex, right_vertex, new_vertex)
		self._refresh_matrices(graph)
		return self._serialize_graph(graph)

	def edge_contraction(self, graph_id: str, edge_name: str, new_vertex: str) -> Dict[str, Any]:
		"""Contract an edge by merging its endpoint vertices.

		The selected edge is removed and its incident vertices are fused
		into a new vertex.

		Args:
			graph_id (str): Identifier of the graph.
			edge_name (str): Name of the edge to contract.
			new_vertex (str): Name assigned to the merged vertex.

		Returns:
			Dict[str, Any]: Serialized updated graph.

		Raises:
			GraphValidationError: If the edge does not exist or the new
				vertex name is invalid.

		"""
		graph = self.get_graph_model(graph_id)
		ensure_edge_exists(graph, edge_name)
		if new_vertex not in graph.vertices:
			ensure_unique_vertex(graph, new_vertex)
		edge_contraction(graph, edge_name, new_vertex)
		self._refresh_matrices(graph)
		return self._serialize_graph(graph)

	def center(self, graph_id: str) -> Dict[str, Any]:
		"""Compute the center or bicenter of a tree graph.

		The algorithm iteratively removes leaves until one or two central
		vertices remain.

		Args:
			graph_id (str): Identifier of the graph.

		Returns:
			Dict[str, Any]: Dictionary containing center vertices and
			center classification.

		Raises:
			GraphValidationError: If the graph is not a valid tree.

		"""
		graph = self.get_graph_model(graph_id)
		ensure_has_direction(graph)
		result = center_or_bicenter(graph)
		graph.derived['center'] = result
		return result

	def mst(self, graph_id: str) -> Dict[str, Any]:
		"""Compute the minimum spanning tree of a graph.

		The method applies Kruskal's algorithm and generates additional
		structural information such as branches, chords, rank, nullity,
		and visualization payloads.

		Args:
			graph_id (str): Identifier of the graph.

		Returns:
			Dict[str, Any]: MST data and visualization payload.

		Raises:
			GraphValidationError: If the graph is invalid for MST
				computation.

		"""
		graph = self.get_graph_model(graph_id)
		ensure_has_direction(graph)
		result = minimum_spanning_tree(graph)
		groups = build_family_groups('B', [result.branches], 'edges') + build_family_groups(
			'C', [result.chords], 'edges'
		)
		payload = {
			'mst_edges': result.edges,
			'complement_tree_edges': result.complement_edges,
			'branches': result.branches,
			'chords': result.chords,
			'rank': result.rank,
			'nullity': result.nullity,
			'total_weight': result.total_weight,
			'visualization': build_visualization_payload(
				graph,
				highlighted_edges=result.branches,
				groups=groups,
			),
		}
		graph.derived['mst'] = payload
		return payload

	def maximum_spanning_tree(self, graph_id: str) -> Dict[str, Any]:
		"""Compute the maximum spanning tree of a graph.

		The algorithm selects edges that maximize total weight while
		preserving connectivity and avoiding cycles.

		Args:
			graph_id (str): Identifier of the graph.

		Returns:
			Dict[str, Any]: Maximum spanning tree data and visualization.

		Raises:
			GraphValidationError: If the graph is invalid for spanning
				tree computation.

		"""
		graph = self.get_graph_model(graph_id)
		ensure_has_direction(graph)
		result = maximum_spanning_tree(graph)
		groups = build_family_groups('B', [result.branches], 'edges') + build_family_groups(
			'C', [result.chords], 'edges'
		)
		payload = {
			'branches': result.branches,
			'chords': result.chords,
			'rank': result.rank,
			'nullity': result.nullity,
			'total_weight': result.total_weight,
			'visualization': build_visualization_payload(
				graph,
				highlighted_edges=result.branches,
				groups=groups,
			),
		}
		graph.derived['maximum_spanning_tree'] = payload
		return payload

	def tree_distance(self, graph_a_id: str, graph_b_id: str) -> Dict[str, Any]:
		"""Compute weighted distance between two trees.

		The distance is defined as the difference between the sum of
		union edge weights and the sum of intersection edge weights.

		Args:
			graph_a_id (str): Identifier of the first tree.
			graph_b_id (str): Identifier of the second tree.

		Returns:
			Dict[str, Any]: Tree distance metrics and intermediate
			operations.

		Raises:
			GraphValidationError: If any graph is not a valid tree.

		"""
		graph_a = self.get_graph_model(graph_a_id)
		graph_b = self.get_graph_model(graph_b_id)
		validate_tree(graph_a)
		validate_tree(graph_b)
		result = tree_distance(graph_a, graph_b)
		return result

	def ordinal(self, graph_id: str) -> Dict[str, Any]:
		"""Compute ordinal labels for graph vertices.

		The ordinal function performs a direction-aware topological
		traversal and assigns incremental ordinal values to vertices.

		Args:
			graph_id (str): Identifier of the graph.

		Returns:
			Dict[str, Any]: Ordinal mapping and traversal order.

		Raises:
			GraphValidationError: If the graph is not directed or
				contains cycles.

		"""
		graph = self.get_graph_model(graph_id)
		result = ordinal_function(graph)
		graph.derived['ordinal'] = result
		return result

	def bellman(self, graph_id: str, source: str, target: Optional[str] = None) -> Dict[str, Any]:
		"""Compute Bellman lambda values for a directed graph.

		The algorithm evaluates shortest accumulated weights following
		the stored ordinal traversal order.

		Args:
			graph_id (str): Identifier of the graph.
			source (str): Source vertex.
			target (Optional[str], optional): Target vertex used for path
				reconstruction. Defaults to ``None``.

		Returns:
			Dict[str, Any]: Bellman lambda values, intermediate steps,
			and reconstructed path.

		Raises:
			GraphValidationError: If the graph or source vertex is
				invalid.

		"""
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
		"""Compute shortest paths using Dijkstra's algorithm.

		The algorithm computes minimum distances from the source vertex
		and optionally reconstructs the shortest path to a target
		vertex.

		Args:
			graph_id (str): Identifier of the graph.
			source (str): Source vertex.
			target (Optional[str], optional): Target vertex for path
				reconstruction. Defaults to ``None``.

		Returns:
			Dict[str, Any]: Distance data, traversal order,
			reconstructed path, and visualization payload.

		Raises:
			GraphValidationError: If the source vertex does not exist.

		"""
		graph = self.get_graph_model(graph_id)
		result = dijkstra(graph, source, target)
		path_edges = self._path_edges(graph, result.path)
		payload = {
			'source': result.source,
			'target': result.target,
			'pairs': result.pairs,
			'definitive_order': result.definitive_order,
			'distances': result.distances,
			'path': result.path,
			'visualization': build_visualization_payload(
				graph,
				highlighted_vertices=result.path,
				highlighted_edges=path_edges,
				groups=build_family_groups('P', [result.path], 'vertices') if result.path else [],
			),
		}
		graph.derived['dijkstra'] = payload
		return payload

	def floyd_warshall(self, graph_id: str) -> Dict[str, Any]:
		"""Compute all-pairs shortest paths using Floyd-Warshall.

		The algorithm generates distance and predecessor matrices and
		reconstructs shortest paths between all vertex pairs.

		Args:
			graph_id (str): Identifier of the graph.

		Returns:
			Dict[str, Any]: Floyd-Warshall matrices, shortest paths,
			cycle detection information, and visualization payload.

		Raises:
			GraphValidationError: If the graph is not weighted.

		"""
		graph = self.get_graph_model(graph_id)
		result = floyd_warshall(graph)
		groups = []
		for source, targets in result.shortest_paths.items():
			for target, path in targets.items():
				if len(path) >= 2:
					groups.extend(build_family_groups(f'{source}_{target}_', [path], 'vertices'))
		payload = {
			'distance_matrix': result.distance_matrix,
			'predecessor_matrix': result.predecessor_matrix,
			'shortest_paths': result.shortest_paths,
			'paths': result.shortest_paths,
			'negative_cycle_detected': result.negative_cycle_detected,
			'visualization': build_visualization_payload(graph, groups=groups),
		}
		graph.derived['floyd_warshall'] = payload
		return payload

	def circuits(self, graph_id: str) -> Dict[str, Any]:
		"""Detect all graph circuits and generate circuit matrices.

		The method identifies all edge circuits, builds the circuit
		matrix representation, and generates visualization data.

		Args:
			graph_id (str): Identifier of the graph.

		Returns:
			Dict[str, Any]: Circuit families, matrix representation,
			and visualization payload.

		Raises:
			GraphValidationError: If the graph is invalid.

		"""
		graph = self.get_graph_model(graph_id)
		result = all_circuits(graph)
		groups = build_family_groups('C', result.circuits, 'edges')
		payload = {
			'circuits': result.circuits,
			'edge_labels': result.edge_labels,
			'matrix': result.matrix,
			'visualization': build_visualization_payload(
				graph,
				highlighted_edges=sorted({edge for circuit in result.circuits for edge in circuit}),
				groups=groups,
			),
		}
		graph.derived['circuits'] = payload
		return payload

	def fundamental_circuits(self, graph_id: str) -> Dict[str, Any]:
		"""Compute fundamental circuits from a spanning tree.

		Fundamental circuits are generated using the chords of the
		stored minimum spanning tree.

		Args:
			graph_id (str): Identifier of the graph.

		Returns:
			Dict[str, Any]: Fundamental circuits, circuit matrix,
			and visualization payload.

		Raises:
			GraphValidationError: If the graph is invalid for MST
				computation.

		"""
		graph = self.get_graph_model(graph_id)
		mst_data = graph.derived.get('mst')
		if not mst_data:
			mst_data = self.mst(graph_id)
		result = fundamental_circuits(
			graph, mst_data.get('branches', []), mst_data.get('chords', [])
		)
		groups = build_family_groups('CF', result.circuits, 'edges')
		payload = {
			'circuits': result.circuits,
			'edge_labels': result.edge_labels,
			'matrix': result.matrix,
			'visualization': build_visualization_payload(
				graph,
				highlighted_edges=sorted({edge for circuit in result.circuits for edge in circuit}),
				groups=groups,
			),
		}
		graph.derived['fundamental_circuits'] = payload
		return payload

	def cut_sets(self, graph_id: str) -> Dict[str, Any]:
		"""Compute all edge cut sets of a graph.

		The method identifies edge subsets whose removal disconnects
		the graph and builds the corresponding cut matrix.

		Args:
			graph_id (str): Identifier of the graph.

		Returns:
			Dict[str, Any]: Cut-set families, cut matrix,
			disconnecting sets, and visualization payload.

		Raises:
			GraphValidationError: If the graph is invalid.

		"""
		graph = self.get_graph_model(graph_id)
		result = detect_cut_sets(graph)
		groups = build_family_groups('K', result['cut_sets'], 'edges')
		payload = {
			'cut_sets': result['cut_sets'],
			'cut_matrix': result['cut_matrix'],
			'edge_labels': result['edge_labels'],
			'disconnecting_sets': result['disconnecting_sets'],
			'visualization': build_visualization_payload(
				graph,
				highlighted_edges=sorted(
					{edge for cut_set in result['cut_sets'] for edge in cut_set}
				),
				groups=groups,
			),
		}
		graph.derived['cut_sets'] = payload
		return payload

	def fundamental_cut_sets(self, graph_id: str) -> Dict[str, Any]:
		"""Compute fundamental cut sets from the stored MST.

		Fundamental cut sets are generated from the branches of the
		minimum spanning tree and represent minimal disconnecting
		structures.

		Args:
			graph_id (str): Identifier of the graph.

		Returns:
			Dict[str, Any]: Fundamental cut sets, cut matrix,
			branch/chord classification, and visualization payload.

		Raises:
			GraphValidationError: If the graph is invalid for MST
				computation.

		"""
		graph = self.get_graph_model(graph_id)
		mst_data = graph.derived.get('mst')
		if not mst_data:
			mst_data = self.mst(graph_id)
		result = fundamental_cut_sets(graph, mst_data.get('branches', []))
		groups = build_family_groups('FK', result['cut_sets'], 'edges')
		payload = {
			'cut_sets': result['cut_sets'],
			'cut_matrix': result['cut_matrix'],
			'edge_labels': result['edge_labels'],
			'branches': result['branches'],
			'chords': result['chords'],
			'visualization': build_visualization_payload(
				graph,
				highlighted_edges=sorted(
					{edge for cut_set in result['cut_sets'] for edge in cut_set}
				),
				groups=groups,
			),
		}
		graph.derived['fundamental_cut_sets'] = payload
		return payload

	def incidence_matrix(self, graph_id: str) -> Dict[str, Any]:
		"""Return the incidence matrix of a graph.

		The incidence matrix relates vertices and edges according to
		graph direction and connectivity.

		Args:
			graph_id (str): Identifier of the graph.

		Returns:
			Dict[str, Any]: Incidence matrix representation.

		Raises:
			GraphValidationError: If the graph does not exist.

		"""
		graph = self.get_graph_model(graph_id)
		matrix = incidence_matrix(graph)
		graph.derived['matrices'] = graph.derived.get('matrices', {})
		graph.derived['matrices']['incidence'] = matrix
		return matrix

	def vertex_adjacency_matrix(self, graph_id: str) -> Dict[str, Any]:
		"""Return the vertex adjacency matrix of a graph.

		The matrix represents adjacency relations between vertices.

		Args:
			graph_id (str): Identifier of the graph.

		Returns:
			Dict[str, Any]: Vertex adjacency matrix representation.

		Raises:
			GraphValidationError: If the graph does not exist.

		"""
		graph = self.get_graph_model(graph_id)
		matrix = vertex_adjacency_matrix(graph)
		graph.derived['matrices'] = graph.derived.get('matrices', {})
		graph.derived['matrices']['vertex_adjacency'] = matrix
		return matrix

	def edge_adjacency_matrix(self, graph_id: str) -> Dict[str, Any]:
		"""Return the edge adjacency matrix of a graph.

		The matrix represents adjacency relationships between edges.

		Args:
			graph_id (str): Identifier of the graph.

		Returns:
			Dict[str, Any]: Edge adjacency matrix representation.

		Raises:
			GraphValidationError: If the graph does not exist.

		"""
		graph = self.get_graph_model(graph_id)
		matrix = edge_adjacency_matrix(graph)
		graph.derived['matrices'] = graph.derived.get('matrices', {})
		graph.derived['matrices']['edge_adjacency'] = matrix
		return matrix

	def vertex_coloring(self, graph_id: str) -> Dict[str, Any]:
		"""Compute a vertex coloring for the graph.

		The algorithm assigns colors to vertices such that adjacent
		vertices do not share the same color.

		Args:
			graph_id (str): Identifier of the graph.

		Returns:
			Dict[str, Any]: Chromatic number, chromatic classes,
			chromatic polynomial, and visualization payload.

		Raises:
			GraphValidationError: If the graph is invalid.

		"""
		graph = self.get_graph_model(graph_id)
		result = vertex_coloring(graph)
		groups = [
			{
				'name': name,
				'label': f'{name} = {{{", ".join(vertices)}}}' if vertices else f'{name} = {{}}',
				'type': 'vertices_set',
				'vertices': list(vertices),
				'edges': [],
			}
			for name, vertices in result.classes.items()
		]
		payload = {
			'chromatic_number': result.chromatic_number,
			'chromatic_polynomial': result.chromatic_polynomial,
			'chromatic_classes': result.classes,
			'visualization': build_visualization_payload(
				graph,
				highlighted_vertices=sorted(
					{vertex for vertices in result.classes.values() for vertex in vertices}
				),
				groups=groups,
			),
		}
		graph.derived['vertex_coloring'] = payload
		return payload

	def edge_coloring(self, graph_id: str) -> Dict[str, Any]:
		"""Compute an edge coloring for the graph.

		The algorithm assigns colors to edges such that adjacent edges
		do not share the same color.

		Args:
			graph_id (str): Identifier of the graph.

		Returns:
			Dict[str, Any]: Chromatic index, edge chromatic classes,
			and visualization payload.

		Raises:
			GraphValidationError: If the graph is invalid.

		"""
		graph = self.get_graph_model(graph_id)
		result = edge_coloring(graph)
		groups = [
			{
				'name': name,
				'label': f'{name} = {{{", ".join(edges)}}}' if edges else f'{name} = {{}}',
				'type': 'edges_set',
				'vertices': [],
				'edges': list(edges),
			}
			for name, edges in result.edge_classes.items()
		]
		payload = {
			'chromatic_index': result.chromatic_index,
			'edge_chromatic_classes': result.edge_classes,
			'visualization': build_visualization_payload(
				graph,
				highlighted_edges=sorted(
					{edge for edges in result.edge_classes.values() for edge in edges}
				),
				groups=groups,
			),
		}
		graph.derived['edge_coloring'] = payload
		return payload

	def independent_sets(self, graph_id: str) -> Dict[str, Any]:
		"""Compute independent-set families and related metrics.

		The method identifies all independent sets, maximal independent
		sets, and maximum independent sets of the graph.

		Args:
			graph_id (str): Identifier of the graph.

		Returns:
			Dict[str, Any]: Independent-set families, independence
			number, and visualization payload.

		Raises:
			GraphValidationError: If the graph is invalid.

		"""
		graph = self.get_graph_model(graph_id)
		result = independent_sets(graph)
		groups = build_family_groups('I', result.maximum_sets, 'vertices')
		payload = {
			'all_independent_sets': result.all_sets,
			'independence_number': result.independence_number,
			'maximum_independent_sets': result.maximum_sets,
			'maximal_independent_sets': result.maximal_sets,
			'visualization': build_visualization_payload(
				graph,
				highlighted_vertices=sorted(
					{vertex for family in result.maximum_sets for vertex in family}
				),
				groups=groups,
			),
		}
		graph.derived['independent_sets'] = payload
		return payload

	def domination(self, graph_id: str) -> Dict[str, Any]:
		"""Compute dominating-set families and domination number.

		The method identifies all dominating sets, minimum dominating
		sets, and independent dominating sets of the graph.

		Args:
			graph_id (str): Identifier of the graph.

		Returns:
			Dict[str, Any]: Domination metrics, dominating-set families,
			and visualization payload.

		Raises:
			GraphValidationError: If the graph is invalid.

		"""
		graph = self.get_graph_model(graph_id)
		result = domination(graph)
		groups = (
			build_family_groups('D', result.dominating_sets, 'vertices')
			+ build_family_groups('MD', result.minimum_dominating_sets, 'vertices')
			+ build_family_groups('ID', result.independent_dominating_sets, 'vertices')
		)
		payload = {
			'domination_number': result.domination_number,
			'dominating_sets': result.dominating_sets,
			'minimum_dominating_sets': result.minimum_dominating_sets,
			'independent_dominating_sets': result.independent_dominating_sets,
			'visualization': build_visualization_payload(
				graph,
				highlighted_vertices=sorted(
					{vertex for family in result.minimum_dominating_sets for vertex in family}
				),
				groups=groups,
			),
		}
		graph.derived['domination'] = payload
		return payload

	def matching(self, graph_id: str) -> Dict[str, Any]:
		"""Compute matching families and matching number.

		The method identifies all matchings, maximal matchings, and
		maximum matchings of the graph.

		Args:
			graph_id (str): Identifier of the graph.

		Returns:
			Dict[str, Any]: Matching families, matching number,
			and visualization payload.

		Raises:
			GraphValidationError: If the graph is invalid.

		"""
		graph = self.get_graph_model(graph_id)
		result = matching(graph)
		groups = build_family_groups('M', result.matchings, 'edges')
		payload = {
			'matchings': result.matchings,
			'maximal_matchings': result.maximal_matchings,
			'maximum_matchings': result.maximum_matchings,
			'matching_number': result.matching_number,
			'visualization': build_visualization_payload(
				graph,
				highlighted_edges=sorted(
					{edge for family in result.maximum_matchings for edge in family}
				),
				groups=groups,
			),
		}
		graph.derived['matching'] = payload
		return payload

	def _path_edges(self, graph: Graph, path: List[str]) -> List[str]:
		"""Return edge names corresponding to a vertex path.

		The method searches graph edges that connect consecutive
		vertices of the provided path sequence.

		Args:
			graph (Graph): Graph containing the path.
			path (List[str]): Ordered vertex path.

		Returns:
			List[str]: Edge names associated with the path.

		"""
		edge_names: List[str] = []
		for left, right in zip(path, path[1:]):
			matching_edges = [
				edge.name
				for edge in graph.edges.values()
				if (edge.source == left and edge.target == right)
				or (not edge.directed and edge.source == right and edge.target == left)
			]
			if matching_edges:
				edge_names.append(sorted(matching_edges)[0])
		return edge_names

	def validate_snapshot(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
		"""Validate a serialized graph snapshot.

		The validation ensures that the snapshot structure, version,
		and graph payloads are correct before restoration.

		Args:
			snapshot (Dict[str, Any]): Snapshot payload to validate.

		Returns:
			Dict[str, Any]: Validated snapshot payload.

		Raises:
			GraphSnapshotError: If the snapshot format is invalid.

		"""
		return validate_snapshot(snapshot)

	def to_snapshot(self) -> Dict[str, Any]:
		"""Export all registered graphs into a snapshot.

		The snapshot includes graph structures, derived metadata,
		and serializer version information.

		Returns:
			Dict[str, Any]: Serialized snapshot containing all graphs.

		"""
		return to_snapshot(self._graphs.values())

	def from_snapshot(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
		"""Restore the graph registry from a snapshot.

		The method recreates all stored graphs and refreshes dynamic
		matrix representations after restoration.

		Args:
			snapshot (Dict[str, Any]): Snapshot payload.

		Returns:
			Dict[str, Any]: Serialized list of restored graphs.

		Raises:
			GraphSnapshotError: If the snapshot format is invalid.

		"""
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
		"""Execute and store the result of a binary graph operation.

		Retrieve two compatible graphs, execute the provided graph
		operation, refresh all derived matrix representations, store the
		result graph in the registry, and return its serialized form.

		Args:
			operation: Binary graph operation function receiving two graphs
				and a result identifier.
			graph_a_id (str): Identifier of the first graph.
			graph_b_id (str): Identifier of the second graph.
			result_id (str): Identifier assigned to the resulting graph.

		Returns:
			Dict[str, Any]: Serialized result graph.

		Raises:
			GraphValidationError: If graphs are incompatible or do not
				exist.

		"""
		graph_a = self.get_graph_model(graph_a_id)
		graph_b = self.get_graph_model(graph_b_id)
		ensure_graph_compatibility(graph_a, graph_b)
		result = operation(graph_a, graph_b, result_id)
		self._finalize_result_graph(result)
		return self._serialize_graph(result)

	def _finalize_result_graph(self, graph: Graph) -> None:
		"""Persist a generated graph and refresh derived structures.

		Update all matrix representations associated with the graph and
		store the graph inside the internal registry.

		Args:
			graph (Graph): Graph produced by an operation or algorithm.

		"""
		self._refresh_matrices(graph)
		self._graphs[graph.graph_id] = graph

	def _refresh_matrices(self, graph: Graph) -> None:
		"""Recompute all matrix representations for a graph.

		Generate incidence, vertex adjacency, and edge adjacency matrices
		and store them inside the graph derived state.

		Args:
			graph (Graph): Graph whose matrix representations will be
				recomputed.

		"""
		graph.derived['matrices'] = {
			'incidence': incidence_matrix(graph),
			'vertex_adjacency': vertex_adjacency_matrix(graph),
			'edge_adjacency': edge_adjacency_matrix(graph),
		}

	def _serialize_graph(self, graph: Graph) -> Dict[str, Any]:
		"""Serialize a graph using the snapshot serializer.

		Export the graph into snapshot format and return a detached deep
		copy of the serialized graph payload to avoid accidental mutation
		of internal state.

		Args:
			graph (Graph): Graph to serialize.

		Returns:
			Dict[str, Any]: Serialized graph payload.

		"""
		snapshot = to_snapshot([graph])
		graph_payload = snapshot['state']['graphs'][0]
		return deepcopy(graph_payload)
