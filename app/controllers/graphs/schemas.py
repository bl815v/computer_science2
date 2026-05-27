"""Pydantic request schemas for graph endpoints.

Define all request payload models used by the graph REST API.
These schemas validate incoming JSON bodies for graph creation,
vertex and edge operations, graph transformations, path algorithms,
tree metrics, and snapshot import/export functionality.

The module uses Pydantic models to ensure type safety and enforce
basic validation constraints before requests reach the controller
and service layers.

Classes:
	GraphCreateRequest:
		Request schema used to create a graph.

	VertexRequest:
		Request schema used for vertex operations.

	EdgeRequest:
		Request schema used for edge operations.

	BinaryOperationRequest:
		Request schema used for operations involving two graphs.

	UnaryOperationRequest:
		Request schema used for operations involving one graph.

	VertexFusionRequest:
		Request schema used for vertex fusion operations.

	EdgeContractionRequest:
		Request schema used for edge contraction operations.

	PathRequest:
		Request schema used for shortest-path algorithms.

	TreeDistanceRequest:
		Request schema used for tree distance calculations.

	SnapshotRequest:
		Request schema used for graph snapshot import operations.

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

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class GraphCreateRequest(BaseModel):
	"""Represent the payload used to create a graph.

	Attributes:
		graph_id (str):
			Unique identifier assigned to the graph.

		directed (bool):
			Indicate whether the graph is directed.

		weighted (bool):
			Indicate whether the graph supports weighted edges.

	"""

	graph_id: str = Field(..., min_length=1)
	directed: bool = True
	weighted: bool = False


class VertexRequest(BaseModel):
	"""Represent the payload used for vertex operations.

	Attributes:
		name (str):
			Name or identifier of the vertex.

	"""

	name: str = Field(..., min_length=1)


class EdgeRequest(BaseModel):
	"""Represent the payload used to create an edge.

	Attributes:
		name (str):
			Unique identifier assigned to the edge.

		source (str):
			Source vertex identifier.

		target (str):
			Target vertex identifier.

		directed (Optional[bool]):
			Optional edge direction override.

		weight (Optional[float]):
			Optional edge weight value.

	"""

	name: str = Field(..., min_length=1)
	source: str = Field(..., min_length=1)
	target: str = Field(..., min_length=1)
	directed: Optional[bool] = None
	weight: Optional[float] = None


class BinaryOperationRequest(BaseModel):
	"""Represent the payload for operations involving two graphs.

	Used for operations such as union, intersection,
	ring sum, cartesian product, tensor product,
	and graph composition.

	Attributes:
		graph_a_id (str):
			Identifier of the first graph.

		graph_b_id (str):
			Identifier of the second graph.

		result_id (str):
			Identifier assigned to the resulting graph.

	"""

	graph_a_id: str = Field(..., min_length=1)
	graph_b_id: str = Field(..., min_length=1)
	result_id: str = 'result_graph'


class UnaryOperationRequest(BaseModel):
	"""Represent the payload for operations involving one graph.

	Used for operations such as graph complement.

	Attributes:
		graph_id (str):
			Identifier of the input graph.

		result_id (str):
			Identifier assigned to the resulting graph.

	"""

	graph_id: str = Field(..., min_length=1)
	result_id: str = 'result_graph'


class VertexFusionRequest(BaseModel):
	"""Represent the payload used for vertex fusion operations.

	Attributes:
		left_vertex (str):
			Identifier of the first vertex to merge.

		right_vertex (str):
			Identifier of the second vertex to merge.

		new_vertex (str):
			Identifier assigned to the resulting fused vertex.

	"""

	left_vertex: str = Field(..., min_length=1)
	right_vertex: str = Field(..., min_length=1)
	new_vertex: str = Field(..., min_length=1)


class EdgeContractionRequest(BaseModel):
	"""Represent the payload used for edge contraction operations.

	Attributes:
		edge_name (str):
			Identifier of the edge to contract.

		new_vertex (str):
			Identifier assigned to the resulting contracted vertex.

	"""

	edge_name: str = Field(..., min_length=1)
	new_vertex: str = Field(..., min_length=1)


class PathRequest(BaseModel):
	"""Represent the payload used for path algorithms.

	Used by shortest-path and path-related algorithms
	such as Dijkstra and Bellman.

	Attributes:
		source (str):
			Starting vertex identifier.

		target (Optional[str]):
			Optional destination vertex identifier.

	"""

	source: str = Field(..., min_length=1)
	target: Optional[str] = None


class TreeDistanceRequest(BaseModel):
	"""Represent the payload used for tree distance calculations.

	Attributes:
		graph_a_id (str):
			Identifier of the first tree graph.

		graph_b_id (str):
			Identifier of the second tree graph.

	"""

	graph_a_id: str = Field(..., min_length=1)
	graph_b_id: str = Field(..., min_length=1)


class SnapshotRequest(BaseModel):
	"""Represent the payload used for graph snapshot imports.

	Attributes:
		snapshot (Dict[str, Any]):
			Versioned snapshot object containing exported
			graph state and configuration data.

	"""

	snapshot: Dict[str, Any]
