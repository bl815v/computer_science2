"""Define hash function strategies for fixed-size hash structures.

Provide abstract and concrete hash function implementations such as
mod, square, truncation, and folding. Each strategy transforms a
numeric string key into an integer index candidate.

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

from abc import ABC, abstractmethod
from typing import List


class HashFunction(ABC):
	"""Define interface for hash function strategies."""

	@abstractmethod
	def hash(self, key: str, digits: int, size: int) -> int:
		"""Compute hash value for a given key.

		Args:
		    key (str): Numeric string key.
		    digits (int): Required number of digits for the key.
		    size (int): Size of the hash table.

		Returns:
		    int: Computed hash value.

		"""
		pass


class ModHash(HashFunction):
	"""Implement direct modulo-style hash strategy.

	Convert the key directly to integer form.
	"""

	def hash(self, key: str, digits: int, size: int) -> int:
		"""Return integer representation of the key.

		Args:
		    key (str): Numeric string key.
		    digits (int): Required number of digits for the key.
		    size (int): Size of the hash table.

		Returns:
		    int: Integer value of the key.

		"""
		return int(key)


class SquareHash(HashFunction):
	"""Implement middle-square hash strategy."""

	def hash(self, key: str, digits: int, size: int) -> int:
		"""Extract middle digits from squared key.

		Square the numeric key and extract a centered substring
		whose length matches the number of digits required to
		represent the largest possible index.

		Args:
		    key (str): Numeric string key.
		    digits (int): Required number of digits for the key.
		    size (int): Size of the hash table.

		Returns:
		    int: Extracted middle portion of the squared key.

		"""
		d = len(str(size - 1))
		num = int(key)
		square = num * num
		s = str(square)

		if len(s) <= d:
			return int(s)

		start = (len(s) - d) // 2
		middle = s[start : start + d]
		return int(middle)


class TruncationHash(HashFunction):
	"""Implement truncation hash strategy based on selected positions."""

	def __init__(self, positions: List[int]):
		"""Initialize truncation strategy.

		Args:
		    positions (List[int]): 1-based digit positions to extract.

		"""
		self.positions = positions

	def hash(self, key: str, digits: int, size: int) -> int:
		"""Build hash using selected digit positions.

		Args:
		    key (str): Numeric string key.
		    digits (int): Required number of digits for the key.
		    size (int): Size of the hash table.

		Returns:
		    int: Integer formed by concatenating selected digits.

		"""
		selected = ''.join(key[p - 1] for p in self.positions)
		return int(selected)


class FoldingHash(HashFunction):
	"""Implement folding hash strategy using grouping and aggregation."""

	def __init__(self, group_size: int, operation: str = 'sum'):
		"""Initialize folding strategy.

		Args:
		    group_size (int): Number of digits per group.
		    operation (str): Aggregation method, either "sum" or "mul".

		Raises:
		    ValueError: If operation is not supported.

		"""
		self.group_size = group_size
		self.operation = operation.lower()

		if self.operation not in ('sum', 'mul'):
			raise ValueError("La operación debe ser 'sum' o 'mul'")

	def hash(self, key: str, digits: int, size: int) -> int:
		"""Compute hash by grouping digits and aggregating results.

		Split the key into groups of fixed size, then combine
		the groups using either summation or multiplication.
		Extract the last required digits based on table size.

		Args:
		    key (str): Numeric string key.
		    digits (int): Required number of digits for the key.
		    size (int): Size of the hash table.

		Returns:
		    int: Folded hash value.

		"""
		d = len(str(size - 1))
		groups = []

		for i in range(0, len(key), self.group_size):
			groups.append(int(key[i : i + self.group_size]))

		if self.operation == 'sum':
			total = sum(groups)
		else:
			total = 1
			for g in groups:
				total *= g

		s = str(total)

		if len(s) <= d:
			return total

		return int(s[-d:])
