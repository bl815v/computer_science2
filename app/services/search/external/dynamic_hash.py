"""
Dynamic external hash structure with automatic resizing.

This module implements a dynamic external hash table that grows or
shrinks based on the current load factor. Keys are distributed into
buckets (blocks) determined by a hash function.

Each bucket has a fixed capacity. When a bucket becomes full, additional
keys are stored in an overflow list associated with that bucket.

The number of buckets may change dynamically depending on the selected
expansion policy and load thresholds.

Supported expansion policies:

    - total:
        The number of buckets doubles or halves during resizing.

    - partial:
        Buckets grow in intermediate steps (B → B + B/2 → 2B) to
        provide smoother expansion and reduction behavior.

The structure automatically rehashes all stored keys whenever the
number of buckets changes.

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

from typing import Dict, List, Optional

from app.services.search.external.base_external import BaseSearchService
from app.services.search.external.hash_external import HashExternalSearch
from app.services.search.hash.hash_function import HashFunction


class DynamicHashExternalSearch(BaseSearchService):
	"""Dynamic external hash structure with bucket resizing.

	This structure distributes keys into buckets using a hash function.
	Each bucket contains a fixed-size main block and an overflow list
	that stores additional elements when the block becomes full.

	The table automatically expands or shrinks depending on its
	current load factor.

	Load factor:

	    load_factor = number_of_elements / total_capacity

	Resizing occurs when the load factor crosses the configured
	expansion or reduction thresholds.

	Attributes:
	    hash_func (HashFunction):
	        Hash function used to determine the bucket index.

	    initial_num_buckets (int):
	        Initial number of buckets created during initialization.

	    bucket_size (int):
	        Maximum number of elements stored in each bucket's main block.

	    expansion_policy (str):
	        Strategy used to determine how the number of buckets grows.
	        Supported values are "total" and "partial".

	    expansion_threshold (float):
	        Load factor threshold that triggers expansion.

	    reduction_threshold (float):
	        Load factor threshold that triggers reduction.

	    current_num_buckets (int):
	        Current number of buckets in the structure.

	    blocks (List[List[Optional[str]]]):
	        Main storage blocks for each bucket.

	    overflow (List[List[str]]):
	        Overflow lists used when blocks become full.

	    size (int):
	        Total storage capacity (buckets * bucket_size).

	    digits (int):
	        Number of digits required for key validation.

	    _count (int):
	        Current number of stored keys.

	"""

	def __init__(
		self,
		hash_func: HashFunction,
		initial_num_buckets: int,
		bucket_size: int,
		expansion_policy: str = 'total',
		expansion_threshold: float = 0.75,
		reduction_threshold: float = 0.5,
	):
		"""Initialize the dynamic external hash structure.

		Args:
		    hash_func (HashFunction):
		        Hash function used to map keys to buckets.

		    initial_num_buckets (int):
		        Initial number of buckets created.

		    bucket_size (int):
		        Capacity of each bucket's main block.

		    expansion_policy (str):
		        Bucket expansion strategy. Supported values are
		        "total" and "partial".

		    expansion_threshold (float):
		        Load factor that triggers expansion.

		    reduction_threshold (float):
		        Load factor that triggers reduction.

		"""
		super().__init__()
		self.hash_func = hash_func
		self.initial_num_buckets = initial_num_buckets
		self.bucket_size = bucket_size
		self.expansion_policy = expansion_policy.lower()
		self.expansion_threshold = expansion_threshold
		self.reduction_threshold = reduction_threshold
		self.current_num_buckets = initial_num_buckets
		self._count = 0

		self.blocks: List[List[Optional[str]]] = []
		self.overflow: List[List[str]] = []
		self.size: int = 0
		self.digits: int = 0

	def create(self, size: int = None, digits: int = None) -> None:
		"""Initialize the internal structure.

		This method creates the initial bucket structure and
		configures the capacity of each bucket.

		Args:
		    size (int):
		        Ignored parameter kept for compatibility with
		        the base class interface.

		    digits (int):
		        Number of digits required for key validation.

		Raises:
		    ValueError:
		        If the number of digits is not provided.

		"""
		if digits is None:
			raise ValueError('Se requiere el número de dígitos')

		total_size = self.initial_num_buckets * self.bucket_size

		super().create(total_size, digits)

		self.blocks = [[None] * self.bucket_size for _ in range(self.initial_num_buckets)]
		self.overflow = [[] for _ in range(self.initial_num_buckets)]
		self.current_num_buckets = self.initial_num_buckets
		self._count = 0

	def _bucket_for(self, value: str) -> int:
		"""Compute the bucket index for a given key.

		Args:
		    value (str):
		        Key to hash.

		Returns:
		    int:
		        Index of the bucket where the key should be stored.

		"""
		return (
			self.hash_func.hash(value, self.digits, self.current_num_buckets)
			% self.current_num_buckets
		)

	def _global_position(self, bucket_idx: int, slot_idx: int, overflow_idx: int = -1) -> int:
		"""Compute the global position of an element.

		The structure reports positions using 1-based indexing.

		Args:
		    bucket_idx (int):
		        Bucket index.

		    slot_idx (int):
		        Position inside the bucket block.

		    overflow_idx (int):
		        Position inside the overflow list. If -1, the
		        element is located in the main block.

		Returns:
		    int:
		        Global 1-based position of the element.

		"""
		if overflow_idx == -1:
			return bucket_idx * self.bucket_size + slot_idx + 1
		else:
			total_principal = self.current_num_buckets * self.bucket_size
			overflow_before = sum(len(self.overflow[i]) for i in range(bucket_idx))
			return total_principal + overflow_before + overflow_idx + 1

	def search(self, value: str) -> List[Dict[str, int]]:
		"""Search for a key in the structure.

		Args:
		    value (str):
		        Key to search.

		Returns:
		    List[Dict[str, int]]:
		        A list containing the location information of the key.
		        The list is empty if the key does not exist.

		"""
		self._validate_structure()
		self._validate_value(value)

		bucket_idx = self._bucket_for(value)

		for i, v in enumerate(self.blocks[bucket_idx]):
			if v == value:
				return [
					{
						'global_position': self._global_position(bucket_idx, i),
						'block_index': bucket_idx + 1,
						'block_position': i + 1,
					}
				]

		for i, v in enumerate(self.overflow[bucket_idx]):
			if v == value:
				return [
					{
						'global_position': self._global_position(bucket_idx, -1, i),
						'block_index': bucket_idx + 1,
						'block_position': i + 1,
					}
				]

		return []

	def insert(self, value: str) -> int:
		"""Insert a key into the structure.

		If the load factor exceeds the expansion threshold,
		the structure may resize before inserting the new key.

		Args:
		    value (str):
		        Key to insert.

		Returns:
		    int:
		        Global 1-based position where the key was stored.

		Raises:
		    ValueError:
		        If the key already exists.

		"""
		self._validate_structure()
		self._validate_value(value)

		if self.search(value):
			raise ValueError(f'La clave {value} ya existe')

		if (self._count + 1) / self.size > self.expansion_threshold:
			new_buckets = self._next_bucket_count()
			if new_buckets is not None:
				self._resize(new_buckets)
				bucket_idx = self._bucket_for(value)
			else:
				bucket_idx = self._bucket_for(value)
		else:
			bucket_idx = self._bucket_for(value)

		block = self.blocks[bucket_idx]

		for i in range(len(block)):
			if block[i] is None:
				block[i] = value
				self._count += 1
				return self._global_position(bucket_idx, i)

		self.overflow[bucket_idx].append(value)
		self._count += 1
		return self._global_position(bucket_idx, -1, len(self.overflow[bucket_idx]) - 1)

	def delete(self, value: str) -> List[int]:
		"""Remove a key from the structure.

		Args:
		    value (str):
		        Key to remove.

		Returns:
		    List[int]:
		        List containing the global position where the
		        key was removed. Returns an empty list if the
		        key does not exist.

		"""
		self._validate_structure()
		if not self.search(value):
			return []

		bucket_idx = self._bucket_for(value)
		block = self.blocks[bucket_idx]

		for i in range(len(block)):
			if block[i] == value:
				block[i] = None
				self._count -= 1
				pos = self._global_position(bucket_idx, i)
				self._maybe_reduce()
				return [pos]

		overflow = self.overflow[bucket_idx]
		for i in range(len(overflow)):
			if overflow[i] == value:
				del overflow[i]
				self._count -= 1
				pos = self._global_position(bucket_idx, -1, i)
				self._maybe_reduce()
				return [pos]

		return []

	def sort(self) -> None:
		"""Disable sorting for dynamic hash structures.

		Raises:
		    NotImplementedError:
		        Always raised when called.

		"""
		raise NotImplementedError('Ordenar no es compatible con tablas hash dinámicas')

	def _maybe_reduce(self) -> None:
		"""Reduce the number of buckets if the load factor is below the reduction threshold.

		This method checks the current load factor of the structure. If the ratio
		between stored elements and total capacity is less than or equal to the
		configured reduction threshold, the structure attempts to decrease the
		number of buckets.

		The new bucket count is determined using the configured reduction policy.
		If a valid previous bucket count exists, the structure is resized and all
		keys are rehashed into the new configuration.
		"""
		if self._count / self.size <= self.reduction_threshold:
			new_buckets = self._prev_bucket_count()
			if new_buckets is not None:
				self._resize(new_buckets)

	def _next_bucket_count(self) -> Optional[int]:
		"""Calculate the next bucket count according to the expansion policy.

		Returns:
			Optional[int]: The new number of buckets if expansion is possible,
			otherwise None.

		Notes:
			Two expansion policies are supported:

			- ``total``: The number of buckets doubles each time the structure
			expands.

			- ``partial``: The number of buckets grows in intermediate steps
			between powers of two using the following sequence:

				B → B + B/2 → 2B

			where ``B`` represents a power-of-two multiple of the initial
			number of buckets. This allows more gradual growth of the
			structure.

		"""
		curr = self.current_num_buckets
		if self.expansion_policy == 'total':
			return curr * 2
		else:
			base = self.initial_num_buckets
			k = 0
			while base * (1 << (k + 1)) <= curr:
				k += 1
			B = base * (1 << k)
			if curr == B:
				return B + B // 2
			elif curr == B + B // 2:
				return 2 * B
			else:
				return curr * 2

	def _prev_bucket_count(self) -> Optional[int]:
		"""Calculate the previous bucket count according to the reduction policy.

		Returns:
			Optional[int]: The previous valid number of buckets if reduction
			is allowed, otherwise None.

		Notes:
			- The number of buckets will never be reduced below the initial
			number defined when the structure was created.
			- For the ``total`` policy, the bucket count is halved.
			- For the ``partial`` policy, the structure reverses the same
			intermediate steps used during expansion:

				2B → B + B/2 → B

			If the current size is already the base level and cannot be
			reduced further, the method returns None.

		"""
		curr = self.current_num_buckets
		if curr <= self.initial_num_buckets:
			return None
		if self.expansion_policy == 'total':
			return curr // 2
		else:
			base = self.initial_num_buckets
			k = 0
			while base * (1 << (k + 1)) < curr:
				k += 1
			B = base * (1 << k)
			if curr == 2 * B:
				return B + B // 2
			elif curr == B + B // 2:
				return B
			elif curr == B:
				if B == base:
					return None
				prev_B = B // 2
				return prev_B + prev_B // 2
			else:
				return None

	def _resize(self, new_num_buckets: int) -> None:
		"""Resize the hash structure and rehash all stored keys.

		This method rebuilds the internal bucket structure using the specified
		number of buckets. All existing keys are collected and reinserted
		according to the new hash distribution.

		The process consists of three main steps:

		1. Collect all keys currently stored in both primary blocks and
		overflow lists.
		2. Create new empty bucket structures with the updated size.
		3. Rehash and insert every key into the new structure.

		If a primary bucket is full during reinsertion, the key is placed in
		the corresponding overflow list.

		Args:
			new_num_buckets (int): The new number of buckets to allocate.

		"""
		keys = []
		for block in self.blocks:
			for v in block:
				if v is not None:
					keys.append(v)
		for ov in self.overflow:
			keys.extend(ov)

		new_blocks = [[None] * self.bucket_size for _ in range(new_num_buckets)]
		new_overflow = [[] for _ in range(new_num_buckets)]

		for key in keys:
			bucket = self.hash_func.hash(key, self.digits, new_num_buckets) % new_num_buckets

			placed = False
			for i in range(self.bucket_size):
				if new_blocks[bucket][i] is None:
					new_blocks[bucket][i] = key
					placed = True
					break
			if not placed:
				new_overflow[bucket].append(key)

		self.blocks = new_blocks
		self.overflow = new_overflow
		self.size = new_num_buckets * self.bucket_size
		self.current_num_buckets = new_num_buckets
