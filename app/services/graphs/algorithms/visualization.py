"""Reusable visualization payload builders for graph algorithms.

Provide standardized visualization payload generators used by graph
algorithms and frontend rendering layers. Includes helpers for
highlighting vertices and edges, grouping graph families, and attaching
labels and colors to visualization structures.

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
	"""Normalize a collection of names into a sorted unique list.

	None values are ignored and duplicates are removed to ensure stable
	and deterministic visualization payloads.

	Args:
		values (Iterable[str] | None): Collection of names.

	Returns:
		List[str]: Sorted list of unique valid names.

	"""
	return sorted({value for value in (values or []) if value is not None})


def build_family_groups(
	prefix: str,
	families: List[List[str]],
	member_type: str,
	color_palette: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
	"""Build visualization groups for graph family structures.

	This helper generates labeled and colorized groups representing
	families of vertices or edges, such as dominating sets,
	independent sets, circuits, or matchings.

	Args:
		prefix (str): Prefix used for generated group names.
		families (List[List[str]]): Collection of family members.
		member_type (str): Either ``'vertices'`` or ``'edges'``.
		color_palette (Optional[List[str]]): Optional custom color
			palette for generated groups.

	Returns:
		List[Dict[str, Any]]: Visualization-ready group payloads.

	"""
	palette = color_palette or _PALETTE
	groups: List[Dict[str, Any]] = []
	for index, family in enumerate(families, start=1):
		members = _normalize_names(family)
		group_name = f'{prefix}{index}'
		group_color = palette[(index - 1) % len(palette)]
		group: Dict[str, Any] = {
			'name': group_name,
			'label': f'{group_name} = {{{", ".join(members)}}}'
			if members
			else f'{group_name} = {{}}',
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
	"""Build a standardized visualization payload for graph rendering.

	The generated payload contains normalized graph structures,
	highlight metadata, visualization groups, labels, and optional
	color assignments compatible with frontend visualization layers.

	Args:
		graph (Graph): Input graph instance.
		highlighted_vertices (Iterable[str] | None): Vertices that must
			be visually highlighted.
		highlighted_edges (Iterable[str] | None): Edges that must be
			visually highlighted.
		groups (Optional[List[Dict[str, Any]]]): Optional visualization
			groups describing graph families or subsets.
		labels (Optional[Dict[str, Any]]): Additional label mappings.
		colors (Optional[Dict[str, Any]]): Optional custom color
			assignments for vertices and edges.

	Returns:
		Dict[str, Any]: Visualization-ready payload containing vertices,
			edges, groups, labels, highlights, and colors.

	"""
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
