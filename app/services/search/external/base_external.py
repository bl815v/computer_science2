"""
Base implementation for external search structures organized in blocks.

This module defines an abstract base class for external search methods
that organize data into fixed-size blocks. The structure maintains:

    - Global ordering across all blocks.
    - Internal ordering within each block.

The block size is calculated as the floor of the square root of the
total number of elements. This layout approximates classical external
search methods used in file indexing and block-based storage systems.

The class provides generic implementations for:

    - Structure creation
    - Value insertion
    - Value deletion
    - Global sorting and compaction

Subclasses must implement the specific search strategy by overriding
the `search` method.

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

import math
from abc import abstractmethod
from typing import Dict, List, Optional

from app.services.search.base_search import BaseSearchService


class BaseExternalSearch(BaseSearchService):
	"""
	Abstract base class for block-based external search structures.

	Data is stored in several fixed-size blocks. The block size is
	calculated as the floor of the square root of the total number
	of elements. Blocks maintain global ordering across the structure
	and internal ordering within each block.

	This class provides common functionality for managing the
	block structure, while subclasses must implement their
	specific search algorithm.

	Attributes:
		blocks (List[List[Optional[str]]]):
			List of blocks storing keys. Each block contains values
			or None in empty positions.

		block_size (int):
			Fixed size of each block (the last block may be smaller).

	"""

	def __init__(self) -> None:
		"""
		Initialize an empty external search structure.

		Creates an empty list of blocks and sets the block size to zero.
		The structure must be initialized using `create()` before use.
		"""
		super().__init__()
		self.blocks: List[List[Optional[str]]] = []
		self.block_size: int = 0

	def create(self, size: int, digits: int) -> None:
		"""
		Initialize the structure with a fixed capacity and key length.

		The block size is computed as the integer square root of the
		total size. The storage is then divided into blocks of that size.
		The final block may contain fewer elements.

		Args:
			size (int):
				Maximum number of elements the structure can store.

			digits (int):
				Required number of digits for each key.

		Raises:
			ValueError:
				If `size` or `digits` are not positive integers.

		"""
		super().create(size, digits)

		self.block_size = math.isqrt(size)
		num_blocks = (size + self.block_size - 1) // self.block_size
		self.blocks = []
		for i in range(num_blocks):
			start = i * self.block_size
			end = min(start + self.block_size, size)
			self.blocks.append([None] * (end - start))

	def insert(self, value: str) -> int:
		"""
		Insert a new key into the structure.

		The value is first placed in the first available empty position
		in global order. After insertion, the structure is sorted to
		maintain the ordered sequence across all blocks.

		Args:
			value (str):
				Numeric key to insert.

		Returns:
			int:
				1-based global position where the value was initially inserted.

		Raises:
			ValueError:
				If the structure is not initialized, the value is invalid,
				the value already exists, or the structure is full.

		"""
		self._validate_structure()
		self._validate_value(value)

		if self.search(value):
			raise ValueError(f'La clave {value} ya existe en la estructura')

		first_empty = None
		for i, block in enumerate(self.blocks):
			for j, v in enumerate(block):
				if v is None:
					first_empty = (i, j)
					break
			if first_empty:
				break

		if first_empty is None:
			raise ValueError('No hay espacio disponible en la estructura')

		i, j = first_empty
		self.blocks[i][j] = value
		global_pos = sum(len(b) for b in self.blocks[:i]) + j + 1

		self.sort()
		return global_pos

	def delete(self, value: str) -> List[int]:
		"""
		Remove all occurrences of a key from the structure.

		The method identifies all matching values, removes them from
		their positions, and then reorders the structure.

		Args:
			value (str):
				Numeric key to remove.

		Returns:
			List[int]:
				List of global positions (1-based) where the key was found
				and removed. Returns an empty list if the key does not exist.

		Raises:
			ValueError:
				If the structure is not initialized.

		"""
		self._validate_structure()
		positions_info = self.search(value)

		if not positions_info:
			return []

		global_positions = []
		for info in positions_info:
			global_pos = info['global_position']
			global_positions.append(global_pos)
			idx = global_pos - 1
			acum = 0
			for block in self.blocks:
				if idx < acum + len(block):
					internal = idx - acum
					block[internal] = None
					break
				acum += len(block)

		self.sort()
		return global_positions

	def sort(self) -> None:
		"""
		Sort the structure and compact all non-null values.

		The method collects all non-null values, sorts them in ascending
		order, and redistributes them sequentially across the blocks.
		Empty positions are placed at the end of the structure.
		"""
		self._validate_structure()

		values = []
		for block in self.blocks:
			for v in block:
				if v is not None:
					values.append(v)
		values.sort()

		idx = 0
		for block in self.blocks:
			for j in range(len(block)):
				if idx < len(values):
					block[j] = values[idx]
					idx += 1
				else:
					block[j] = None

	@abstractmethod
	def search(self, value: str) -> List[Dict[str, int]]:
		"""
		Search for a key using a subclass-specific strategy.

		Each subclass implements its own search algorithm, such as
		sequential, indexed, or binary search across blocks.

		Args:
			value (str):
				Numeric key to search for.

		Returns:
			List[Dict[str, int]]:
				List of dictionaries describing the positions where
				the key was found. Each dictionary contains:

					- 'global_position': 1-based position in the entire structure
					- 'block_index': index of the block (1-based)
					- 'block_position': 1-based position within the block

				Returns an empty list if the key is not found.

		"""
		pass
