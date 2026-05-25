"""
External hash-based search structure.

This module implements an external search structure that combines
block-based storage with hash indexing and overflow lists.

Unlike ordered external search structures (such as linear or binary
external search), this structure does not maintain global ordering.
Instead, it uses a hash function to determine the ideal position
for each key.

If the ideal position inside the block is already occupied,
the key is inserted into an overflow list associated with the block.

Main components implemented in this module:

    HashExternalSearch
        External hash-based search structure with per-block
        overflow lists for collision handling.

    BaseConversionHash
        Hash function implementation based on base conversion
        and digit truncation.

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

from copy import deepcopy
from typing import Any, Dict, List, Optional, Tuple

from app.services.search.external.base_external import BaseExternalSearch
from app.services.search.hash.abstract_hash import HashMixin
from app.services.search.hash.collision_simple import CollisionResolver
from app.services.search.hash.hash_function import HashFunction
from app.services.search.persistence import (
	SnapshotError,
	hash_function_from_snapshot,
	hash_function_to_snapshot,
)


class HashExternalSearch(BaseExternalSearch):
	"""
	External hash-based search structure with block-level overflow lists.

	This structure combines block-based storage with a hash indexing
	strategy. A hash function determines the ideal global position for
	each key within the structure.

	If the computed position inside the corresponding block is free,
	the key is stored directly in that position. If the position is
	already occupied, the key is inserted into an overflow list
	associated with the block.

	The overflow lists handle collisions using a simple chained
	approach, where multiple keys mapped to the same position are
	stored sequentially.

	Block sizes are determined by the base external structure
	(`BaseExternalSearch`), typically using a square-root
	decomposition of the total capacity.

	Attributes:
	    hash_func (HashFunction):
	        Hash function used to compute the ideal position.

	    overflow (List[List[str]]):
	        Overflow lists used to store keys that collide within
	        the same block.

	    block_offsets (List[int]):
	        Starting global offset (1-based) of each block within
	        the structure. This allows quick conversion between
	        block-local and global positions.

	"""

	snapshot_type = 'hash_external_search'

	def __init__(self, hash_func: HashFunction):
		"""
		Initialize the hash-based external structure.

		Args:
			hash_func (HashFunction):
				Hash function used to compute ideal positions
				for inserted keys.

		"""
		super().__init__()
		self.hash_func = hash_func
		self.overflow: List[List[str]] = []
		self.block_offsets: List[int] = []

	def create(self, size: int, digits: int) -> None:
		"""
		Initialize the structure and its overflow lists.

		This method creates the block structure using the base
		external search implementation and initializes an overflow
		list for each block. It also computes the starting offset
		of every block to facilitate global position calculations.

		Args:
			size (int):
				Maximum number of elements supported by the structure.

			digits (int):
				Required number of digits for each numeric key.

		"""
		super().create(size, digits)
		self.overflow = [[] for _ in range(len(self.blocks))]
		self.block_offsets = []
		acc = 0
		for block in self.blocks:
			self.block_offsets.append(acc)
			acc += len(block)

	def _snapshot_config(self) -> Dict[str, Any]:
		"""
		Return the configuration used for snapshot persistence.

		The exported configuration extends the base external
		structure configuration by including the serialized
		hash function definition.

		This information allows the structure to reconstruct
		the same hashing strategy when restoring a snapshot.

		Returns:
			Dict[str, Any]:
				Dictionary containing:

					- Base structure configuration.
					- Serialized hash function metadata.

		"""
		config = super()._snapshot_config()
		config['hash_function'] = hash_function_to_snapshot(self.hash_func)
		return config

	def _snapshot_state(self) -> Dict[str, Any]:
		"""
		Return the runtime state used for snapshot persistence.

		The exported state contains the complete storage layout
		of the structure, including:

			- Primary block storage.
			- Overflow collision lists.
			- Block offset mapping.

		Deep copies are used to avoid mutating the internal
		structure after export.

		Returns:
			Dict[str, Any]:
				Dictionary containing the current hash-based
				external structure state.

		"""
		return {
			'blocks': deepcopy(self.blocks),
			'overflow': deepcopy(self.overflow),
			'block_offsets': deepcopy(self.block_offsets),
		}

	def _restore_snapshot(self, config: Dict[str, Any], state: Dict[str, Any]) -> None:
		"""
		Restore the structure from an exported snapshot.

		The method reconstructs the hash function, recreates
		the block layout, validates the snapshot consistency,
		and restores all stored values and overflow lists.

		Args:
			config (Dict[str, Any]):
				Configuration section extracted from the snapshot.

			state (Dict[str, Any]):
				Runtime state section extracted from the snapshot.

		Raises:
			SnapshotError:
				If the snapshot structure is invalid, corrupted,
				or incompatible with the computed block layout.

		"""
		hash_func = hash_function_from_snapshot(config.get('hash_function'))
		self.hash_func = hash_func

		size = int(config.get('size', 0))
		digits = int(config.get('digits', 0))
		self.create(size=size, digits=digits)

		blocks = state.get('blocks', [])
		overflow = state.get('overflow', [])
		block_offsets = state.get('block_offsets', [])
		if (
			not isinstance(blocks, list)
			or not isinstance(overflow, list)
			or not isinstance(block_offsets, list)
		):
			raise SnapshotError('External hash snapshot is corrupt')
		if len(blocks) != len(self.blocks) or len(overflow) != len(self.blocks):
			raise SnapshotError('External hash snapshot block counts do not match')

		self.blocks = deepcopy(blocks)
		self.overflow = deepcopy(overflow)
		self.block_offsets = deepcopy(block_offsets)

		if len(self.block_offsets) != len(self.blocks):
			raise SnapshotError('External hash snapshot offsets do not match the block layout')

	def _locate(self, value: str) -> tuple[int, int, int]:
		"""
		Determine the target block and ideal hashed position.

		The method applies the configured hash function to
		compute the ideal global position for the key and
		then identifies which block contains that position.

		Args:
			value (str):
				Numeric key to locate inside the structure.

		Returns:
			tuple[int, int, int]:
				Tuple containing:

					- block_idx:
						Zero-based block index.

					- offset:
						Starting global offset of the block.

					- ideal_pos:
						Zero-based global hashed position.

		"""
		ideal_pos = self.hash_func.hash(value, self.digits, self.size) % self.size
		for i, offset in enumerate(self.block_offsets):
			if i == len(self.blocks) - 1 or ideal_pos < self.block_offsets[i + 1]:
				return i, offset, ideal_pos
		return len(self.blocks) - 1, self.block_offsets[-1], ideal_pos

	def _global_position_overflow(self, block_idx: int, pos_in_overflow: int) -> int:
		"""
		Compute the global position of an overflow element.

		Since overflow elements are stored outside the main
		block storage, their global position is calculated
		after all primary block elements and the overflow
		elements of previous blocks.

		Args:
			block_idx (int):
				Index of the block containing the overflow list.

			pos_in_overflow (int):
				Position within the block's overflow list.

		Returns:
			int:
				1-based global position of the overflow element.

		"""
		total_principal = sum(len(b) for b in self.blocks)
		overflow_before = sum(len(self.overflow[i]) for i in range(block_idx))
		return total_principal + overflow_before + pos_in_overflow + 1

	def search(self, value: str) -> List[Dict[str, int]]:
		"""
		Search for a key in the hash-based structure.

		The search first checks the ideal hashed position
		inside the corresponding block. If the key is not
		found there, the overflow list for the block is scanned.

		Args:
			value (str):
				Numeric key to search for.

		Returns:
			List[Dict[str, int]]:
				List describing the position where the key was found.

				Each dictionary contains:

					global_position:
						1-based position in the full structure.

					block_index:
						Index of the block containing the key.

					block_position:
						Position inside the block or overflow list.

				Returns an empty list if the key does not exist.

		"""
		self._validate_structure()
		self._validate_value(value)

		block_idx, offset, ideal_pos = self._locate(value)
		block = self.blocks[block_idx]
		pos_in_block = ideal_pos - offset

		if 0 <= pos_in_block < len(block) and block[pos_in_block] == value:
			return [
				{
					'global_position': ideal_pos + 1,
					'block_index': block_idx + 1,
					'block_position': pos_in_block + 1,
				}
			]

		overflow_list = self.overflow[block_idx]
		for i, v in enumerate(overflow_list):
			if v == value:
				global_pos = self._global_position_overflow(block_idx, i)
				return [
					{
						'global_position': global_pos,
						'block_index': block_idx + 1,
						'block_position': i + 1,
					}
				]
		return []

	def insert(self, value: str) -> int:
		"""
		Insert a key into the hash-based structure.

		The method computes the ideal hashed position and attempts
		to place the key directly in the corresponding block slot.
		If the slot is occupied, the key is appended to the overflow
		list for that block.

		Args:
			value (str):
				Numeric key to insert.

		Returns:
			int:
				1-based global position where the key was stored.

		Raises:
			ValueError:
				If the key already exists in the structure.

		"""
		self._validate_structure()
		self._validate_value(value)

		if self.search(value):
			raise ValueError(f'La clave {value} ya existe en la estructura')

		block_idx, offset, ideal_pos = self._locate(value)
		block = self.blocks[block_idx]
		pos_in_block = ideal_pos - offset

		if 0 <= pos_in_block < len(block) and block[pos_in_block] is None:
			block[pos_in_block] = value
			return ideal_pos + 1

		overflow_list = self.overflow[block_idx]
		overflow_list.append(value)
		return self._global_position_overflow(block_idx, len(overflow_list) - 1)

	def delete(self, value: str) -> List[int]:
		"""
		Remove a key from the structure.

		The method first checks the ideal hashed position.
		If the key is not located there, the overflow list
		for the block is searched.

		Args:
			value (str):
				Numeric key to remove.

		Returns:
			List[int]:
				List containing the global position where
				the key was removed. Returns an empty list
				if the key does not exist.

		"""
		self._validate_structure()
		self._validate_value(value)

		block_idx, offset, ideal_pos = self._locate(value)
		block = self.blocks[block_idx]
		pos_in_block = ideal_pos - offset

		if 0 <= pos_in_block < len(block) and block[pos_in_block] == value:
			block[pos_in_block] = None
			return [ideal_pos + 1]

		overflow_list = self.overflow[block_idx]
		for i, v in enumerate(overflow_list):
			if v == value:
				global_pos = self._global_position_overflow(block_idx, i)
				del overflow_list[i]
				return [global_pos]
		return []

	def sort(self) -> None:
		"""
		Sorting is not supported for hash-based external structures.

		Hash tables do not maintain ordered data, therefore
		reordering operations would break the hashing logic.

		Raises:
			NotImplementedError:
				Always raised when this method is called.

		"""
		raise NotImplementedError('Ordenar no es compatible con tablas hash externas')


class BaseConversionHash(HashFunction):
	"""
	Hash function based on base conversion and digit truncation.

	This function interprets the key digits as digits of another base
	and converts the key to its numeric representation in that base.

	The resulting number is then truncated by keeping only the least
	significant digits required to represent the table size.

	This method is commonly used in hashing techniques where keys
	are transformed into numeric values and truncated to produce
	an index within the table bounds.

	Attributes:
	    base (int):
	        Base used for the conversion process.

	"""

	def __init__(self, base: int):
		"""
		Initialize the conversion with the desired base.

		Args:
		    base (int): Base to which the key will be converted.

		"""
		self.base = base

	def hash(self, key: str, digits: int, size: int) -> int:
		"""
		Compute the hash value using base conversion.

		The key digits are interpreted as digits of the specified
		base and converted into a numeric value. The resulting
		number is then truncated to the required number of digits
		based on the table size.

		Args:
			key (str):
				Numeric key represented as a string.

			digits (int):
				Expected number of digits in the key. This value
				is not used directly but kept for interface
				compatibility.

			size (int):
				Size of the hash table.

		Returns:
			int:
				Hash value derived from the converted number.

		"""
		num = 0
		for ch in key:
			digit = int(ch)
			num = num * self.base + digit

		d = len(str(size - 1))

		s = str(num)
		if len(s) <= d:
			return num
		else:
			return int(s[-d:])
