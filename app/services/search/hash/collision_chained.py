"""Implement hash table variants using chaining and nested fixed-size buckets.

Provide concrete hash table implementations based on separate chaining
and nested array buckets. Both rely on a configurable hash function
strategy and extend the base search service structure.

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
from app.services.search.hash.hash_function import HashFunction


class ChainedHashTable(BaseSearchService):
	"""Implement hash table using separate chaining strategy.

	Store elements in buckets represented as dynamic Python lists.
	Each index in the main table contains a list of keys that share
	the same hash index.
	"""

	def __init__(self, hash_func: HashFunction):
		"""Initialize table with a hash function strategy.

		Args:
		    hash_func (HashFunction): Hash function used to compute indices.

		"""
		super().__init__()
		self.hash_func = hash_func
		self.data: List[List[str]] = []

	def create(self, size: int, digits: int) -> None:
		"""Initialize table with empty chaining buckets.

		Args:
		    size (int): Number of buckets in the table.
		    digits (int): Required number of digits per key.

		"""
		super().create(size, digits)
		self.data = [[] for _ in range(size)]

	def insert(self, value: str) -> int:
		"""Insert key into corresponding chaining bucket.

		Args:
		    value (str): Numeric key to insert.

		Returns:
		    int: 1-based index of the bucket.

		Raises:
		    ValueError: If key already exists.

		"""
		self._validate_structure()
		self._validate_value(value)

		raw = self.hash_func.hash(value, self.digits, self.size)
		index = raw % self.size
		bucket = self.data[index]

		if value in bucket:
			raise ValueError(f'La clave {value} ya existe')

		bucket.append(value)
		return index + 1

	def search(self, value: str) -> List[int]:
		"""Search key within its corresponding bucket.

		Args:
		    value (str): Numeric key to search.

		Returns:
		    List[int]: 1-based bucket index if found, otherwise empty list.

		"""
		self._validate_structure()

		raw = self.hash_func.hash(value, self.digits, self.size)
		index = raw % self.size

		if value in self.data[index]:
			return [index + 1]

		return []

	def delete(self, value: str) -> List[int]:
		"""Remove key from its corresponding bucket.

		Args:
		    value (str): Numeric key to delete.

		Returns:
		    List[int]: 1-based bucket index if removed, otherwise empty list.

		"""
		self._validate_structure()

		raw = self.hash_func.hash(value, self.digits, self.size)
		index = raw % self.size
		bucket = self.data[index]

		if value in bucket:
			bucket.remove(value)
			return [index + 1]

		return []

	def sort(self) -> None:
		"""Disable sorting for chained hash tables.

		Raises:
		    NotImplementedError: Always raised because sorting
		        is not supported for this structure.

		"""
		raise NotImplementedError('Ordenar no es compatible con tablas hash encadenadas')


class NestedArrayHashTable(BaseSearchService):
	"""Implement hash table using fixed-size nested array buckets.

	Store elements in buckets of predefined capacity. Each bucket
	is a list of fixed length initialized with None values.
	"""

	def __init__(self, hash_func: HashFunction, bucket_size: int):
		"""Initialize table with hash function and bucket size.

		Args:
		    hash_func (HashFunction): Hash function used to compute indices.
		    bucket_size (int): Maximum number of elements per bucket.

		"""
		super().__init__()
		self.hash_func = hash_func
		self.bucket_size = bucket_size
		self.data: List[List[Optional[str]]] = []

	def create(self, size: int, digits: int) -> None:
		"""Initialize table with fixed-size buckets.

		Args:
		    size (int): Number of buckets in the table.
		    digits (int): Required number of digits per key.

		"""
		super().create(size, digits)
		self.data = [[None] * self.bucket_size for _ in range(size)]

	def insert(self, value: str) -> int:
		"""Insert key into first available slot of its bucket.

		Args:
		    value (str): Numeric key to insert.

		Returns:
		    int: 1-based bucket index.

		Raises:
		    ValueError: If key already exists or bucket is full.

		"""
		self._validate_structure()
		self._validate_value(value)

		raw = self.hash_func.hash(value, self.digits, self.size)
		index = raw % self.size
		bucket = self.data[index]

		if value in bucket:
			raise ValueError(f'La clave {value} ya existe')

		for i, slot in enumerate(bucket):
			if slot is None:
				bucket[i] = value
				return index + 1

		raise ValueError(f'Lista {index} llena')

	def search(self, value: str) -> List[int]:
		"""Search key within its corresponding bucket.

		Args:
		    value (str): Numeric key to search.

		Returns:
		    List[int]: 1-based bucket index if found, otherwise empty list.

		"""
		self._validate_structure()

		raw = self.hash_func.hash(value, self.digits, self.size)
		index = raw % self.size

		if value in self.data[index]:
			return [index + 1]

		return []

	def delete(self, value: str) -> List[int]:
		"""Remove key from its corresponding bucket.

		Args:
		    value (str): Numeric key to delete.

		Returns:
		    List[int]: 1-based bucket index if removed, otherwise empty list.

		"""
		self._validate_structure()

		raw = self.hash_func.hash(value, self.digits, self.size)
		index = raw % self.size
		bucket = self.data[index]

		for i, slot in enumerate(bucket):
			if slot == value:
				bucket[i] = None
				return [index + 1]

		return []

	def sort(self) -> None:
		"""Disable sorting for nested-array hash tables.

		Raises:
		    NotImplementedError: Always raised because sorting
		        is not supported for this structure.

		"""
		raise NotImplementedError('Ordenar no es compatible con tablas hash de arreglos anidados')
