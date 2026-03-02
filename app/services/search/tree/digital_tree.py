"""
Implement a digital tree structure based on binary encoding.

Extend the base tree abstraction to provide insertion, search,
deletion, and visualization logic using a binary traversal
strategy. Represent each node with left and right branches
corresponding to binary digits.

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

from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from app.services.search.base_search import BaseSearchService
from app.services.search.tree.basic_tree import BaseTree, DigitalNode


class DigitalTree(BaseTree):
	"""
	Implement a binary digital tree using bitwise traversal.

	Store letters according to their binary representation,
	navigating left for '0' and right for '1'.
	"""

	def __init__(self, encoding: str = 'ABC'):
		"""
		Initialize digital tree configuration.

		Args:
			encoding: Define letter encoding strategy
				("ABC" positional encoding or "ASCII").

		"""
		super().__init__(encoding)
		self.root: Optional[DigitalNode] = None

	def create(self, size: int = None, digits: int = None) -> None:
		"""
		Initialize tree structure and reset root node.

		Delegate storage initialization to the base implementation
		and clear existing tree state.
		"""
		super().create(size, digits)
		self.root = None

	def _insert_node(self, binary: str, index: int, letter: str) -> None:
		"""
		Insert a node following binary digit traversal.

		Navigate the tree using each bit of the binary string,
		creating new nodes when necessary.

		Args:
			binary: Binary representation of the letter.
			index: Position in underlying storage.
			letter: Original letter value.

		Raises:
			RuntimeError: If insertion fails unexpectedly.

		"""
		bits = list(binary)
		if self.root is None:
			self.root = DigitalNode(letter, binary, index)
			return
		current = self.root
		for bit in bits:
			if bit == '0':
				if current.left is None:
					current.left = DigitalNode(letter, binary, index)
					return
				current = current.left
			else:
				if current.right is None:
					current.right = DigitalNode(letter, binary, index)
					return
				current = current.right
		raise RuntimeError('Error inesperado: no se pudo insertar')

	def _search_binary(self, binary: str) -> List[int]:
		"""
		Search for a binary value in the tree.

		Traverse nodes according to binary digits and return
		the stored position if found.

		Args:
			binary: Binary representation to locate.

		Returns:
			List[int]: 1-based position if found, otherwise empty list.

		"""
		bits = list(binary)
		current = self.root
		if current and current.binary == binary:
			return [current.index + 1]
		for bit in bits:
			if current is None:
				return []
			if bit == '0':
				current = current.left
			else:
				current = current.right
			if current and current.binary == binary:
				return [current.index + 1]
		return []

	def _delete_node(self, binary: str) -> None:
		"""
		Remove a node matching the given binary value.

		Clear node content and prune empty branches recursively.

		Args:
			binary: Binary representation of the node to remove.

		"""
		pass

	def _build_graph(
		self,
		node: Optional[DigitalNode],
		graph: nx.DiGraph,
		parent_id: Optional[int] = None,
		edge_label: Optional[str] = None,
		depth: int = 0,
		highlight_index: Optional[int] = None,
	):
		"""
		Build a graph representation of the tree.

		Add nodes and labeled edges recursively for visualization.
		Highlight a node if its index matches the specified value.
		"""
		if node is None:
			return
		node_id = id(node)
		is_highlight = highlight_index is not None and node.index == highlight_index
		graph.add_node(
			node_id,
			label=node.letter if node.letter else '',
			has_letter=node.letter is not None,
			is_highlight=is_highlight,
		)
		if parent_id is not None:
			graph.add_edge(parent_id, node_id, label=edge_label)
		self._build_graph(node.left, graph, node_id, '0', depth + 1, highlight_index)
		self._build_graph(node.right, graph, node_id, '1', depth + 1, highlight_index)

	def _compute_positions(
		self, node: Optional[DigitalNode], x: float, y: float, level: int, dx: float
	):
		"""
		Compute node coordinates for visualization layout.

		Assign positions recursively, spacing children horizontally
		according to tree depth.
		"""
		if node is None:
			return
		node_id = id(node)
		self._node_positions[node_id] = (x, y)
		spacing = dx / (2 ** (level + 1))
		next_y = y - 1.5
		if node.left:
			self._compute_positions(node.left, x - spacing, next_y, level + 1, dx)
		if node.right:
			self._compute_positions(node.right, x + spacing, next_y, level + 1, dx)
