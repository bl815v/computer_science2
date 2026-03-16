"""
Hash utilities shared across hash-based search structures.

This module defines a mixin that provides common functionality used
by different hash table implementations. The mixin centralizes logic
related to hash computation and collision probing so it can be reused
by multiple structures without duplicating code.

The mixin does not implement a full hash table. Instead, it provides
support utilities that other classes can combine with their own
storage logic.

Key responsibilities include:

	- Computing normalized hash values.
	- Handling probing for open addressing strategies.
	- Managing configuration for collision resolution.

Classes using this mixin are expected to define their own storage
mechanism and operations such as insert, search, and delete.

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

from typing import Optional

from app.services.search.hash.collision_simple import CollisionResolver
from app.services.search.hash.hash_function import HashFunction


class HashMixin:
	"""Provide shared hashing behavior for hash-based structures.

	This mixin encapsulates common operations required by hash tables,
	such as computing normalized hash values and determining the next
	probing position when collisions occur.

	It supports two main modes of operation:

		- **none**:
			No collision resolution strategy is defined. The hash
			position is used directly.

		- **open**:
			Open addressing is used and probing positions are generated
			using the provided collision resolver.

	The mixin does not manage storage. Instead, it supplies helper
	methods that other classes can call while implementing their
	own insertion and search algorithms.

	Attributes:
		hash_func (HashFunction):
			Hash function used to compute raw hash values.

		resolver (Optional[CollisionResolver]):
			Strategy used to compute the next probe location when
			collisions occur.

		mode (str):
			Operating mode of the hash structure. Possible values:

				- "none": no collision handling
				- "open": open addressing with probing

		_DELETED (object):
			Sentinel marker used to represent deleted entries in
			open addressing tables.

	"""

	def __init__(self, hash_func: HashFunction, resolver: Optional[CollisionResolver] = None):
		"""Initialize the hash mixin.

		Args:
			hash_func (HashFunction):
				Hash function used to compute raw hash values.

			resolver (Optional[CollisionResolver]):
				Collision resolution strategy used for open
				addressing probing. If not provided, the structure
				operates without collision handling.

		"""
		self.hash_func = hash_func
		self.resolver = resolver
		self.mode = 'open' if resolver is not None else 'none'
		self._DELETED = object()

	def _compute_raw_hash(self, value: str, digits: int, size: int) -> int:
		"""Compute a normalized hash value within table bounds.

		The raw hash produced by the hash function may exceed the
		table size. This method ensures the returned value falls
		within the valid index range.

		Args:
			value (str):
				Key to be hashed.

			digits (int):
				Number of digits used by the hash function.

			size (int):
				Size of the hash table.

		Returns:
			int:
				Normalized hash index in the range ``[0, size - 1]``.

		"""
		raw = self.hash_func.hash(value, digits, size)
		return raw % size

	def _probe(self, value: str, start_index: int, attempt: int, size: int, digits: int) -> int:
		"""Compute the next probing position for open addressing.

		If a collision resolver is configured, the next index is
		calculated using the resolver's probing strategy
		(e.g., linear probing, quadratic probing, or double hashing).

		If no resolver is defined, the original hash position is
		returned unchanged.

		Args:
		    value (str):
		        Key being inserted or searched.

		    start_index (int):
		        Initial hash position.

		    attempt (int):
		        Current probing attempt number.

		    size (int):
		        Size of the hash table.

		    digits (int):
		        Number of digits used by the hash function.

		Returns:
		    int:
		        Next index to probe in the table.

		"""
		if self.mode == 'open' and self.resolver:
			return self.resolver.get_next(value, start_index, attempt, size, digits)
		return start_index
