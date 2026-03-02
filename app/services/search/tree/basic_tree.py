"""Define base structures and shared behavior for tree-based letter search.

Provide node representations and an abstract tree implementation
supporting insertion, search, deletion, and visualization. Encode
letters using configurable binary representations and integrate
with the base search service infrastructure.

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

from abc import abstractmethod
from typing import List, Optional

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from app.services.search.base_search import BaseSearchService


class DigitalNode:
	"""
	Represent a binary node for digital tree structures.

	Store letter metadata, binary representation, and child references.
	"""

	def __init__(
		self,
		letter: Optional[str] = None,
		binary: Optional[str] = None,
		index: Optional[int] = None,
	):
		"""
		Initialize a digital tree node.

		Args:
			letter: Store the associated letter.
			binary: Store the binary representation of the letter.
			index: Store the position in the underlying data array.

		"""
		self.letter = letter
		self.binary = binary
		self.index = index
		self.left: Optional[DigitalNode] = None
		self.right: Optional[DigitalNode] = None


class SimpleNode:
	"""
	Represent a binary node for simple tree structures.

	Store letter metadata, binary representation, and left/right children.
	"""

	def __init__(
		self,
		letter: Optional[str] = None,
		binary: Optional[str] = None,
		index: Optional[int] = None,
	):
		"""
		Initialize a simple binary tree node.

		Args:
			letter: Store the associated letter.
			binary: Store the binary representation of the letter.
			index: Store the position in the underlying data array.

		"""
		self.letter = letter
		self.binary = binary
		self.index = index
		self.left: Optional[SimpleNode] = None
		self.right: Optional[SimpleNode] = None


class MultiNode:
	(
		"""
    Represent a multi-way node for m-ary tree structures.

    Maintain a fixed number of children determined by 2^m.
    """
		"""
    Represent a multi-way node for m-ary tree structures.

    Maintain a fixed number of children determined by 2^m.
    """
	)

	def __init__(
		self,
		m: int,
		letter: Optional[str] = None,
		binary: Optional[str] = None,
		index: Optional[int] = None,
	):
		"""
		Initialize an m-ary tree node.

		Args:
		    m: Define branching factor exponent (number of children = 2^m).
		    letter: Store the associated letter.
		    binary: Store the binary representation of the letter.
		    index: Store the position in the underlying data array.

		"""
		self.m = m
		self.letter = letter
		self.binary = binary
		self.index = index
		self.children: List[Optional[MultiNode]] = [None] * (2**m)


class BaseTree(BaseSearchService):
	"""
	Provide an abstract base implementation for letter-based trees.

	Manage encoding, storage, validation, and visualization logic.
	Delegate structural behavior to concrete subclasses.
	"""

	def __init__(self, encoding: str = 'ABC'):
		"""
		Initialize tree configuration.

		Args:
		    encoding: Define letter encoding strategy.
		        Supported values:
		        - "ABC": Spanish alphabet positional encoding.
		        - "ASCII": Standard ASCII encoding.

		"""
		super().__init__()
		self.encoding = encoding.upper()
		self.root = None
		self._node_positions = {}

	def create(self, size: int = None, digits: int = None) -> None:
		"""
		Initialize the tree structure.

		Set default size and digit configuration if not provided.
		Reset root node and underlying storage.
		"""
		if size is None:
			size = 1000
		if digits is None:
			if self.encoding == 'ABC':
				digits = 5
			else:
				digits = 8
		super().create(size, digits)
		self.root = None

	def _normalize_letter(self, letter: str) -> str:
		letter = letter.upper()
		alfabeto = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
		if letter not in alfabeto:
			raise ValueError(f"Letra '{letter}' no válida. Use solo letras del alfabeto americano.")
		return letter

	def _letter_to_binary(self, letter: str) -> str:
		"""
		Convert a letter to its binary representation.

		Apply the configured encoding strategy.

		Raises:
			ValueError: If encoding type is unsupported.

		"""
		if self.encoding == 'ABC':
			alfabeto = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
			pos = alfabeto.index(letter) + 1
			return format(pos, 'b').zfill(self.digits)
		elif self.encoding == 'ASCII':
			codigo = ord(letter)
			return format(codigo, 'b').zfill(self.digits)
		else:
			raise ValueError(f'Codificación desconocida: {self.encoding}')

	def _binary_to_letter(self, binary: str) -> str:
		"""Convert a binary string back to its letter representation."""
		if self.encoding == 'ABC':
			pos = int(binary, 2)
			alfabeto = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
			return alfabeto[pos - 1]
		elif self.encoding == 'ASCII':
			return chr(int(binary, 2))
		else:
			raise ValueError(f'Codificación desconocida: {self.encoding}')

	def _rebuild_tree(self):
		"""Rebuild the tree structure from the current data array."""
		self.root = None
		for i, val in enumerate(self.data):
			if val is not None:
				letter = self._binary_to_letter(val)
				self._insert_node(val, i, letter)

	def insert(self, letter: str) -> int:
		"""
		Insert a letter into the tree.

		Encode the letter, validate uniqueness, assign storage index,
		and delegate structural insertion to subclass implementation.

		Returns:
			int: 1-based position where the value was stored.

		Raises:
			ValueError: If the letter already exists.

		"""
		self._validate_structure()
		letter_norm = self._normalize_letter(letter)
		binary = self._letter_to_binary(letter_norm)
		self._validate_value(binary)

		if self.search(letter_norm):
			raise ValueError(f"La letra '{letter_norm}' ya existe en la estructura")

		try:
			index = self.data.index(None)
		except ValueError:
			self.data.append(None)
			index = len(self.data) - 1
			self.size += 1

		self._insert_node(binary, index, letter_norm)
		self.data[index] = binary
		return index + 1

	def search(self, letter: str) -> List[int]:
		"""
		Search for a letter in the tree.

		Convert the letter to binary form and delegate search
		to subclass implementation.

		Returns:
			List[int]: 1-based positions where the letter is found.

		"""
		self._validate_structure()
		letter_norm = self._normalize_letter(letter)
		binary = self._letter_to_binary(letter_norm)
		return self._search_binary(binary)

	def delete(self, letter: str) -> List[int]:
		"""
		Delete a letter from the tree.

		Remove associated storage entries and delegate structural
		deletion to subclass implementation.

		Returns:
			List[int]: 1-based positions removed.

		"""
		self._validate_structure()
		letter_norm = self._normalize_letter(letter)
		binary = self._letter_to_binary(letter_norm)
		positions = self._search_binary(binary)
		if not positions:
			return []
		for pos in positions:
			self.data[pos - 1] = None
		self._delete_node(binary)
		return positions

	def search_plot(self, letter: str, filename: str = 'search_result.png'):
		"""
		Search for a letter and generate a visualization.

		Highlight the first matching node in the generated image.
		"""
		positions = self.search(letter)
		if not positions:
			print(f"La letra '{letter}' no se encontró.")
			return
		target_index = positions[0] - 1
		self.plot(filename, highlight_index=target_index)

	@abstractmethod
	def _insert_node(self, binary: str, index: int, letter: str) -> None:
		"""
		Insert a node into the tree structure.

		Implement structural insertion logic in subclasses.
		"""
		pass

	@abstractmethod
	def _search_binary(self, binary: str) -> List[int]:
		"""
		Search for a binary value in the tree structure.

		Implement search traversal logic in subclasses.
		"""
		pass

	@abstractmethod
	def _delete_node(self, binary: str) -> None:
		"""
		Delete a node from the tree structure.

		Implement structural deletion logic in subclasses.
		"""
		pass

	def sort(self) -> None:
		"""
		Sort not applicable for tree structures.

		Override to do nothing.
		"""
		pass

	@abstractmethod
	def _build_graph(
		self, node, graph, parent_id=None, edge_label=None, depth=0, highlight_index=None
	):
		"""
		Build graph representation for visualization.

		Populate graph nodes and edges recursively.
		"""
		pass

	@abstractmethod
	def _compute_positions(self, node, x, y, level, dx):
		"""
		Compute node positions for visualization layout.

		Store calculated coordinates in internal position mapping.
		"""
		pass

	def plot(self, filename: str = 'tree.png', highlight_index: Optional[int] = None):
		"""
		Generate a tree visualization image.

		Render nodes and edges using NetworkX and Matplotlib.
		Highlight a specific node if an index is provided.
		"""
		if self.root is None:
			return
		G = nx.DiGraph()
		self._build_graph(self.root, G, depth=0, highlight_index=highlight_index)
		self._node_positions = {}
		self._compute_positions(self.root, x=0, y=0, level=0, dx=10)
		pos = self._node_positions

		plt.figure(figsize=(12, 8))
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

		HIGHLIGHT_COLOR = '#7CB9E8'  # Blue
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

		nx.draw_networkx_labels(G, pos, labels, font_size=10, font_color='black')

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
					fontsize=9,
					ha='center',
					va='center',
					bbox=dict(facecolor='white', edgecolor='none', alpha=0.7, pad=1),
				)
		plt.axis('off')
		plt.tight_layout()
		plt.savefig(filename, dpi=150, bbox_inches='tight')
		plt.close()
