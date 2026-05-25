"""Validation helpers for graph services.

Author: Juan Esteban Bedoya <jebedoyal@udistrital.edu.co>
"""

from __future__ import annotations

from typing import Iterable

from app.services.graphs.models import Edge, Graph


class GraphValidationError(ValueError):
	"""Raised when graph state or operation inputs are invalid."""


def ensure_graph_exists(graph: Graph | None, graph_id: str) -> Graph:
	"""Ensure a graph exists.

	Args:
		graph (Graph | None): Graph instance.
		graph_id (str): Expected graph identifier.

	Returns:
		Graph: The validated graph instance.

	Raises:
		GraphValidationError: If graph does not exist.

	"""
	if graph is None:
		raise GraphValidationError(f"Graph '{graph_id}' does not exist")
	return graph


def ensure_unique_vertex(graph: Graph, vertex_name: str) -> None:
	"""Ensure a vertex name is unique in the graph."""
	if vertex_name in graph.vertices:
		raise GraphValidationError(f"Vertex '{vertex_name}' already exists")


def ensure_vertex_exists(graph: Graph, vertex_name: str) -> None:
	"""Ensure a vertex exists in the graph."""
	if vertex_name not in graph.vertices:
		raise GraphValidationError(f"Vertex '{vertex_name}' does not exist")


def ensure_unique_edge(graph: Graph, edge_name: str) -> None:
	"""Ensure an edge name is unique in the graph."""
	if edge_name in graph.edges:
		raise GraphValidationError(f"Edge '{edge_name}' already exists")


def ensure_edge_exists(graph: Graph, edge_name: str) -> Edge:
	"""Ensure an edge exists in the graph and return it."""
	edge = graph.edges.get(edge_name)
	if edge is None:
		raise GraphValidationError(f"Edge '{edge_name}' does not exist")
	return edge


def ensure_weight(value: float | None, weighted: bool, edge_name: str) -> None:
	"""Ensure edge weight consistency with graph mode."""
	if weighted and value is None:
		raise GraphValidationError(
			f"Missing weight for edge '{edge_name}' in weighted graph"
		)


def ensure_graph_compatibility(graph_a: Graph, graph_b: Graph) -> None:
	"""Ensure graph compatibility for binary operations."""
	if graph_a.directed != graph_b.directed:
		raise GraphValidationError('Graph direction compatibility mismatch')
	if graph_a.weighted != graph_b.weighted:
		raise GraphValidationError('Graph weight compatibility mismatch')


def ensure_has_direction(graph: Graph) -> None:
	"""Ensure direction metadata is defined.

	Raises:
		GraphValidationError: If direction metadata is missing.

	"""
	if graph.directed is None:
		raise GraphValidationError('Graph direction is missing')


def ensure_weights_for_algorithm(graph: Graph, operation_name: str) -> None:
	"""Ensure graph has effective weights for weighted algorithms."""
	if not graph.weighted:
		raise GraphValidationError(f'{operation_name} requires weighted edges')


def ensure_non_empty_vertices(vertex_names: Iterable[str]) -> None:
	"""Ensure no empty vertex names are present."""
	for name in vertex_names:
		if not name or not str(name).strip():
			raise GraphValidationError('Vertex name must be a non-empty string')
