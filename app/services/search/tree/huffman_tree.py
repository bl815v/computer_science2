"""
Implement Huffman coding tree structure and related utilities.

This module provides an implementation of the Huffman coding algorithm
using a binary tree structure. The tree is constructed from a text input
based on character frequencies and generates optimal prefix-free binary
codes for compression.

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
	Represent a Huffman coding tree constructed from input text.

	The tree is built using character frequency analysis and a priority
	queue to iteratively merge nodes with the lowest frequencies until
	a single root node remains.

	Each leaf node represents a character and is assigned a binary code
	derived from its path in the tree.

	The structure is immutable once created, meaning that insertion and
	deletion operations are not allowed.

	Attributes:
		text (str):
			Input text normalized to uppercase.

		freq_dict (Dict[str, int]):
			Frequency dictionary mapping characters to occurrence counts.

		letter_to_index (Dict[str, int]):
			Mapping from characters to internal node indices.

		letter_to_code (Dict[str, str]):
			Mapping from characters to Huffman binary codes.

		total_freq (int):
			Total number of characters in the input text.

		steps (List[List[SimpleNode]]):
			Intermediate states of the priority queue during tree construction.

		root (Optional[SimpleNode]):
			Root node of the Huffman tree.

	"""

	def __init__(self, text: str, encoding: str = 'ABC'):
		"""
		Initialize the Huffman tree from the provided text.

		The constructor normalizes the input text, computes character
		frequencies, allocates internal storage, and triggers the
		tree construction process.

		Args:
			text (str):
				Source text used to generate the Huffman coding tree.

			encoding (str, optional):
				Encoding format inherited from BaseTree. Defaults to 'ABC'.

		"""
		super().__init__(encoding)
		self.text = text.upper()
		self.freq_dict = Counter(self.text)
		unique_chars = len(set(self.text))
		size = max(1, unique_chars)
		self.create(size=size, digits=1)
		self.letter_to_index: Dict[str, int] = {}
		self.letter_to_code: Dict[str, str] = {}
		self.total_freq = len(self.text)
		self.steps: List[List[SimpleNode]] = []
		self._build_tree()

	def _build_tree(self) -> None:
		"""
		Build the Huffman tree from the input text.

		This method performs the core Huffman algorithm:

		1. Create a leaf node for each character based on its frequency.
		2. Insert nodes into a priority queue ordered by frequency.
		3. Repeatedly merge the two nodes with the smallest frequencies.
		4. Continue until a single root node remains.

		The method also records intermediate steps for visualization.
		"""
		if not self.text:
			self.root = None
			return

		heap = []
		next_index = 0
		for char, count in self.freq_dict.items():
			leaf = SimpleNode(letter=char, index=next_index)
			leaf.freq = count
			leaf.name = char
			leaf.level = 0
			heapq.heappush(heap, (count, next_index, leaf))
			next_index += 1

		self._record_step(heap)

		while len(heap) > 1:
			freq1, _, left = heapq.heappop(heap)
			freq2, _, right = heapq.heappop(heap)
			internal = SimpleNode(letter=None, index=next_index)
			internal.freq = freq1 + freq2
			internal.left = left
			internal.right = right
			internal.level = max(left.level, right.level) + 1
			open_b, close_b = self._get_brackets(internal.level)
			internal.name = f'{open_b}{left.name} + {right.name}{close_b}'
			heapq.heappush(heap, (internal.freq, next_index, internal))
			next_index += 1
			self._record_step(heap)

		self.root = heap[0][2] if heap else None
		self._assign_codes(self.root, '')

	def _record_step(self, heap):
		"""
		Record an intermediate step during Huffman tree construction.

		The nodes currently present in the priority queue are extracted,
		sorted, and stored for later visualization.

		Args:
			heap:
				Priority queue containing nodes and their frequencies.

		"""
		nodes = [node for (_, _, node) in heap]
		nodes.sort(key=lambda n: (-n.freq, n.name))
		self.steps.append(nodes)

	def _assign_codes(self, node: Optional[SimpleNode], code: str) -> None:
		"""
		Recursively assign Huffman binary codes to leaf nodes.

		Left edges correspond to '0' and right edges correspond to '1'.

		Args:
			node (Optional[SimpleNode]):
				Current node in the traversal.

			code (str):
				Accumulated binary prefix for the current node.

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
		Prevent insertion into the Huffman tree.

		Huffman trees are immutable after construction.

		Raises:
			NotImplementedError:
				Always raised to indicate the operation is unsupported.

		"""
		raise NotImplementedError(
			'El árbol de Huffman es inmutable; no se pueden insertar nuevos caracteres.'
		)

	def delete(self, letter: str) -> List[int]:
		"""
		Prevent deletion from the Huffman tree.

		Huffman trees are immutable after construction.

		Raises:
			NotImplementedError:
				Always raised to indicate the operation is unsupported.

		"""
		raise NotImplementedError(
			'El árbol de Huffman es inmutable; no se pueden eliminar caracteres.'
		)

	def search(self, letter: str) -> List[int]:
		"""
		Search for a character in the Huffman tree.

		The search returns the internal index of the node associated
		with the specified character.

		Args:
			letter (str):
				Character to search.

		Returns:
			List[int]:
				A list containing the 1-based index of the character if found.
				Returns an empty list if the character is not present.

		"""
		self._validate_structure()
		letter_norm = self._normalize_letter(letter)
		if letter_norm in self.letter_to_index:
			return [self.letter_to_index[letter_norm] + 1]
		return []

	def _normalize_letter(self, letter: str) -> str:
		"""
		Normalize and validate input character.

		Args:
			letter (str):
				Input character.

		Returns:
			str:
				Uppercase normalized character.

		Raises:
			ValueError:
				If the input is not a single character.

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
		Search for a node using its Huffman binary code.

		The method performs a depth-first traversal to locate
		a node whose binary code matches the specified value.

		Args:
			binary (str):
				Binary code to search.

		Returns:
			List[int]:
				List of matching node indices.

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
		Generate a graphical visualization of the Huffman tree.

		The tree is rendered using NetworkX and Matplotlib with
		automatic layout adjustments to prevent label collisions.

		Args:
			filename (str, optional):
				Output image file name. Defaults to 'tree.png'.

			highlight_index (Optional[int], optional):
				Index of the node to highlight in the visualization.

		"""
		if self.root is None:
			return

		G = nx.DiGraph()
		self._build_graph(self.root, G, depth=0, highlight_index=highlight_index)

		base_dx = 30.0
		dx_scale = 1.0
		max_scale = 5.0
		step = 1.2
		tolerance = 0.08

		font_size = 16
		char_width_factor = 0.6

		def compute_positions_and_labels(scale):
			self._node_positions = {}
			self._compute_positions(self.root, x=0, y=0, level=0, dx=base_dx * scale)
			pos = self._node_positions.copy()

			xs = [x for x, y in pos.values()]
			ys = [y for x, y in pos.values()]
			xmin, xmax = min(xs), max(xs)
			ymin, ymax = min(ys), max(ys)
			pad_x = 2.0
			pad_y = 1.0
			x_lim = (xmin - pad_x, xmax + pad_x)
			y_lim = (ymin - pad_y, ymax + pad_y)

			labels_info = []
			for node, (x, y) in pos.items():
				data = G.nodes[node]
				freq = data.get('freq')
				if freq is None:
					continue
				if freq == self.total_freq:
					text = '1'
				else:
					text = f'{freq}/{self.total_freq}'
				side = data.get('side')
				if side == 'left':
					label_x = x - 4.0
					label_y = y
				elif side == 'right':
					label_x = x + 4.0
					label_y = y
				else:
					label_x = x
					label_y = y + 0.2
				labels_info.append({'x': label_x, 'y': label_y, 'text': text})
			return pos, x_lim, y_lim, labels_info

		while dx_scale <= max_scale:
			pos, x_lim, y_lim, labels_info = compute_positions_and_labels(dx_scale)

			fig_width = 20.0
			fig_height = 12.0

			phys_labels = []
			collision = False
			for info in labels_info:
				phys_x = (info['x'] - x_lim[0]) / (x_lim[1] - x_lim[0]) * fig_width
				phys_y = (info['y'] - y_lim[0]) / (y_lim[1] - y_lim[0]) * fig_height
				text_len = len(info['text'])
				half_width = (text_len * font_size * char_width_factor) / 72.0 / 2.0
				half_height = font_size / 72.0 / 2.0
				phys_labels.append({'x': phys_x, 'y': phys_y, 'hw': half_width, 'hh': half_height})

			n = len(phys_labels)
			for i in range(n):
				for j in range(i + 1, n):
					dx = abs(phys_labels[i]['x'] - phys_labels[j]['x'])
					dy = abs(phys_labels[i]['y'] - phys_labels[j]['y'])
					if dx < (phys_labels[i]['hw'] + phys_labels[j]['hw'] + tolerance) and dy < (
						phys_labels[i]['hh'] + phys_labels[j]['hh'] + tolerance
					):
						collision = True
						break
				if collision:
					break

			if not collision:
				break
			dx_scale *= step

		plt.figure(figsize=(20, 12))
		plt.xlim(x_lim)
		plt.ylim(y_lim)

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

	def _record_step(self, heap):
		"""
		Record an intermediate step during Huffman tree construction.

		Args:
			heap: Priority queue containing nodes and their frequencies.

		"""
		nodes = [node for (_, _, node) in heap]
		nodes.sort(key=lambda n: (-n.freq, -n.index))
		self.steps.append(nodes)

	def _get_brackets(self, level: int):
		"""
		Select bracket style based on tree depth level.

		Brackets alternate between:
			(), [], {}

		Args:
			level (int):
				Depth level in the tree.

		Returns:
			Tuple[str, str]:
				Opening and closing bracket characters.

		"""
		r = (level - 1) % 3
		if r == 0:
			return '(', ')'
		elif r == 1:
			return '[', ']'
		else:
			return '{', '}'

	def show_table(self):
		"""
		Generate the Huffman encoding table.

		The table contains character frequencies, binary codes,
		and length statistics used to compute compression metrics.

		Returns:
			Dict:
				Dictionary containing:

				- table: List of table rows with character data.
				- total_L: Total weighted code length.
				- average_L: Average code length.
				- total_freq: Total number of characters.

		"""
		if not self.letter_to_code:
			return {'table': [], 'total_L': 0, 'average_L': 0.0, 'total_freq': 0}

		total_L = 0
		table_rows = []

		chars = list(self.freq_dict.keys())
		chars.sort(key=lambda c: (-self.freq_dict[c], -self.letter_to_index[c]))

		for char in chars:
			freq = self.freq_dict[char]
			code = self.letter_to_code[char]
			li = len(code)
			L = freq * li
			total_L += L
			row = {'char': char, 'freq': freq, 'binary': code, 'li': li, 'L': L}
			table_rows.append(row)

		promedio = total_L / self.total_freq

		return {
			'table': table_rows,
			'total_L': total_L,
			'average_L': promedio,
			'total_freq': self.total_freq,
		}

	def show_steps(self, steps: Optional[List[int]] = None):
		"""
		Return the intermediate steps of the Huffman algorithm.

		Each step corresponds to the current contents of the
		priority queue during tree construction.

		Args:
			steps (Optional[List[int]]):
				Specific step numbers to return.

		Returns:
			Dict:
				Dictionary containing the selected construction steps.

		"""
		if not hasattr(self, 'steps') or not self.steps:
			return {'steps': []}

		total_steps = len(self.steps)
		if steps is None:
			steps_to_show = range(1, total_steps + 1)
		else:
			steps_to_show = [s for s in steps if 1 <= s <= total_steps]

		result_steps = []

		for step_num in steps_to_show:
			nodes = self.steps[step_num - 1]
			items = []
			for node in nodes:
				display_name = node.name
				if len(nodes) == 1 and display_name:
					first = display_name[0]
					last = display_name[-1]
					if first in '([{' and last in ')]}':
						close_map = {'(': ')', '[': ']', '{': '}'}
						if close_map.get(first) == last:
							display_name = display_name[1:-1]
				items.append({'name': display_name, 'freq': node.freq})
			result_steps.append({'step': step_num, 'items': items})

		return {'steps': result_steps}
