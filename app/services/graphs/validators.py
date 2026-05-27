"""Validation helpers for graph services.

Provide reusable validation utilities for graph operations, graph
integrity checks, and algorithm preconditions. Includes helpers for
validating vertices, edges, graph compatibility, weights, and general
graph state consistency.

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

from typing import Iterable

from app.services.graphs.models import Edge, Graph


class GraphValidationError(ValueError):
	"""Raise when graph state or operation inputs are invalid.

	This exception is used across graph services and algorithms to signal
	invalid graph configurations, inconsistent operations, or missing
	required graph elements.
	"""


def ensure_graph_exists(graph: Graph | None, graph_id: str) -> Graph:
	"""Ensure that a graph instance exists.

	Args:
		graph (Graph | None): Graph instance to validate.
		graph_id (str): Expected graph identifier.

	Returns:
		Graph: Validated graph instance.

	Raises:
		GraphValidationError: If the graph does not exist.

	"""
	if graph is None:
		raise GraphValidationError(f"Graph '{graph_id}' does not exist")
	return graph


def ensure_unique_vertex(graph: Graph, vertex_name: str) -> None:
	"""Ensure that a vertex name is unique within a graph.

	Args:
		graph (Graph): Target graph.
		vertex_name (str): Vertex identifier to validate.

	Raises:
		GraphValidationError: If the vertex already exists.

	"""
	if vertex_name in graph.vertices:
		raise GraphValidationError(f"Vertex '{vertex_name}' already exists")


def ensure_vertex_exists(graph: Graph, vertex_name: str) -> None:
	"""Ensure that a vertex exists in a graph.

	Args:
		graph (Graph): Target graph.
		vertex_name (str): Vertex identifier to validate.

	Raises:
		GraphValidationError: If the vertex does not exist.

	"""
	if vertex_name not in graph.vertices:
		raise GraphValidationError(f"Vertex '{vertex_name}' does not exist")


def ensure_unique_edge(graph: Graph, edge_name: str) -> None:
	"""Ensure that an edge name is unique within a graph.

	Args:
		graph (Graph): Target graph.
		edge_name (str): Edge identifier to validate.

	Raises:
		GraphValidationError: If the edge already exists.

	"""
	if edge_name in graph.edges:
		raise GraphValidationError(f"Edge '{edge_name}' already exists")


def ensure_edge_exists(graph: Graph, edge_name: str) -> Edge:
	"""Ensure that an edge exists in a graph.

	Args:
		graph (Graph): Target graph.
		edge_name (str): Edge identifier to validate.

	Returns:
		Edge: Validated edge instance.

	Raises:
		GraphValidationError: If the edge does not exist.

	"""
	edge = graph.edges.get(edge_name)
	if edge is None:
		raise GraphValidationError(f"Edge '{edge_name}' does not exist")
	return edge


def ensure_weight(value: float | None, weighted: bool, edge_name: str) -> None:
	"""Ensure edge weight consistency with graph configuration.

	Args:
		value (float | None): Edge weight value.
		weighted (bool): Whether the graph requires weights.
		edge_name (str): Edge identifier.

	Raises:
		GraphValidationError: If a weighted graph receives an edge
			without weight information.

	"""
	if weighted and value is None:
		raise GraphValidationError(f"Missing weight for edge '{edge_name}' in weighted graph")


def ensure_graph_compatibility(graph_a: Graph, graph_b: Graph) -> None:
	"""Ensure compatibility between two graphs.

	Graphs are considered compatible when they share the same
	directionality and weight configuration.

	Args:
		graph_a (Graph): First graph.
		graph_b (Graph): Second graph.

	Raises:
		GraphValidationError: If graph configurations differ.

	"""
	if graph_a.directed != graph_b.directed:
		raise GraphValidationError('Graph direction compatibility mismatch')
	if graph_a.weighted != graph_b.weighted:
		raise GraphValidationError('Graph weight compatibility mismatch')


def ensure_has_direction(graph: Graph) -> None:
	"""Ensure that graph direction metadata is defined.

	Args:
		graph (Graph): Graph to validate.

	Raises:
		GraphValidationError: If graph direction metadata is missing.

	"""
	if graph.directed is None:
		raise GraphValidationError('Graph direction is missing')


def ensure_weights_for_algorithm(graph: Graph, operation_name: str) -> None:
	"""Ensure a graph supports weighted algorithms.

	Args:
		graph (Graph): Graph to validate.
		operation_name (str): Algorithm or operation name.

	Raises:
		GraphValidationError: If the graph is not weighted.

	"""
	if not graph.weighted:
		raise GraphValidationError(f'{operation_name} requires weighted edges')


def ensure_non_empty_vertices(vertex_names: Iterable[str]) -> None:
	"""Ensure all provided vertex names are non-empty.

	Args:
		vertex_names (Iterable[str]): Vertex names to validate.

	Raises:
		GraphValidationError: If at least one vertex name is empty
			or contains only whitespace.

	"""
	for name in vertex_names:
		if not name or not str(name).strip():
			raise GraphValidationError('Vertex name must be a non-empty string')
