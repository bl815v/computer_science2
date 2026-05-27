"""Expose REST API endpoints for graph operations and algorithms.

This module defines the FastAPI routes used to interact with graph
structures and graph algorithms provided by the application.

The router acts as the HTTP interface layer between client requests
and the internal `GraphService`. It exposes endpoints for:

    - Graph creation and deletion operations.
    - Vertex and edge manipulation.
    - Binary and unary graph operations.
    - Graph products and compositions.
    - Tree and shortest-path algorithms.
    - Matrix generation.
    - Circuit and cut-set analysis.
    - Coloring and combinatorial algorithms.
    - Snapshot export/import persistence.

All endpoints delegate business logic to `GraphService` and use
centralized error handling through `_handle_error()`.

Author: Juan Esteban Bedoya <jebedoyal@udistrital.edu.co>

This file is part of ComputerScience2 project.

ComputerScience2 is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version.

ComputerScience2 is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with ComputerScience2. If not, see <https://www.gnu.org/licenses/>.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.controllers.graphs.schemas import (
	BinaryOperationRequest,
	EdgeContractionRequest,
	EdgeRequest,
	GraphCreateRequest,
	PathRequest,
	SnapshotRequest,
	TreeDistanceRequest,
	UnaryOperationRequest,
	VertexFusionRequest,
	VertexRequest,
)
from app.services.graphs.graph_service import GraphService
from app.services.graphs.serializer import GraphSnapshotError
from app.services.graphs.validators import GraphValidationError

router = APIRouter(prefix='/graphs', tags=['Graphs'])
service = GraphService()


def _handle_error(exc: Exception) -> None:
	"""
	Raise standardized HTTP exceptions for graph endpoints.

	Map domain-specific validation and snapshot errors to HTTP 400
	responses. Unexpected exceptions are returned as HTTP 500 errors.

	Args:
		exc (Exception):
			Original exception raised during route execution.

	Raises:
		HTTPException:
			FastAPI-compatible HTTP exception.

	"""
	if isinstance(exc, (GraphValidationError, GraphSnapshotError, ValueError)):
		raise HTTPException(status_code=400, detail=str(exc))
	raise HTTPException(status_code=500, detail=str(exc))


@router.get('/state')
def list_graphs() -> dict:
	"""
	List all graphs currently stored in memory.

	Returns:
		dict:
			Dictionary containing the registered graphs and metadata.

	"""
	return service.list_graphs()


@router.post('/create')
def create_graph(request: GraphCreateRequest) -> dict:
	"""
	Create and register a new graph.

	Args:
		request (GraphCreateRequest):
			Graph creation parameters.

	Returns:
		dict:
			Information about the created graph.

	"""
	try:
		return service.create_graph(
			graph_id=request.graph_id,
			directed=request.directed,
			weighted=request.weighted,
		)
	except Exception as exc:
		_handle_error(exc)


@router.post('/{graph_id}/vertex')
def add_vertex(graph_id: str, request: VertexRequest) -> dict:
	"""
	Add a vertex to a graph.

	Args:
		graph_id (str):
			Identifier of the target graph.

		request (VertexRequest):
			Vertex insertion payload.

	Returns:
		dict:
			Operation result information.

	"""
	try:
		return service.add_vertex(graph_id, request.name)
	except Exception as exc:
		_handle_error(exc)


@router.delete('/{graph_id}/vertex/{name}')
def remove_vertex(graph_id: str, name: str) -> dict:
	"""
	Remove a vertex and all incident edges from a graph.

	Args:
		graph_id (str):
			Identifier of the graph.

		name (str):
			Vertex name.

	Returns:
		dict:
			Operation result information.

	"""
	try:
		return service.remove_vertex(graph_id, name)
	except Exception as exc:
		_handle_error(exc)


@router.post('/{graph_id}/edge')
def add_edge(graph_id: str, request: EdgeRequest) -> dict:
	"""
	Add an edge to a graph.

	Args:
		graph_id (str):
			Target graph identifier.

		request (EdgeRequest):
			Edge definition payload.

	Returns:
		dict:
			Operation result information.

	"""
	try:
		return service.add_edge(
			graph_id=graph_id,
			edge_name=request.name,
			source=request.source,
			target=request.target,
			directed=request.directed,
			weight=request.weight,
		)
	except Exception as exc:
		_handle_error(exc)


@router.delete('/{graph_id}/edge/{name}')
def remove_edge(graph_id: str, name: str) -> dict:
	"""
	Remove an edge from a graph.

	Args:
		graph_id (str):
			Graph identifier.

		name (str):
			Edge identifier.

	Returns:
		dict:
			Operation result information.

	"""
	try:
		return service.remove_edge(graph_id, name)
	except Exception as exc:
		_handle_error(exc)


@router.post('/union')
def union(request: BinaryOperationRequest) -> dict:
	"""
	Compute the union of two graphs.

	Args:
		request (BinaryOperationRequest):
			Binary operation parameters.

	Returns:
		dict:
			Resulting graph information.

	"""
	try:
		return service.union(request.graph_a_id, request.graph_b_id, request.result_id)
	except Exception as exc:
		_handle_error(exc)


@router.post('/intersection')
def intersection(request: BinaryOperationRequest) -> dict:
	"""
	Compute the intersection of two graphs.

	Args:
		request (BinaryOperationRequest):
			Binary operation parameters.

	Returns:
		dict:
			Result graph information.

	"""
	try:
		return service.intersection(request.graph_a_id, request.graph_b_id, request.result_id)
	except Exception as exc:
		_handle_error(exc)


@router.post('/ring-sum')
def ring_sum(request: BinaryOperationRequest) -> dict:
	"""
	Compute the ring sum (symmetric difference) of two graphs.

	Args:
		request (BinaryOperationRequest):
			Binary operation parameters.

	Returns:
		dict:
			Result graph information.

	"""
	try:
		return service.ring_sum(request.graph_a_id, request.graph_b_id, request.result_id)
	except Exception as exc:
		_handle_error(exc)


@router.post('/sum')
def sum_graph(request: BinaryOperationRequest) -> dict:
	"""
	Compute the graph sum of two graphs.

	Args:
		request (BinaryOperationRequest):
			Binary operation parameters.

	Returns:
		dict:
			Result graph information.

	"""
	try:
		return service.sum(request.graph_a_id, request.graph_b_id, request.result_id)
	except Exception as exc:
		_handle_error(exc)


@router.post('/complement')
def complement(request: UnaryOperationRequest) -> dict:
	"""
	Compute the complement of a graph.

	Args:
		request (UnaryOperationRequest):
			Unary operation parameters.

	Returns:
		dict:
			Result graph information.

	"""
	try:
		return service.complement(request.graph_id, request.result_id)
	except Exception as exc:
		_handle_error(exc)


@router.post('/cartesian-product')
def cartesian_product_endpoint(request: BinaryOperationRequest) -> dict:
	"""
	Compute the cartesian product of two graphs.

	Args:
		request (BinaryOperationRequest):
			Product operation parameters.

	Returns:
		dict:
			Result graph information.

	"""
	try:
		return service.cartesian_product(request.graph_a_id, request.graph_b_id, request.result_id)
	except Exception as exc:
		_handle_error(exc)


@router.post('/tensor-product')
def tensor_product_endpoint(request: BinaryOperationRequest) -> dict:
	"""
	Compute the tensor product of two graphs.

	Args:
		request (BinaryOperationRequest):
			Product operation parameters.

	Returns:
		dict:
			Result graph information.

	"""
	try:
		return service.tensor_product(request.graph_a_id, request.graph_b_id, request.result_id)
	except Exception as exc:
		_handle_error(exc)


@router.post('/composition')
def composition_endpoint(request: BinaryOperationRequest) -> dict:
	"""
	Compute the composition of two graphs.

	Args:
		request (BinaryOperationRequest):
			Composition parameters.

	Returns:
		dict:
			Result graph information.

	"""
	try:
		return service.composition(request.graph_a_id, request.graph_b_id, request.result_id)
	except Exception as exc:
		_handle_error(exc)


@router.post('/{graph_id}/vertex-fusion')
def vertex_fusion_endpoint(graph_id: str, request: VertexFusionRequest) -> dict:
	"""
	Fuse two vertices into a single vertex.

	Args:
		graph_id (str):
			Graph identifier.

		request (VertexFusionRequest):
			Vertex fusion parameters.

	Returns:
		dict:
			Operation result information.

	"""
	try:
		return service.vertex_fusion(
			graph_id, request.left_vertex, request.right_vertex, request.new_vertex
		)
	except Exception as exc:
		_handle_error(exc)


@router.post('/{graph_id}/edge-contraction')
def edge_contraction_endpoint(graph_id: str, request: EdgeContractionRequest) -> dict:
	"""
	Contract an edge into a single vertex.

	Args:
		graph_id (str):
			Graph identifier.

		request (EdgeContractionRequest):
			Contraction parameters.

	Returns:
		dict:
			Operation result information.

	"""
	try:
		return service.edge_contraction(graph_id, request.edge_name, request.new_vertex)
	except Exception as exc:
		_handle_error(exc)


@router.post('/{graph_id}/mst')
def mst(graph_id: str) -> dict:
	"""
	Compute the minimum spanning tree of a graph.

	Args:
		graph_id (str):
			Graph identifier.

	Returns:
		dict:
			MST information and complement graph.

	"""
	try:
		return service.mst(graph_id)
	except Exception as exc:
		_handle_error(exc)


@router.post('/{graph_id}/maximum-spanning-tree')
def maximum_spanning_tree(graph_id: str) -> dict:
	"""
	Compute the maximum spanning tree of a graph.

	Args:
		graph_id (str):
			Graph identifier.

	Returns:
		dict:
			Maximum spanning tree information.

	"""
	try:
		return service.maximum_spanning_tree(graph_id)
	except Exception as exc:
		_handle_error(exc)


@router.post('/{graph_id}/center')
def center(graph_id: str) -> dict:
	"""
	Compute the center or bicenter of a tree.

	Args:
		graph_id (str):
			Tree graph identifier.

	Returns:
		dict:
			Tree center information.

	"""
	try:
		return service.center(graph_id)
	except Exception as exc:
		_handle_error(exc)


@router.post('/tree-distance')
def tree_distance_endpoint(request: TreeDistanceRequest) -> dict:
	"""
	Compute weighted distance between two trees.

	Args:
		request (TreeDistanceRequest):
			Tree comparison parameters.

	Returns:
		dict:
			Distance metrics.

	"""
	try:
		return service.tree_distance(request.graph_a_id, request.graph_b_id)
	except Exception as exc:
		_handle_error(exc)


@router.post('/{graph_id}/ordinal')
def ordinal(graph_id: str) -> dict:
	"""
	Compute ordinal values for a directed graph.

	Args:
		graph_id (str):
			Graph identifier.

	Returns:
		dict:
			Ordinal analysis results.

	"""
	try:
		return service.ordinal(graph_id)
	except Exception as exc:
		_handle_error(exc)


@router.post('/{graph_id}/bellman')
def bellman(graph_id: str, request: PathRequest) -> dict:
	"""
	Compute Bellman shortest-path values.

	Args:
		graph_id (str):
			Graph identifier.

		request (PathRequest):
			Path query parameters.

	Returns:
		dict:
			Shortest-path information.

	"""
	try:
		return service.bellman(graph_id, request.source, request.target)
	except Exception as exc:
		_handle_error(exc)


@router.post('/{graph_id}/dijkstra')
def dijkstra(graph_id: str, request: PathRequest) -> dict:
	"""
	Compute Dijkstra shortest paths.

	Args:
		graph_id (str):
			Graph identifier.

		request (PathRequest):
			Path query parameters.

	Returns:
		dict:
			Shortest-path information.

	"""
	try:
		return service.dijkstra(graph_id, request.source, request.target)
	except Exception as exc:
		_handle_error(exc)


@router.post('/{graph_id}/floyd-warshall')
def floyd_warshall(graph_id: str) -> dict:
	"""
	Compute Floyd-Warshall all-pairs shortest paths.

	Args:
		graph_id (str):
			Graph identifier.

	Returns:
		dict:
			Distance matrix and path information.

	"""
	try:
		return service.floyd_warshall(graph_id)
	except Exception as exc:
		_handle_error(exc)


@router.post('/{graph_id}/circuits')
def circuits(graph_id: str) -> dict:
	"""
	Detect graph circuits and generate the circuit matrix.

	Args:
		graph_id (str):
			Graph identifier.

	Returns:
		dict:
			Circuit information and matrices.

	"""
	try:
		return service.circuits(graph_id)
	except Exception as exc:
		_handle_error(exc)


@router.post('/{graph_id}/cut-sets')
def cut_sets(graph_id: str) -> dict:
	"""
	Detect cut sets and generate the cut-set matrix.

	Args:
		graph_id (str):
			Graph identifier.

	Returns:
		dict:
			Cut-set information and matrices.

	"""
	try:
		return service.cut_sets(graph_id)
	except Exception as exc:
		_handle_error(exc)


@router.post('/{graph_id}/fundamental-circuits')
def fundamental_circuits_endpoint(graph_id: str) -> dict:
	"""
	Compute fundamental circuits using the MST structure.

	Args:
		graph_id (str):
			Graph identifier.

	Returns:
		dict:
			Fundamental circuit information.

	"""
	try:
		return service.fundamental_circuits(graph_id)
	except Exception as exc:
		_handle_error(exc)


@router.post('/{graph_id}/fundamental-cut-sets')
def fundamental_cut_sets_endpoint(graph_id: str) -> dict:
	"""
	Compute fundamental cut sets using the MST structure.

	Args:
		graph_id (str):
			Graph identifier.

	Returns:
		dict:
			Fundamental cut-set information.

	"""
	try:
		return service.fundamental_cut_sets(graph_id)
	except Exception as exc:
		_handle_error(exc)


@router.post('/{graph_id}/domination')
def domination_endpoint(graph_id: str) -> dict:
	"""
	Compute dominating sets and domination number.

	Args:
		graph_id (str):
			Graph identifier.

	Returns:
		dict:
			Domination analysis results.

	"""
	try:
		return service.domination(graph_id)
	except Exception as exc:
		_handle_error(exc)


@router.post('/{graph_id}/matching')
def matching_endpoint(graph_id: str) -> dict:
	"""
	Compute graph matchings and matching number.

	Args:
		graph_id (str):
			Graph identifier.

	Returns:
		dict:
			Matching analysis results.

	"""
	try:
		return service.matching(graph_id)
	except Exception as exc:
		_handle_error(exc)


@router.get('/{graph_id}/matrices/incidence')
def incidence(graph_id: str) -> dict:
	"""
	Return the incidence matrix of a graph.

	Args:
		graph_id (str):
			Graph identifier.

	Returns:
		dict:
			Incidence matrix representation.

	"""
	try:
		return service.incidence_matrix(graph_id)
	except Exception as exc:
		_handle_error(exc)


@router.get('/{graph_id}/matrices/vertex-adjacency')
def vertex_adjacency(graph_id: str) -> dict:
	"""
	Return the vertex adjacency matrix of a graph.

	Args:
		graph_id (str):
			Graph identifier.

	Returns:
		dict:
			Adjacency matrix representation.

	"""
	try:
		return service.vertex_adjacency_matrix(graph_id)
	except Exception as exc:
		_handle_error(exc)


@router.get('/{graph_id}/matrices/edge-adjacency')
def edge_adjacency(graph_id: str) -> dict:
	"""
	Return the edge adjacency matrix of a graph.

	Args:
		graph_id (str):
			Graph identifier.

	Returns:
		dict:
			Edge adjacency matrix representation.

	"""
	try:
		return service.edge_adjacency_matrix(graph_id)
	except Exception as exc:
		_handle_error(exc)


@router.post('/{graph_id}/vertex-coloring')
def vertex_coloring_endpoint(graph_id: str) -> dict:
	"""
	Compute vertex coloring and chromatic number.

	Args:
		graph_id (str):
			Graph identifier.

	Returns:
		dict:
			Vertex coloring information.

	"""
	try:
		return service.vertex_coloring(graph_id)
	except Exception as exc:
		_handle_error(exc)


@router.post('/{graph_id}/edge-coloring')
def edge_coloring_endpoint(graph_id: str) -> dict:
	"""
	Compute edge coloring and chromatic index.

	Args:
		graph_id (str):
			Graph identifier.

	Returns:
		dict:
			Edge coloring information.

	"""
	try:
		return service.edge_coloring(graph_id)
	except Exception as exc:
		_handle_error(exc)


@router.post('/{graph_id}/independent-sets')
def independent_sets_endpoint(graph_id: str) -> dict:
	"""
	Compute independent sets and related metrics.

	Args:
		graph_id (str):
			Graph identifier.

	Returns:
		dict:
			Independent-set analysis information.

	"""
	try:
		return service.independent_sets(graph_id)
	except Exception as exc:
		_handle_error(exc)


@router.post('/export')
def export_graphs() -> dict:
	"""
	Export all graphs into a versioned snapshot.

	Returns:
		dict:
			Serialized snapshot containing all stored graphs.

	"""
	return service.to_snapshot()


@router.post('/import')
def import_graphs(request: SnapshotRequest) -> dict:
	"""
	Import graphs from a versioned snapshot.

	Args:
		request (SnapshotRequest):
			Snapshot payload to restore.

	Returns:
		dict:
			Import operation result.

	"""
	try:
		service.validate_snapshot(request.snapshot)
		return service.from_snapshot(request.snapshot)
	except Exception as exc:
		_handle_error(exc)
