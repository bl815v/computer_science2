"""
Implement Huffman coding tree structure for character compression.

Construct a binary tree based on character frequency
distribution from an input text. Generate prefix-free
binary codes for each character and provide search
and visualization capabilities.

Disallow insertion and deletion operations after
construction, ensuring structural immutability.

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

import heapq
from collections import Counter
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from app.services.search.base_search import BaseSearchService
from app.services.search.tree.basic_tree import BaseTree, SimpleNode


class HuffmanTree(BaseTree):
	"""
	Represent Huffman coding tree built from input text.

	Generate optimal prefix-free binary codes based on
	character frequency. Once constructed, the structure
	remains immutable and does not allow insertions
	or deletions.

	Attributes:
		text: Normalized uppercase input text.
		letter_to_index: Mapping from letter to storage index.
		letter_to_code: Mapping from letter to Huffman binary code.
		total_freq: Total number of characters in input text.
		root: Root node of Huffman tree.

	"""

	def __init__(self, text: str, encoding: str = 'ABC'):
		"""
		Initialize Huffman tree from input text.

		Normalize text to uppercase, compute character
		frequencies, allocate base storage, and build
		Huffman tree structure.

		Args:
			text: Source text used to generate frequency distribution.
			encoding: Compatibility parameter inherited from BaseTree.

		"""
		super().__init__(encoding)
		self.text = text.upper()
		unique_chars = len(set(self.text))
		size = max(1, unique_chars)
		self.create(size=size, digits=1)
		self.letter_to_index: Dict[str, int] = {}
		self.letter_to_code: Dict[str, str] = {}
		self.total_freq = len(self.text)
		self._build_tree()

	def _build_tree(self) -> None:
		"""
		Build Huffman tree from stored text.

		Count character frequencies, construct leaf nodes,
		and iteratively merge lowest-frequency nodes using
		a priority queue until a single root remains.

		Assign binary codes to each character after
		tree construction.
		"""
		if not self.text:
			self.root = None
			return

		freq = Counter(self.text)

		heap = []
		next_index = 0
		for char, count in freq.items():
			leaf = SimpleNode(letter=char, index=next_index)
			leaf.freq = count
			heapq.heappush(heap, (count, next_index, leaf))
			next_index += 1

		while len(heap) > 1:
			freq1, _, left = heapq.heappop(heap)
			freq2, _, right = heapq.heappop(heap)
			internal = SimpleNode(letter=None, index=None)
			internal.freq = freq1 + freq2
			internal.left = left
			internal.right = right
			heapq.heappush(heap, (internal.freq, next_index, internal))
			next_index += 1

		self.root = heap[0][2] if heap else None

		self._assign_codes(self.root, '')

	def _assign_codes(self, node: Optional[SimpleNode], code: str) -> None:
		"""
		Assign binary Huffman codes to leaf nodes.

		Traverse tree recursively, appending '0' for left
		edges and '1' for right edges. Store resulting
		codes in mapping dictionaries and internal data array.

		Args:
			node: Current tree node.
			code: Accumulated binary prefix.

		"""
		if node is None:
			return
		if node.left is None and node.right is None:
			node.binary = code
			self.letter_to_code[node.letter] = code
			self.letter_to_index[node.letter] = node.index
			self.data[node.index] = code
		else:
			self._assign_codes(node.left, code + '0')
			self._assign_codes(node.right, code + '1')

	def insert(self, letter: str) -> int:
		"""
		Prevent insertion of new characters.

		Raises:
			NotImplementedError: Always raised since
			Huffman tree is immutable.

		"""
		raise NotImplementedError(
			'El árbol de Huffman es inmutable; no se pueden insertar nuevos caracteres.'
		)

	def delete(self, letter: str) -> List[int]:
		"""
		Prevent deletion of characters.

		Raises:
			NotImplementedError: Always raised since
			Huffman tree is immutable.

		"""
		raise NotImplementedError(
			'El árbol de Huffman es inmutable; no se pueden eliminar caracteres.'
		)

	def search(self, letter: str) -> List[int]:
		"""
		Search for character in Huffman tree.

		Normalize input to uppercase and return
		1-based index if character exists.

		Args:
			letter: Character to search.

		Returns:
			List[int]: Position list containing index if found,
					otherwise empty list.

		"""
		self._validate_structure()
		letter_norm = self._normalize_letter(letter)
		if letter_norm in self.letter_to_index:
			return [self.letter_to_index[letter_norm] + 1]
		return []

	def _normalize_letter(self, letter: str) -> str:
		"""
		Normalize and validate search input.

		Ensure input is a single character and convert
		it to uppercase.

		Args:
			letter: Character to normalize.

		Returns:
			str: Uppercase character.

		Raises:
			ValueError: If input length is invalid.

		"""
		if len(letter) != 1:
			raise ValueError('La búsqueda debe ser un único carácter.')
		return letter.upper()

	def _insert_node(self, binary: str, index: int, letter: str) -> None:
		"""
		Provide placeholder required by BaseTree.

		Not used in HuffmanTree implementation.
		"""
		pass

	def _search_binary(self, binary: str) -> List[int]:
		"""
		Search for node by binary code.

		Perform depth-first traversal to locate
		leaf node with matching binary code.

		Args:
			binary: Binary code to search.

		Returns:
			List[int]: Matching node indices.

		"""
		result = []

		def dfs(node: Optional[SimpleNode]) -> None:
			if node is None:
				return
			if node.letter is not None and node.binary == binary:
				result.append(node.index)
			dfs(node.left)
			dfs(node.right)

		dfs(self.root)
		return result

	def _delete_node(self, binary: str) -> None:
		"""
		Provide placeholder required by BaseTree.

		Not used in HuffmanTree implementation.
		"""
		pass

	def _build_graph(
		self, node, graph, parent_id=None, edge_label=None, depth=0, highlight_index=None, side=None
	):
		"""
		Build NetworkX directed graph from Huffman tree.

		Store node attributes:
			- label: Character for leaf nodes.
			- freq: Absolute frequency.
			- side: Left or right child indicator.
			- is_highlight: Highlight marker for visualization.

		Args:
			node: Current tree node.
			graph: NetworkX graph instance.
			parent_id: Parent node identifier.
			edge_label: Binary edge label ('0' or '1').
			depth: Current depth level.
			highlight_index: Optional index to highlight.
			side: Relationship to parent ('left' or 'right').

		"""
		if node is None:
			return
		node_id = id(node)

		label = node.letter if node.letter is not None else ''
		has_letter = node.letter is not None
		is_highlight = highlight_index is not None and node.index == highlight_index

		graph.add_node(
			node_id,
			label=label,
			has_letter=has_letter,
			is_highlight=is_highlight,
			freq=node.freq,
			side=side,
		)

		if parent_id is not None:
			graph.add_edge(parent_id, node_id, label=edge_label)

		self._build_graph(node.left, graph, node_id, '0', depth + 1, highlight_index, side='left')
		self._build_graph(node.right, graph, node_id, '1', depth + 1, highlight_index, side='right')

	def _compute_positions(self, node, x, y, level, dx):
		"""
		Compute (x, y) positions for visualization layout.

		Recursively assign coordinates to nodes,
		spreading children horizontally and descending vertically.

		Args:
			node: Current node.
			x: Horizontal position.
			y: Vertical position.
			level: Depth level.
			dx: Horizontal spacing factor.

		"""
		if node is None:
			return
		self._node_positions[id(node)] = (x, y)
		if node.left:
			self._compute_positions(node.left, x - dx, y - 1, level + 1, dx / 2)
		if node.right:
			self._compute_positions(node.right, x + dx, y - 1, level + 1, dx / 2)

	def plot(self, filename: str = 'tree.png', highlight_index: Optional[int] = None):
		"""
		Generate PNG visualization of Huffman tree.

		Display:
			- Leaf nodes with character labels.
			- Edge labels ('0' and '1').
			- Node frequency as fraction of total.
			- Optional highlighted node.

		Args:
			filename: Output image file path.
			highlight_index: Optional node index to highlight.

		"""
		if self.root is None:
			return

		G = nx.DiGraph()
		self._build_graph(self.root, G, depth=0, highlight_index=highlight_index)
		self._node_positions = {}
		self._compute_positions(self.root, x=0, y=0, level=0, dx=30)
		pos = self._node_positions

		plt.figure(figsize=(20, 12))

		empty_nodes = []
		leaf_nodes = []
		highlight_node = None
		for n, data in G.nodes(data=True):
			if data.get('is_highlight', False):
				highlight_node = n
			elif data.get('has_letter', False):
				leaf_nodes.append(n)
			else:
				empty_nodes.append(n)

		if empty_nodes:
			nx.draw_networkx_nodes(
				G, pos, nodelist=empty_nodes, node_color='lightgray', node_shape='o', node_size=300
			)

		if leaf_nodes:
			nx.draw_networkx_nodes(
				G, pos, nodelist=leaf_nodes, node_color='lightgray', node_shape='s', node_size=800
			)

		HIGHLIGHT_COLOR = '#7CB9E8'
		if highlight_node is not None:
			shape = 's' if G.nodes[highlight_node].get('has_letter', False) else 'o'
			nx.draw_networkx_nodes(
				G,
				pos,
				nodelist=[highlight_node],
				node_color=HIGHLIGHT_COLOR,
				node_shape=shape,
				node_size=800 if shape == 's' else 300,
			)

		labels = {}
		for n in leaf_nodes:
			if G.nodes[n]['label']:
				labels[n] = G.nodes[n]['label']
		if highlight_node is not None and G.nodes[highlight_node].get('has_letter', False):
			labels[highlight_node] = G.nodes[highlight_node]['label']
		nx.draw_networkx_labels(G, pos, labels, font_size=18, font_color='black')

		nx.draw_networkx_edges(G, pos, arrows=False, edge_color='gray')

		for u, v, data in G.edges(data=True):
			if 'label' in data:
				x1, y1 = pos[u]
				x2, y2 = pos[v]
				mx, my = (x1 + x2) / 2, (y1 + y2) / 2
				dx = x2 - x1
				dy = y2 - y1
				length = np.sqrt(dx**2 + dy**2)
				if length > 0:
					perp_x = -dy / length
					perp_y = dx / length
					if x2 < x1:
						offset_x = -perp_x * 0.2
						offset_y = -perp_y * 0.2
					else:
						offset_x = perp_x * 0.2
						offset_y = perp_y * 0.2
				else:
					offset_x = offset_y = 0
				plt.text(
					mx + offset_x,
					my + offset_y,
					data['label'],
					fontsize=18,
					ha='center',
					va='center',
					bbox=dict(facecolor='white', edgecolor='none', alpha=0.7, pad=1),
				)

		for n, data in G.nodes(data=True):
			freq = data.get('freq')
			if freq is None:
				continue
			side = data.get('side')
			x, y = pos[n]

			if freq == self.total_freq:
				text = '1'
			else:
				text = f'{freq}/{self.total_freq}'

			offset_x = 0.0
			offset_y = 0.0
			if side == 'left':
				offset_x = -4.0
			elif side == 'right':
				offset_x = 4.0
			else:
				offset_y = 0.2

			plt.text(
				x + offset_x,
				y + offset_y,
				text,
				fontsize=16,
				ha='center',
				va='center',
				color='dimgray',
				bbox=None,
			)

		plt.axis('off')
		plt.tight_layout()
		plt.savefig(filename, dpi=150, bbox_inches='tight')
		plt.close()
