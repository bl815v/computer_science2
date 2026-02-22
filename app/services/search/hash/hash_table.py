"""Implement configurable hash table supporting multiple collision modes.

Provide a hash table implementation that can operate without collision
strategy, with open addressing using a resolver, or with separate
chaining. Allow dynamic transition to chaining mode and support
insertion, search, and deletion operations.

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
from app.services.search.hash.collision_simple import CollisionResolver
from app.services.search.hash.hash_function import HashFunction


class CollisionWithoutStrategyError(Exception):
	"""Raise when collision occurs without a defined resolution strategy."""

	pass


class HashTable(BaseSearchService):
	"""Implement hash table with configurable collision handling.

	Support three modes:
	    - "none": No collision strategy defined.
	    - "open": Open addressing using a collision resolver.
	    - "chaining": Separate chaining with bucket lists.
	"""

	def __init__(
		self,
		hash_func: HashFunction,
		resolver: Optional[CollisionResolver] = None,
	):
		"""Initialize hash table with hash function and optional resolver.

		Args:
		    hash_func (HashFunction): Primary hash function strategy.
		    resolver (Optional[CollisionResolver]): Collision resolution
		        strategy for open addressing mode.

		"""
		super().__init__()
		self.hash_func = hash_func
		self.resolver = resolver
		self.mode = 'open' if resolver is not None else 'none'
		self._DELETED = object()

	def create(self, size: int, digits: int) -> None:
		"""Initialize internal storage based on selected mode.

		Args:
		    size (int): Number of slots in the table.
		    digits (int): Required number of digits per key.

		"""
		super().create(size, digits)

		if self.mode == 'chaining':
			self.data = [[] for _ in range(size)]
		else:
			self.data = [None] * size

	def set_chaining(self) -> None:
		"""Switch table to separate chaining mode.

		Rehash all existing keys into a new bucket-based structure.
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
			raw = self.hash_func.hash(key, self.digits, self.size)
			index = raw % self.size
			self.data[index].append(key)

	def insert(self, value: str) -> int:
		"""Insert key according to active collision strategy.

		Args:
		    value (str): Numeric key to insert.

		Returns:
		    int: 1-based position where key was inserted.

		Raises:
		    ValueError: If key already exists or no space is available.
		    CollisionWithoutStrategyError: If collision occurs and
		        no strategy is defined.

		"""
		self._validate_structure()
		self._validate_value(value)

		raw = self.hash_func.hash(value, self.digits, self.size)
		index = raw % self.size

		if self.mode == 'chaining':
			bucket = self.data[index]
			if value in bucket:
				raise ValueError(f'La clave {value} ya existe')
			bucket.append(value)
			return index + 1

		elif self.mode == 'open':
			for attempt in range(self.size):
				probe = self.resolver.get_next(value, index, attempt, self.size, self.digits)
				if self.data[probe] is None or self.data[probe] is self._DELETED:
					self.data[probe] = value
					return probe + 1
				if self.data[probe] == value:
					raise ValueError(f'La clave {value} ya existe')

			raise ValueError('No hay espacio disponible para insertar la clave')

		else:
			if self.data[index] is not None:
				if self.data[index] == value:
					raise ValueError(f'La clave {value} ya existe')
				raise CollisionWithoutStrategyError(
					f'Colisión en la dirección {index} para la clave {value}. '
					'Define una solución de colisión.'
				)

			self.data[index] = value
			return index + 1

	def search(self, value: str) -> List[int]:
		"""Search key according to active collision strategy.

		Args:
		    value (str): Numeric key to search.

		Returns:
		    List[int]: 1-based positions where key is found.

		"""
		self._validate_structure()

		raw = self.hash_func.hash(value, self.digits, self.size)
		index = raw % self.size

		if self.mode == 'chaining':
			if value in self.data[index]:
				return [index + 1]
			return []

		elif self.mode == 'open':
			positions = []
			for attempt in range(self.size):
				probe = self.resolver.get_next(value, index, attempt, self.size, self.digits)
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
		"""Delete key according to active collision strategy.

		Args:
		    value (str): Numeric key to delete.

		Returns:
		    List[int]: 1-based positions where key was removed.

		"""
		self._validate_structure()

		raw = self.hash_func.hash(value, self.digits, self.size)
		index = raw % self.size

		if self.mode == 'chaining':
			bucket = self.data[index]
			if value in bucket:
				bucket.remove(value)
				return [index + 1]
			return []

		elif self.mode == 'open':
			positions = []
			for attempt in range(self.size):
				probe = self.resolver.get_next(value, index, attempt, self.size, self.digits)
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

		Raises:
		    NotImplementedError: Always raised because sorting
		        is not supported for hash tables.

		"""
		raise NotImplementedError('Ordenar no es compatible con tablas hash')
