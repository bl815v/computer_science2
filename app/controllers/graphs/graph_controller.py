"""Expose REST API endpoints for graph operations and algorithms.

Author: Juan Esteban Bedoya <jebedoyal@udistrital.edu.co>
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
	"""Raise standardized HTTP errors for graph routes."""
	if isinstance(exc, (GraphValidationError, GraphSnapshotError, ValueError)):
		raise HTTPException(status_code=400, detail=str(exc))
	raise HTTPException(status_code=500, detail=str(exc))


@router.get('/state')
def list_graphs() -> dict:
	"""List all graphs currently stored in memory."""
	return service.list_graphs()


@router.post('/create')
def create_graph(request: GraphCreateRequest) -> dict:
	"""Create a new graph in the service registry."""
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
	"""Add a vertex to the selected graph."""
	try:
		return service.add_vertex(graph_id, request.name)
	except Exception as exc:
		_handle_error(exc)


@router.delete('/{graph_id}/vertex/{name}')
def remove_vertex(graph_id: str, name: str) -> dict:
	"""Remove a vertex and incident edges from graph."""
	try:
		return service.remove_vertex(graph_id, name)
	except Exception as exc:
		_handle_error(exc)


@router.post('/{graph_id}/edge')
def add_edge(graph_id: str, request: EdgeRequest) -> dict:
	"""Add an edge to graph."""
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
	"""Remove an edge from graph."""
	try:
		return service.remove_edge(graph_id, name)
	except Exception as exc:
		_handle_error(exc)


@router.post('/union')
def union(request: BinaryOperationRequest) -> dict:
	"""Compute union of two graphs."""
	try:
		return service.union(request.graph_a_id, request.graph_b_id, request.result_id)
	except Exception as exc:
		_handle_error(exc)


@router.post('/intersection')
def intersection(request: BinaryOperationRequest) -> dict:
	"""Compute intersection of two graphs."""
	try:
		return service.intersection(request.graph_a_id, request.graph_b_id, request.result_id)
	except Exception as exc:
		_handle_error(exc)


@router.post('/ring-sum')
def ring_sum(request: BinaryOperationRequest) -> dict:
	"""Compute ring sum of two graphs."""
	try:
		return service.ring_sum(request.graph_a_id, request.graph_b_id, request.result_id)
	except Exception as exc:
		_handle_error(exc)


@router.post('/sum')
def sum_graph(request: BinaryOperationRequest) -> dict:
	"""Compute sum of two graphs."""
	try:
		return service.sum(request.graph_a_id, request.graph_b_id, request.result_id)
	except Exception as exc:
		_handle_error(exc)


@router.post('/complement')
def complement(request: UnaryOperationRequest) -> dict:
	"""Compute complement of one graph."""
	try:
		return service.complement(request.graph_id, request.result_id)
	except Exception as exc:
		_handle_error(exc)


@router.post('/cartesian-product')
def cartesian_product_endpoint(request: BinaryOperationRequest) -> dict:
	"""Compute cartesian product of two graphs."""
	try:
		return service.cartesian_product(request.graph_a_id, request.graph_b_id, request.result_id)
	except Exception as exc:
		_handle_error(exc)


@router.post('/tensor-product')
def tensor_product_endpoint(request: BinaryOperationRequest) -> dict:
	"""Compute tensor product of two graphs."""
	try:
		return service.tensor_product(request.graph_a_id, request.graph_b_id, request.result_id)
	except Exception as exc:
		_handle_error(exc)


@router.post('/composition')
def composition_endpoint(request: BinaryOperationRequest) -> dict:
	"""Compute composition of two graphs."""
	try:
		return service.composition(request.graph_a_id, request.graph_b_id, request.result_id)
	except Exception as exc:
		_handle_error(exc)


@router.post('/{graph_id}/vertex-fusion')
def vertex_fusion_endpoint(graph_id: str, request: VertexFusionRequest) -> dict:
	"""Fuse two vertices into one."""
	try:
		return service.vertex_fusion(graph_id, request.left_vertex, request.right_vertex, request.new_vertex)
	except Exception as exc:
		_handle_error(exc)


@router.post('/{graph_id}/edge-contraction')
def edge_contraction_endpoint(graph_id: str, request: EdgeContractionRequest) -> dict:
	"""Contract edge endpoints into one vertex."""
	try:
		return service.edge_contraction(graph_id, request.edge_name, request.new_vertex)
	except Exception as exc:
		_handle_error(exc)


@router.post('/{graph_id}/mst')
def mst(graph_id: str) -> dict:
	"""Compute minimum spanning tree and its complement."""
	try:
		return service.mst(graph_id)
	except Exception as exc:
		_handle_error(exc)


@router.post('/{graph_id}/maximum-spanning-tree')
def maximum_spanning_tree(graph_id: str) -> dict:
	"""Compute maximum spanning tree and its complement."""
	try:
		return service.maximum_spanning_tree(graph_id)
	except Exception as exc:
		_handle_error(exc)


@router.post('/{graph_id}/center')
def center(graph_id: str) -> dict:
	"""Compute center or bicenter of a tree."""
	try:
		return service.center(graph_id)
	except Exception as exc:
		_handle_error(exc)


@router.post('/tree-distance')
def tree_distance_endpoint(request: TreeDistanceRequest) -> dict:
	"""Compute weighted tree distance between two graphs."""
	try:
		return service.tree_distance(request.graph_a_id, request.graph_b_id)
	except Exception as exc:
		_handle_error(exc)


@router.post('/{graph_id}/ordinal')
def ordinal(graph_id: str) -> dict:
	"""Compute ordinal function over directed graph."""
	try:
		return service.ordinal(graph_id)
	except Exception as exc:
		_handle_error(exc)


@router.post('/{graph_id}/bellman')
def bellman(graph_id: str, request: PathRequest) -> dict:
	"""Compute Bellman lambda values."""
	try:
		return service.bellman(graph_id, request.source, request.target)
	except Exception as exc:
		_handle_error(exc)


@router.post('/{graph_id}/dijkstra')
def dijkstra(graph_id: str, request: PathRequest) -> dict:
	"""Compute Dijkstra shortest paths."""
	try:
		return service.dijkstra(graph_id, request.source, request.target)
	except Exception as exc:
		_handle_error(exc)


@router.post('/{graph_id}/floyd-warshall')
def floyd_warshall(graph_id: str) -> dict:
	"""Compute Floyd-Warshall all-pairs shortest paths."""
	try:
		return service.floyd_warshall(graph_id)
	except Exception as exc:
		_handle_error(exc)


@router.post('/{graph_id}/circuits')
def circuits(graph_id: str) -> dict:
	"""Detect all circuits and build matrix."""
	try:
		return service.circuits(graph_id)
	except Exception as exc:
		_handle_error(exc)


@router.post('/{graph_id}/cut-sets')
def cut_sets(graph_id: str) -> dict:
	"""Detect cut sets and build matrix."""
	try:
		return service.cut_sets(graph_id)
	except Exception as exc:
		_handle_error(exc)


@router.post('/{graph_id}/fundamental-circuits')
def fundamental_circuits_endpoint(graph_id: str) -> dict:
	"""Compute fundamental circuits from MST structure."""
	try:
		return service.fundamental_circuits(graph_id)
	except Exception as exc:
		_handle_error(exc)


@router.post('/{graph_id}/fundamental-cut-sets')
def fundamental_cut_sets_endpoint(graph_id: str) -> dict:
	"""Compute fundamental cut sets from MST structure."""
	try:
		return service.fundamental_cut_sets(graph_id)
	except Exception as exc:
		_handle_error(exc)


@router.post('/{graph_id}/domination')
def domination_endpoint(graph_id: str) -> dict:
	"""Compute dominating-set families and domination number."""
	try:
		return service.domination(graph_id)
	except Exception as exc:
		_handle_error(exc)


@router.post('/{graph_id}/matching')
def matching_endpoint(graph_id: str) -> dict:
	"""Compute matching families and matching number."""
	try:
		return service.matching(graph_id)
	except Exception as exc:
		_handle_error(exc)


@router.get('/{graph_id}/matrices/incidence')
def incidence(graph_id: str) -> dict:
	"""Return incidence matrix."""
	try:
		return service.incidence_matrix(graph_id)
	except Exception as exc:
		_handle_error(exc)


@router.get('/{graph_id}/matrices/vertex-adjacency')
def vertex_adjacency(graph_id: str) -> dict:
	"""Return vertex adjacency matrix."""
	try:
		return service.vertex_adjacency_matrix(graph_id)
	except Exception as exc:
		_handle_error(exc)


@router.get('/{graph_id}/matrices/edge-adjacency')
def edge_adjacency(graph_id: str) -> dict:
	"""Return edge adjacency matrix."""
	try:
		return service.edge_adjacency_matrix(graph_id)
	except Exception as exc:
		_handle_error(exc)


@router.post('/{graph_id}/vertex-coloring')
def vertex_coloring_endpoint(graph_id: str) -> dict:
	"""Compute vertex coloring and chromatic information."""
	try:
		return service.vertex_coloring(graph_id)
	except Exception as exc:
		_handle_error(exc)


@router.post('/{graph_id}/edge-coloring')
def edge_coloring_endpoint(graph_id: str) -> dict:
	"""Compute edge coloring and chromatic index."""
	try:
		return service.edge_coloring(graph_id)
	except Exception as exc:
		_handle_error(exc)


@router.post('/{graph_id}/independent-sets')
def independent_sets_endpoint(graph_id: str) -> dict:
	"""Compute independent sets and associated metrics."""
	try:
		return service.independent_sets(graph_id)
	except Exception as exc:
		_handle_error(exc)


@router.post('/export')
def export_graphs() -> dict:
	"""Export all graphs as a versioned snapshot."""
	return service.to_snapshot()


@router.post('/import')
def import_graphs(request: SnapshotRequest) -> dict:
	"""Import all graphs from versioned snapshot."""
	try:
		service.validate_snapshot(request.snapshot)
		return service.from_snapshot(request.snapshot)
	except Exception as exc:
		_handle_error(exc)
