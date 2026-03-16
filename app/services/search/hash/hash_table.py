"""
Hash table implementation with configurable collision handling.

This module provides a hash table implementation that supports multiple
collision resolution strategies. The table can operate in three different
modes depending on the configuration:

    - none:
        No collision resolution is used. If a collision occurs, an
        exception is raised.

    - open:
        Open addressing is used. Collisions are resolved using a probing
        strategy provided by a CollisionResolver implementation.

    - chaining:
        Separate chaining is used. Each position in the table stores a
        list (bucket) containing all keys that hash to that index.

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

from app.services.search.base_search import BaseSearchService
from app.services.search.hash.abstract_hash import HashMixin
from app.services.search.hash.collision_simple import CollisionResolver
from app.services.search.hash.hash_function import HashFunction


class CollisionWithoutStrategyError(Exception):
	"""Exception raised when a collision occurs without a strategy.

	This error is triggered when the hash table operates in **"none"**
	mode and two different keys map to the same position. Since no
	collision resolution strategy exists in this mode, the operation
	cannot proceed.
	"""

	pass


class HashTable(BaseSearchService, HashMixin):
	"""Hash table with configurable collision resolution.

	This class implements a hash table capable of operating under
	different collision handling strategies. The strategy used depends
	on the configuration provided during initialization.

	Supported modes:

	    - **none**
	        No collision handling. Any collision raises an exception.

	    - **open**
	        Open addressing using a probing strategy defined by a
	        CollisionResolver implementation.

	    - **chaining**
	        Separate chaining, where each table position stores a list
	        of keys that share the same hash index.

	The table stores keys as strings and returns positions using
	1-based indexing to match the interface expected by the rest of
	the system.

	Inheritance:
	    BaseSearchService:
	        Provides structure validation and common search interface.

	    HashMixin:
	        Provides hash computation and probing utilities.
	"""

	def __init__(self, hash_func: HashFunction, resolver: Optional[CollisionResolver] = None):
		"""Initialize the hash table.

		Args:
		    hash_func (HashFunction):
		        Hash function used to compute key positions.

		    resolver (Optional[CollisionResolver]):
		        Collision resolution strategy used for open addressing.
		        If not provided, the table operates in "none" mode.

		"""
		BaseSearchService.__init__(self)
		HashMixin.__init__(self, hash_func, resolver)

	def create(self, size: int, digits: int) -> None:
		"""Initialize the hash table structure.

		This method allocates the internal storage and prepares the
		table for operations. The internal representation depends on
		the collision handling mode.

		Args:
		    size (int):
		        Number of slots in the hash table.

		    digits (int):
		        Number of digits used for validating keys.

		"""
		super().create(size, digits)

		if self.mode == 'chaining':
			self.data = [[] for _ in range(size)]
		else:
			self.data = [None] * size

	def set_chaining(self) -> None:
		"""Convert the table to separate chaining mode.

		All existing keys are rehashed into a new structure where
		each table index contains a list (bucket). Any previous
		probing or open addressing configuration is removed.
		"""
		if self.mode == 'chaining':
			return

		keys = []
		if self.mode == 'open':
			for item in self.data:
				if item is not None and item is not self._DELETED:
					keys.append(item)
		else:
			for item in self.data:
				if item is not None:
					keys.append(item)

		self.data = [[] for _ in range(self.size)]
		self.mode = 'chaining'
		self.resolver = None

		for key in keys:
			index = self._compute_raw_hash(key, self.digits, self.size)
			self.data[index].append(key)

	def insert(self, value: str) -> int:
		"""Insert a key into the hash table.

		The insertion process depends on the collision handling mode:

		    - chaining:
		        The key is appended to the bucket at the computed index.

		    - open:
		        Probing is used to locate an available slot.

		    - none:
		        If a collision occurs, an exception is raised.

		Args:
		    value (str):
		        Key to insert into the table.

		Returns:
		    int:
		        The 1-based position where the key was inserted.

		Raises:
		    ValueError:
		        If the key already exists or the table is full.

		    CollisionWithoutStrategyError:
		        If a collision occurs while operating in "none" mode.

		"""
		self._validate_structure()
		self._validate_value(value)

		index = self._compute_raw_hash(value, self.digits, self.size)

		if self.mode == 'chaining':
			bucket = self.data[index]
			if value in bucket:
				raise ValueError(f'La clave {value} ya existe')
			bucket.append(value)
			return index + 1

		elif self.mode == 'open':
			for attempt in range(self.size):
				probe = self._probe(value, index, attempt, self.size, self.digits)
				if self.data[probe] is None or self.data[probe] is self._DELETED:
					self.data[probe] = value
					return probe + 1
				if self.data[probe] == value:
					raise ValueError(f'La clave {value} ya existe')
			raise ValueError('No hay espacio disponible para insertar la clave')

		else:  # modo 'none'
			if self.data[index] is not None:
				if self.data[index] == value:
					raise ValueError(f'La clave {value} ya existe')

				raise CollisionWithoutStrategyError(
					f'Colisión en la dirección {index + 1} para la clave {value}. '
					'Define una solución de colisión.'
				)
			self.data[index] = value
			return index + 1

	def search(self, value: str) -> List[int]:
		"""Search for a key in the hash table.

		Args:
		    value (str):
		        Key to search for.

		Returns:
		    List[int]:
		        List of positions (1-based) where the key was found.
		        The list is empty if the key does not exist.

		"""
		self._validate_structure()
		index = self._compute_raw_hash(value, self.digits, self.size)

		if self.mode == 'chaining':
			if value in self.data[index]:
				return [index + 1]
			return []

		elif self.mode == 'open':
			positions = []
			for attempt in range(self.size):
				probe = self._probe(value, index, attempt, self.size, self.digits)
				if self.data[probe] is None:
					break
				if self.data[probe] == value:
					positions.append(probe + 1)
			return positions

		else:
			if self.data[index] == value:
				return [index + 1]
			return []

	def delete(self, value: str) -> List[int]:
		"""Remove a key from the hash table.

		Args:
		    value (str):
		        Key to remove from the table.

		Returns:
		    List[int]:
		        List of positions (1-based) where the key was removed.
		        The list is empty if the key was not found.

		"""
		self._validate_structure()
		index = self._compute_raw_hash(value, self.digits, self.size)

		if self.mode == 'chaining':
			bucket = self.data[index]
			if value in bucket:
				bucket.remove(value)
				return [index + 1]
			return []

		elif self.mode == 'open':
			positions = []
			for attempt in range(self.size):
				probe = self._probe(value, index, attempt, self.size, self.digits)
				if self.data[probe] is None:
					break
				if self.data[probe] == value:
					self.data[probe] = self._DELETED
					positions.append(probe + 1)
			return positions

		else:
			if self.data[index] == value:
				self.data[index] = None
				return [index + 1]
			return []

	def sort(self) -> None:
		"""Disable sorting for hash tables.

		Hash tables do not maintain a global ordering of keys, so
		sorting is not supported.

		Raises:
		    NotImplementedError:
		        Always raised when the method is called.

		"""
		raise NotImplementedError('Ordenar no es compatible con tablas hash')
