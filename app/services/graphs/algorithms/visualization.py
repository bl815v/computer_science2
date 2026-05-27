"""Reusable visualization payload builders for graph algorithms.

Author: Juan Esteban Bedoya <jebedoyal@udistrital.edu.co>
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from app.services.graphs.algorithms.shared import sorted_edges, sorted_vertices
from app.services.graphs.models import Graph

_PALETTE = [
	'#2563eb',
	'#16a34a',
	'#dc2626',
	'#d97706',
	'#7c3aed',
	'#0f766e',
	'#be185d',
	'#4f46e5',
]


def _normalize_names(values: Iterable[str] | None) -> List[str]:
	"""Return sorted unique names from an iterable."""
	return sorted({value for value in (values or []) if value is not None})


def build_family_groups(
	prefix: str,
	families: List[List[str]],
	member_type: str,
	color_palette: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
	"""Build labeled groups for a family of subsets."""
	palette = color_palette or _PALETTE
	groups: List[Dict[str, Any]] = []
	for index, family in enumerate(families, start=1):
		members = _normalize_names(family)
		group_name = f'{prefix}{index}'
		group_color = palette[(index - 1) % len(palette)]
		group: Dict[str, Any] = {
			'name': group_name,
			'label': f"{group_name} = {{{', '.join(members)}}}" if members else f'{group_name} = {{}}',
			'type': f'{member_type}_set',
			'color': group_color,
			'vertices': members if member_type == 'vertices' else [],
			'edges': members if member_type == 'edges' else [],
		}
		groups.append(group)
	return groups


def build_visualization_payload(
	graph: Graph,
	highlighted_vertices: Iterable[str] | None = None,
	highlighted_edges: Iterable[str] | None = None,
	groups: Optional[List[Dict[str, Any]]] = None,
	labels: Optional[Dict[str, Any]] = None,
	colors: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
	"""Build a standard visualization payload for graph algorithms."""
	highlighted_vertices_list = _normalize_names(highlighted_vertices)
	highlighted_edges_list = _normalize_names(highlighted_edges)
	vertex_label_map = {name: name for name in sorted_vertices(graph)}
	edge_label_map = {name: name for name in sorted_edges(graph)}
	vertex_colors = (colors or {}).get('vertices', {}) if isinstance(colors, dict) else {}
	edge_colors = (colors or {}).get('edges', {}) if isinstance(colors, dict) else {}

	vertex_entries: List[Dict[str, Any]] = []
	for name in sorted_vertices(graph):
		vertex_entries.append(
			{
				'name': name,
				'label': vertex_label_map.get(name, name),
				'highlighted': name in highlighted_vertices_list,
				'color': vertex_colors.get(name),
			}
		)

	edge_entries: List[Dict[str, Any]] = []
	for name in sorted_edges(graph):
		edge = graph.edges[name]
		edge_entries.append(
			{
				'name': edge.name,
				'source': edge.source,
				'target': edge.target,
				'directed': edge.directed,
				'weight': edge.weight,
				'label': edge_label_map.get(name, name),
				'highlighted': name in highlighted_edges_list,
				'color': edge_colors.get(name),
			}
		)

	group_payloads: List[Dict[str, Any]] = []
	group_labels: Dict[str, str] = {}
	for group in groups or []:
		group_name = str(group.get('name', 'group'))
		group_label = str(group.get('label', group_name))
		group_labels[group_name] = group_label
		group_payloads.append(
			{
				'name': group_name,
				'label': group_label,
				'type': group.get('type'),
				'color': group.get('color'),
				'vertices': _normalize_names(group.get('vertices')),
				'edges': _normalize_names(group.get('edges')),
			}
		)

	payload: Dict[str, Any] = {
		'vertices': vertex_entries,
		'edges': edge_entries,
		'highlighted_vertices': highlighted_vertices_list,
		'highlighted_edges': highlighted_edges_list,
		'groups': group_payloads,
		'labels': {
			'vertices': vertex_label_map,
			'edges': edge_label_map,
			'groups': group_labels,
		},
	}

	if labels:
		payload['labels'].update(labels)
	if colors:
		payload['colors'] = colors

	return payload
