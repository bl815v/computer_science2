"""
Implement a simple residue tree structure using binary traversal.

Extend the base tree abstraction to handle collisions by creating
internal nodes dynamically when two elements share common binary
prefixes. Support insertion, search, deletion, and visualization.

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

from typing import List, Optional

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from app.services.search.base_search import BaseSearchService
from app.services.search.tree.basic_tree import BaseTree, SimpleNode


class SimpleResidueTree(BaseTree):
	"""
	Implement a binary residue tree with dynamic internal nodes.

	Resolve prefix collisions by splitting nodes when two
	binary representations diverge at a deeper level.
	"""

	def __init__(self, encoding: str = 'ABC'):
		"""
		Initialize simple residue tree configuration.

		Args:
			encoding: Define letter encoding strategy
				("ABC" positional encoding or "ASCII").

		"""
		super().__init__(encoding)
		self.root: Optional[SimpleNode] = None

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
		Insert a node using binary prefix comparison.

		Traverse the tree according to binary digits. When a collision
		occurs (two values share a prefix but diverge later), create
		a new internal node to separate both branches.

		Args:
			binary: Binary representation of the letter.
			index: Position in underlying storage.
			letter: Original letter value.

		Raises:
			ValueError: If traversal depth exceeds binary length.

		"""
		bits = list(binary)
		if self.root is None:
			self.root = SimpleNode()
			if bits[0] == '0':
				self.root.left = SimpleNode(letter, binary, index)
			else:
				self.root.right = SimpleNode(letter, binary, index)
			return

		def insert_rec(node: SimpleNode, bits: List[str], depth: int) -> None:
			if depth == len(bits):
				raise ValueError('Profundidad excedida')
			bit = bits[depth]
			if bit == '0':
				child = node.left
				def set_child(n):
					return setattr(node, 'left', n)
			else:
				child = node.right
				def set_child(n):
					return setattr(node, 'right', n)

			if child is None:
				set_child(SimpleNode(letter, binary, index))
				return
			else:
				if child.letter is not None:
					new_internal = SimpleNode()
					set_child(new_internal)
					existing_bits = list(child.binary)
					if existing_bits[depth + 1] == '0':
						new_internal.left = child
					else:
						new_internal.right = child
					insert_rec(new_internal, bits, depth + 1)
				else:
					insert_rec(child, bits, depth + 1)

		insert_rec(self.root, bits, 0)

	def _search_binary(self, binary: str) -> List[int]:
		"""
		Search for a binary value in the tree.

		Traverse the structure following binary digits until
		reaching the target depth.

		Args:
			binary: Binary representation to locate.

		Returns:
			List[int]: 1-based position if found, otherwise empty list.

		"""
		bits = list(binary)
		current = self.root
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

		Prune empty internal nodes recursively after deletion.

		Args:
			binary: Binary representation of the node to remove.

		"""

		def remove(node: Optional[SimpleNode], bits: List[str], depth: int) -> Optional[SimpleNode]:
			if node is None:
				return None
			if depth == len(bits):
				if node.binary == binary:
					return None
				return node
			bit = bits[depth]
			if bit == '0':
				node.left = remove(node.left, bits, depth + 1)
			else:
				node.right = remove(node.right, bits, depth + 1)
			if node.letter is None and node.left is None and node.right is None:
				return None
			return node

		self.root = remove(self.root, list(binary), 0)

	def _build_graph(
		self,
		node: Optional[SimpleNode],
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
		self, node: Optional[SimpleNode], x: float, y: float, level: int, dx: float
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
