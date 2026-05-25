"""Domain models for graph structures and derived results.

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

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(slots=True)
class Vertex:
	"""Represent a vertex in a graph.

	Attributes:
		name (str): Unique vertex identifier.
		ordinal (Optional[int]): Optional ordinal label.

	"""

	name: str
	ordinal: Optional[int] = None


@dataclass(slots=True)
class Edge:
	"""Represent an edge in a graph.

	Attributes:
		name (str): Unique edge identifier.
		source (str): Source vertex name.
		target (str): Target vertex name.
		directed (bool): Whether edge direction is active.
		weight (Optional[float]): Optional edge weight.

	"""

	name: str
	source: str
	target: str
	directed: bool
	weight: Optional[float] = None


@dataclass(slots=True)
class MSTResult:
	"""Store minimum spanning tree data."""

	edges: List[str] = field(default_factory=list)
	complement_edges: List[str] = field(default_factory=list)
	branches: List[str] = field(default_factory=list)
	chords: List[str] = field(default_factory=list)
	rank: int = 0
	nullity: int = 0
	total_weight: float = 0.0


@dataclass(slots=True)
class PathResult:
	"""Store shortest-path algorithm data."""

	source: str
	target: Optional[str]
	distances: Dict[str, float] = field(default_factory=dict)
	path: List[str] = field(default_factory=list)
	steps: List[Dict[str, Any]] = field(default_factory=list)


@dataclass(slots=True)
class BellmanResult:
	"""Store Bellman lambda calculations."""

	source: str
	target: Optional[str]
	lambda_values: Dict[str, float] = field(default_factory=dict)
	intermediate_steps: List[str] = field(default_factory=list)
	path: List[str] = field(default_factory=list)


@dataclass(slots=True)
class DijkstraResult:
	"""Store Dijkstra result and trace."""

	source: str
	target: Optional[str]
	pairs: List[List[Any]] = field(default_factory=list)
	definitive_order: List[str] = field(default_factory=list)
	distances: Dict[str, float] = field(default_factory=dict)
	path: List[str] = field(default_factory=list)


@dataclass(slots=True)
class CircuitResult:
	"""Store cycle sets and matrix representations."""

	circuits: List[List[str]] = field(default_factory=list)
	matrix: List[List[int]] = field(default_factory=list)
	edge_labels: List[str] = field(default_factory=list)


@dataclass(slots=True)
class ColoringResult:
	"""Store coloring metrics and classes."""

	chromatic_number: int = 0
	chromatic_polynomial: str = ''
	classes: Dict[str, List[str]] = field(default_factory=dict)
	chromatic_index: int = 0
	edge_classes: Dict[str, List[str]] = field(default_factory=dict)


@dataclass(slots=True)
class IndependentSetsResult:
	"""Store independent set families and metrics."""

	all_sets: List[List[str]] = field(default_factory=list)
	independence_number: int = 0
	maximum_sets: List[List[str]] = field(default_factory=list)
	maximal_sets: List[List[str]] = field(default_factory=list)


@dataclass(slots=True)
class TreeDistanceResult:
	"""Store weighted tree-distance operation outputs."""

	union_edges: List[str] = field(default_factory=list)
	intersection_edges: List[str] = field(default_factory=list)
	union_weight_sum: float = 0.0
	intersection_weight_sum: float = 0.0
	distance: float = 0.0
	operations: List[str] = field(default_factory=list)


@dataclass(slots=True)
class Graph:
	"""Represent a graph and all derived structures.

	Attributes:
		graph_id (str): Graph identifier.
		directed (bool): Graph orientation flag.
		weighted (bool): Graph weighted flag.
		vertices (Dict[str, Vertex]): Vertex registry by name.
		edges (Dict[str, Edge]): Edge registry by name.
		derived (Dict[str, Any]): Derived and computed structures.

	"""

	graph_id: str
	directed: bool
	weighted: bool
	vertices: Dict[str, Vertex] = field(default_factory=dict)
	edges: Dict[str, Edge] = field(default_factory=dict)
	derived: Dict[str, Any] = field(default_factory=dict)
