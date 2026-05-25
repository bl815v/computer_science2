"""Serialization and snapshot helpers for graph structures.

Author: Juan Esteban Bedoya <jebedoyal@udistrital.edu.co>
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, is_dataclass
from typing import Any, Dict, Iterable, List

from app.services.graphs.models import Edge, Graph, Vertex

SNAPSHOT_TYPE = 'graph'
SNAPSHOT_VERSION = 1


class GraphSnapshotError(ValueError):
	"""Raised when a graph snapshot is invalid or incompatible."""


def _to_plain(value: Any) -> Any:
	"""Convert dataclasses recursively to JSON-compatible structures."""
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
	"""Validate graph snapshot envelope.

	Args:
		snapshot (Any): Snapshot payload.

	Returns:
		Dict[str, Any]: Normalized snapshot object.

	Raises:
		GraphSnapshotError: If snapshot is malformed.

	"""
	if not isinstance(snapshot, dict):
		raise GraphSnapshotError('Snapshot must be a JSON object')

	if snapshot.get('type') != SNAPSHOT_TYPE:
		raise GraphSnapshotError(
			f"Snapshot type mismatch: expected {SNAPSHOT_TYPE}, got {snapshot.get('type')}"
		)

	if snapshot.get('version') != SNAPSHOT_VERSION:
		raise GraphSnapshotError(
			f"Unsupported snapshot version: {snapshot.get('version')}"
		)

	config = snapshot.get('config')
	state = snapshot.get('state')
	if not isinstance(config, dict) or not isinstance(state, dict):
		raise GraphSnapshotError('Snapshot is corrupt: config and state must be objects')

	if 'graphs' not in state or not isinstance(state.get('graphs'), list):
		raise GraphSnapshotError('Snapshot state must include graphs list')

	return snapshot


def _edge_sort_key(edge: Edge) -> tuple[str, str, str, int]:
	"""Build stable sorting key for edge serialization."""
	return (edge.name, edge.source, edge.target, 1 if edge.directed else 0)


def serialize_graph(graph: Graph) -> Dict[str, Any]:
	"""Serialize a graph into a stable JSON-compatible dictionary."""
	vertices = [
		{'name': name, 'ordinal': graph.vertices[name].ordinal}
		for name in sorted(graph.vertices)
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
	"""Deserialize graph payload into a Graph model."""
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
			raise GraphSnapshotError(
				f"Edge '{edge_name}' references unknown vertices"
			)
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
	"""Build versioned snapshot for a collection of graphs.

	Args:
		graphs (Iterable[Graph]): Graph collection.

	Returns:
		Dict[str, Any]: Snapshot envelope.

	"""
	serialized_graphs = [serialize_graph(graph) for graph in sorted(graphs, key=lambda x: x.graph_id)]
	return {
		'type': SNAPSHOT_TYPE,
		'version': SNAPSHOT_VERSION,
		'config': {'count': len(serialized_graphs)},
		'state': {'graphs': serialized_graphs},
	}


def from_snapshot(snapshot: Dict[str, Any]) -> List[Graph]:
	"""Restore graph list from snapshot.

	Args:
		snapshot (Dict[str, Any]): Snapshot envelope.

	Returns:
		List[Graph]: Reconstructed graph list.

	"""
	payload = validate_snapshot(snapshot)
	graphs_payload = payload['state'].get('graphs', [])
	return [deserialize_graph(item) for item in graphs_payload]
