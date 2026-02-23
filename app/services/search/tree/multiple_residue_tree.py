"""
Implement a multiple residue tree using m-bit chunk partitioning.

Extend the base tree abstraction to support multi-way branching,
where each level processes fixed-size binary segments. Handle
collisions by dynamically creating internal nodes and redistributing
existing leaves when necessary. Provide insertion, search, deletion,
and visualization support.

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
from app.services.search.tree.basic_tree import BaseTree, MultiNode


class MultipleResidueTree(BaseTree):
	"""
	Implement an m-ary residue tree based on fixed-size binary chunks.

	Partition binary representations into segments of length m and
	traverse a multi-way structure with 2^m children per node.
	Resolve prefix collisions by splitting leaves into internal nodes.
	"""

	def __init__(self, m: int, encoding: str = 'ABC'):
		"""
		Initialize multiple residue tree configuration.

		Args:
			m: Define chunk size in bits (branching factor = 2^m).
			encoding: Define letter encoding strategy
				("ABC" positional encoding or "ASCII").

		"""
		super().__init__(encoding)
		self.m = m
		self.root: Optional[MultiNode] = None

	def create(self, size: int = None, digits: int = None) -> None:
		"""
		Initialize tree structure and reset root node.

		Delegate storage initialization to the base implementation
		and clear existing tree state.
		"""
		super().create(size, digits)
		self.root = None

	def _get_chunks(self, binary: str) -> List[str]:
		"""
		Split binary string into fixed-size chunks.

		Args:
			binary: Binary representation of a letter.

		Returns:
			List[str]: List of substrings of length m.

		"""
		return [binary[i : i + self.m] for i in range(0, len(binary), self.m)]

	def _insert_node(self, binary: str, index: int, letter: str) -> None:
		"""
		Insert a node using chunk-based traversal.

		Partition the binary representation and delegate
		recursive insertion.

		Args:
			binary: Binary representation of the letter.
			index: Position in underlying storage.
			letter: Original letter value.

		"""
		chunks = self._get_chunks(binary)
		if self.root is None:
			self.root = MultiNode(self.m)
		self._insert_rec(self.root, chunks, 0, letter, binary, index)

	def _insert_rec(
		self, node: MultiNode, chunks: List[str], depth: int, letter: str, binary: str, index: int
	):
		"""
		Recursively insert a node based on chunk index.

		Create internal nodes when necessary and resolve
		collisions by redistributing existing leaves.

		Raises:
			ValueError: If depth exceeds chunk length
				or a duplicate key is detected.

		"""
		if depth == len(chunks):
			raise ValueError('Profundidad excedida')
		chk = chunks[depth]
		idx = int(chk, 2)

		if depth == len(chunks) - 1:
			if node.children[idx] is not None:
				raise ValueError('Clave duplicada')
			node.children[idx] = MultiNode(self.m, letter, binary, index)
			return

		if node.children[idx] is None:
			node.children[idx] = MultiNode(self.m)
			self._insert_rec(node.children[idx], chunks, depth + 1, letter, binary, index)
		elif node.children[idx].letter is not None:
			existing_leaf = node.children[idx]
			new_internal = MultiNode(self.m)
			node.children[idx] = new_internal
			existing_chunks = self._get_chunks(existing_leaf.binary)
			next_idx = int(existing_chunks[depth + 1], 2)
			new_internal.children[next_idx] = existing_leaf
			self._insert_rec(new_internal, chunks, depth + 1, letter, binary, index)
		else:
			self._insert_rec(node.children[idx], chunks, depth + 1, letter, binary, index)

	def _search_binary(self, binary: str) -> List[int]:
		"""
		Search for a binary value using chunk traversal.

		Navigate the tree according to each m-bit segment.

		Args:
			binary: Binary representation to locate.

		Returns:
			List[int]: 1-based position if found, otherwise empty list.

		"""
		chunks = self._get_chunks(binary)
		current = self.root
		for chk in chunks:
			if current is None:
				return []
			idx = int(chk, 2)
			current = current.children[idx]
		if current and current.binary == binary:
			return [current.index + 1]
		return []

	def _delete_node(self, binary: str) -> None:
		"""
		Remove a node matching the given binary value.

		Traverse recursively and prune empty internal nodes
		after deletion.

		Args:
			binary: Binary representation of the node to remove.

		"""
		chunks = self._get_chunks(binary)

		def remove(node: Optional[MultiNode], depth: int) -> Optional[MultiNode]:
			if node is None:
				return None
			if depth == len(chunks):
				return None
			idx = int(chunks[depth], 2)
			node.children[idx] = remove(node.children[idx], depth + 1)
			if node.letter is None and all(c is None for c in node.children):
				return None
			return node

		self.root = remove(self.root, 0)

	def _build_graph(
		self,
		node: Optional[MultiNode],
		graph: nx.DiGraph,
		parent_id: Optional[int] = None,
		edge_label: Optional[str] = None,
		depth: int = 0,
		highlight_index: Optional[int] = None,
	):
		"""
		Build a graph representation of the tree.

		Add nodes and labeled edges recursively.
		Label edges using the corresponding m-bit chunk.
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
		for i, child in enumerate(node.children):
			if child is not None:
				if child.letter is not None:
					chunks = self._get_chunks(child.binary)
					if depth < len(chunks):
						edge = chunks[depth]
					else:
						edge = format(i, 'b').zfill(self.m)
				else:
					edge = format(i, 'b').zfill(self.m)
				self._build_graph(child, graph, node_id, edge, depth + 1, highlight_index)

	def _compute_positions(
		self, node: Optional[MultiNode], x: float, y: float, level: int, dx: float
	):
		"""
		Compute node coordinates for visualization layout.

		Distribute children horizontally according to
		tree level and branching factor.
		"""
		if node is None:
			return
		node_id = id(node)
		self._node_positions[node_id] = (x, y)
		children = [c for c in node.children if c is not None]
		if not children:
			return
		spacing = dx / (2 ** (level + 1))
		next_y = y - 1.5
		total = len(children)
		for i, child in enumerate(children):
			offset = (i - (total - 1) / 2) * spacing
			self._compute_positions(child, x + offset, next_y, level + 1, dx)
