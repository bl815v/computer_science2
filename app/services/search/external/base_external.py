"""Base implementation for external search structures organized in blocks.

This module defines an abstract base class used to implement
external search structures that organize data into fixed-size blocks.

The structure maintains:

    - Global ordering across all blocks.
    - Internal ordering within each block.
    - Compact storage without gaps between valid keys.

The block size is automatically calculated as the integer square
root of the total structure capacity. This organization approximates
classical external storage models used in indexed files and
block-oriented search systems.

The class provides reusable implementations for:

    - Structure initialization.
    - Snapshot export and restoration.
    - Ordered insertion.
    - Deletion and compaction.
    - Global sorting across blocks.

Concrete subclasses are responsible for implementing the
specific search strategy by overriding the abstract ``search`` method.

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
from copy import deepcopy
from typing import Any, Dict, List, Optional

from app.services.search.base_search import BaseSearchService
from app.services.search.persistence import SnapshotError


class BaseExternalSearch(BaseSearchService):
	"""Abstract base class for block-based external search structures.

	This class defines the common behavior shared by all external
	search structures implemented in the project.

	Data is stored inside fixed-size blocks. The block size is
	computed as the integer square root of the total structure
	capacity. Both global ordering and internal block ordering
	are preserved after insertions and deletions.

	Subclasses inherit generic structure management behavior
	and only need to implement their own search strategy.

	Attributes:
		blocks (List[List[Optional[str]]]):
			Collection of storage blocks. Each block contains
			numeric keys or ``None`` values representing empty
			positions.

		block_size (int):
			Maximum number of elements stored per block.

	"""

	snapshot_type = 'base_external'

	def __init__(self) -> None:
		"""Initialize an empty external search structure.

		Create the internal block container and initialize
		the block size to zero. The structure remains unusable
		until ``create`` is called.

		"""
		super().__init__()

		self.blocks: List[List[Optional[str]]] = []
		self.block_size: int = 0

	def create(self, size: int, digits: int) -> None:
		"""Create and initialize the block-based structure.

		The method computes the block size using the integer
		square root of the requested capacity and divides
		the structure into multiple blocks.

		The final block may contain fewer positions than the
		others when the total size is not perfectly divisible.

		Args:
			size (int):
				Maximum number of elements supported by
				the structure.

			digits (int):
				Required number of digits for each key.

		Raises:
			ValueError:
				If ``size`` or ``digits`` are invalid.

		"""
		super().create(size, digits)

		self.block_size = math.isqrt(size)

		num_blocks = (size + self.block_size - 1) // self.block_size

		self.blocks = []

		for i in range(num_blocks):
			start = i * self.block_size
			end = min(start + self.block_size, size)

			self.blocks.append(
				[None] * (end - start),
			)

	def _snapshot_config(self) -> Dict[str, Any]:
		"""Generate snapshot configuration metadata.

		Extend the base snapshot configuration by including
		the computed block size.

		Returns:
			Dict[str, Any]:
				Configuration section used during snapshot export.

		"""
		config = super()._snapshot_config()

		config['block_size'] = self.block_size

		return config

	def _snapshot_state(self) -> Dict[str, Any]:
		"""Generate snapshot state information.

		Create a deep copy of the current block layout so the
		exported snapshot remains independent from future
		modifications.

		Returns:
			Dict[str, Any]:
				State section used during snapshot export.

		"""
		return {
			'blocks': deepcopy(self.blocks),
		}

	def _restore_snapshot(
		self,
		config: Dict[str, Any],
		state: Dict[str, Any],
	) -> None:
		"""Restore the structure state from a snapshot.

		The method recreates the structure using the stored
		configuration and restores the block layout.

		Args:
			config (Dict[str, Any]):
				Snapshot configuration metadata.

			state (Dict[str, Any]):
				Snapshot state information.

		Raises:
			SnapshotError:
				If the snapshot data is invalid or inconsistent
				with the computed block layout.

		"""
		size = int(config.get('size', 0))
		digits = int(config.get('digits', 0))
		block_size = int(config.get('block_size', 0))

		self.create(size=size, digits=digits)

		if block_size != self.block_size:
			raise SnapshotError(
				'Snapshot block size does not match the computed layout',
			)

		blocks = state.get('blocks', [])

		if not isinstance(blocks, list):
			raise SnapshotError(
				'External snapshot blocks must be a list',
			)

		self.blocks = deepcopy(blocks)

	def insert(self, value: str) -> int:
		"""Insert a new key into the structure.

		The method inserts the key into the first available
		position and then globally sorts the structure to
		preserve ordering across all blocks.

		Args:
			value (str):
				Numeric key to insert.

		Returns:
			int:
				1-based global position where the value was
				initially inserted before sorting.

		Raises:
			ValueError:
				If the structure is not initialized, the
				value is invalid, already exists, or the
				structure is full.

		"""
		self._validate_structure()
		self._validate_value(value)

		if self.search(value):
			raise ValueError(
				f'La clave {value} ya existe en la estructura',
			)

		first_empty = None

		for i, block in enumerate(self.blocks):
			for j, v in enumerate(block):
				if v is None:
					first_empty = (i, j)
					break

			if first_empty:
				break

		if first_empty is None:
			raise ValueError(
				'No hay espacio disponible en la estructura',
			)

		i, j = first_empty

		self.blocks[i][j] = value

		global_pos = sum(len(b) for b in self.blocks[:i]) + j + 1

		self.sort()

		return global_pos

	def delete(self, value: str) -> List[int]:
		"""Delete all occurrences of a key from the structure.

		The method searches the entire structure, removes all
		matching values, and then compacts the remaining data
		by reordering the structure.

		Args:
			value (str):
				Numeric key to remove.

		Returns:
			List[int]:
				List of 1-based global positions where the
				key was found and deleted.

				Returns an empty list if the key does not exist.

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
		"""Sort and compact all stored keys.

		The method extracts all non-null values, sorts them
		in ascending order, and redistributes them sequentially
		across all blocks.

		Empty positions are grouped at the end of the structure.

		Raises:
			ValueError:
				If the structure is not initialized.

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
		"""Search for a key using a specialized strategy.

		Subclasses must implement their own search algorithm,
		such as sequential search, indexed search, or binary
		search across blocks.

		Args:
			value (str):
				Numeric key to search.

		Returns:
			List[Dict[str, int]]:
				List describing all positions where the key
				was found.

				Each dictionary contains:

					- ``global_position``:
					  1-based global position.

					- ``block_index``:
					  1-based block index.

					- ``block_position``:
					  1-based position inside the block.

				Returns an empty list if the key does not exist.

		"""
		pass
