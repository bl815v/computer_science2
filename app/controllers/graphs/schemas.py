"""Pydantic request schemas for graph endpoints.

Author: Juan Esteban Bedoya <jebedoyal@udistrital.edu.co>
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class GraphCreateRequest(BaseModel):
	"""Represent graph creation payload."""

	graph_id: str = Field(..., min_length=1)
	directed: bool = True
	weighted: bool = False


class VertexRequest(BaseModel):
	"""Represent vertex operation payload."""

	name: str = Field(..., min_length=1)


class EdgeRequest(BaseModel):
	"""Represent edge creation payload."""

	name: str = Field(..., min_length=1)
	source: str = Field(..., min_length=1)
	target: str = Field(..., min_length=1)
	directed: Optional[bool] = None
	weight: Optional[float] = None


class BinaryOperationRequest(BaseModel):
	"""Represent two-graph operation payload."""

	graph_a_id: str = Field(..., min_length=1)
	graph_b_id: str = Field(..., min_length=1)
	result_id: str = 'result_graph'


class UnaryOperationRequest(BaseModel):
	"""Represent one-graph operation payload."""

	graph_id: str = Field(..., min_length=1)
	result_id: str = 'result_graph'


class VertexFusionRequest(BaseModel):
	"""Represent vertex-fusion payload."""

	left_vertex: str = Field(..., min_length=1)
	right_vertex: str = Field(..., min_length=1)
	new_vertex: str = Field(..., min_length=1)


class EdgeContractionRequest(BaseModel):
	"""Represent edge contraction payload."""

	edge_name: str = Field(..., min_length=1)
	new_vertex: str = Field(..., min_length=1)


class PathRequest(BaseModel):
	"""Represent path algorithm payload."""

	source: str = Field(..., min_length=1)
	target: Optional[str] = None


class TreeDistanceRequest(BaseModel):
	"""Represent tree distance payload."""

	graph_a_id: str = Field(..., min_length=1)
	graph_b_id: str = Field(..., min_length=1)


class SnapshotRequest(BaseModel):
	"""Represent import snapshot payload."""

	snapshot: Dict[str, Any]
