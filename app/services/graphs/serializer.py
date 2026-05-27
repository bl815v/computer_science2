"""Serialization and snapshot helpers for graph structures.

Provide serialization utilities for graph persistence, snapshot export,
and snapshot restoration. Includes validation helpers for snapshot
envelopes, conversion utilities for dataclasses, and deterministic graph
serialization to ensure reproducible graph storage and recovery.

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
from dataclasses import asdict, is_dataclass
from typing import Any, Dict, Iterable, List

from app.services.graphs.models import Edge, Graph, Vertex

SNAPSHOT_TYPE = 'graph'
SNAPSHOT_VERSION = 2
SUPPORTED_SNAPSHOT_VERSIONS = {1, 2}


class GraphSnapshotError(ValueError):
	"""Raise when a graph snapshot is invalid or incompatible.

	This exception is used during serialization and deserialization
	operations when snapshot payloads are malformed, unsupported,
	or inconsistent with the expected graph structure.
	"""


def _to_plain(value: Any) -> Any:
	"""Convert complex structures into JSON-compatible values.

	Recursively transforms dataclasses, dictionaries, tuples, and lists
	into plain Python structures suitable for serialization.

	Args:
		value (Any): Input value to normalize.

	Returns:
		Any: JSON-compatible representation of the input value.

	"""
	if is_dataclass(value):
		return _to_plain(asdict(value))
	if isinstance(value, dict):
		return {str(k): _to_plain(v) for k, v in value.items()}
	if isinstance(value, list):
		return [_to_plain(item) for item in value]
	if isinstance(value, tuple):
		return [_to_plain(item) for item in value]
	return value


def validate_snapshot(snapshot: Any) -> Dict[str, Any]:
	"""Validate graph snapshot envelope structure.

	Check snapshot type, version compatibility, and required structural
	fields before deserialization.

	Args:
		snapshot (Any): Snapshot payload to validate.

	Returns:
		Dict[str, Any]: Validated snapshot dictionary.

	Raises:
		GraphSnapshotError: If the snapshot structure is invalid,
			corrupted, or unsupported.

	"""
	if not isinstance(snapshot, dict):
		raise GraphSnapshotError('Snapshot must be a JSON object')

	if snapshot.get('type') != SNAPSHOT_TYPE:
		raise GraphSnapshotError(
			f'Snapshot type mismatch: expected {SNAPSHOT_TYPE}, got {snapshot.get("type")}'
		)

	if snapshot.get('version') not in SUPPORTED_SNAPSHOT_VERSIONS:
		raise GraphSnapshotError(f'Unsupported snapshot version: {snapshot.get("version")}')

	config = snapshot.get('config')
	state = snapshot.get('state')
	if not isinstance(config, dict) or not isinstance(state, dict):
		raise GraphSnapshotError('Snapshot is corrupt: config and state must be objects')

	if 'graphs' not in state or not isinstance(state.get('graphs'), list):
		raise GraphSnapshotError('Snapshot state must include graphs list')

	return snapshot


def _edge_sort_key(edge: Edge) -> tuple[str, str, str, int]:
	"""Build deterministic sorting key for edges.

	The generated key guarantees stable serialization ordering across
	snapshot generations.

	Args:
		edge (Edge): Edge instance to normalize.

	Returns:
		tuple[str, str, str, int]: Stable sorting tuple.

	"""
	return (edge.name, edge.source, edge.target, 1 if edge.directed else 0)


def serialize_graph(graph: Graph) -> Dict[str, Any]:
	"""Serialize a graph into a JSON-compatible dictionary.

	Convert graph vertices, edges, and derived structures into a stable
	and deterministic representation suitable for persistence.

	Args:
		graph (Graph): Graph instance to serialize.

	Returns:
		Dict[str, Any]: Serialized graph payload.

	"""
	vertices = [
		{'name': name, 'ordinal': graph.vertices[name].ordinal} for name in sorted(graph.vertices)
	]
	edges = [
		{
			'name': edge.name,
			'source': edge.source,
			'target': edge.target,
			'directed': edge.directed,
			'weight': edge.weight,
		}
		for edge in sorted(graph.edges.values(), key=_edge_sort_key)
	]
	return {
		'graph_id': graph.graph_id,
		'directed': graph.directed,
		'weighted': graph.weighted,
		'vertices': vertices,
		'edges': edges,
		'derived': _to_plain(deepcopy(graph.derived)),
	}


def deserialize_graph(payload: Dict[str, Any]) -> Graph:
	"""Deserialize payload into a graph model.

	Restore graph vertices, edges, and derived structures from a
	serialized dictionary representation.

	Args:
		payload (Dict[str, Any]): Serialized graph payload.

	Returns:
		Graph: Reconstructed graph model.

	Raises:
		GraphSnapshotError: If the payload contains invalid graph data
			or inconsistent references.

	"""
	graph_id = payload.get('graph_id')
	directed = bool(payload.get('directed', False))
	weighted = bool(payload.get('weighted', False))

	if not isinstance(graph_id, str) or not graph_id:
		raise GraphSnapshotError('Graph id must be a non-empty string')

	graph = Graph(graph_id=graph_id, directed=directed, weighted=weighted)

	for vertex_payload in payload.get('vertices', []):
		name = vertex_payload.get('name')
		if not isinstance(name, str) or not name:
			raise GraphSnapshotError('Vertex name must be a non-empty string')
		graph.vertices[name] = Vertex(name=name, ordinal=vertex_payload.get('ordinal'))

	for edge_payload in payload.get('edges', []):
		edge_name = edge_payload.get('name')
		source = edge_payload.get('source')
		target = edge_payload.get('target')
		if not isinstance(edge_name, str) or not edge_name:
			raise GraphSnapshotError('Edge name must be a non-empty string')
		if source not in graph.vertices or target not in graph.vertices:
			raise GraphSnapshotError(f"Edge '{edge_name}' references unknown vertices")
		graph.edges[edge_name] = Edge(
			name=edge_name,
			source=source,
			target=target,
			directed=bool(edge_payload.get('directed', directed)),
			weight=edge_payload.get('weight'),
		)

	graph.derived = deepcopy(payload.get('derived', {}))
	return graph


def to_snapshot(graphs: Iterable[Graph]) -> Dict[str, Any]:
	"""Build a versioned snapshot from graph collections.

	Serialize all provided graphs into a snapshot envelope containing
	metadata, configuration, and graph state information.

	Args:
		graphs (Iterable[Graph]): Collection of graphs to serialize.

	Returns:
		Dict[str, Any]: Snapshot envelope ready for persistence.

	"""
	serialized_graphs = [
		serialize_graph(graph) for graph in sorted(graphs, key=lambda x: x.graph_id)
	]
	return {
		'type': SNAPSHOT_TYPE,
		'version': SNAPSHOT_VERSION,
		'config': {'count': len(serialized_graphs)},
		'state': {'graphs': serialized_graphs},
	}


def from_snapshot(snapshot: Dict[str, Any]) -> List[Graph]:
	"""Restore graph models from a snapshot envelope.

	Validate snapshot metadata and reconstruct all stored graph models.

	Args:
		snapshot (Dict[str, Any]): Snapshot envelope.

	Returns:
		List[Graph]: Reconstructed graph instances.

	Raises:
		GraphSnapshotError: If the snapshot is invalid or incompatible.

	"""
	payload = validate_snapshot(snapshot)
	graphs_payload = payload['state'].get('graphs', [])
	return [deserialize_graph(item) for item in graphs_payload]
