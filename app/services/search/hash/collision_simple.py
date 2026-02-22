"""Define collision resolution strategies for open addressing hash tables.

Provide abstract and concrete implementations for resolving collisions
using linear probing, quadratic probing, and double hashing strategies.

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

from app.services.search.hash.hash_function import HashFunction


class CollisionResolver(ABC):
	"""Define interface for collision resolution strategies."""

	@abstractmethod
	def get_next(
		self,
		key: str,
		initial: int,
		attempt: int,
		size: int,
		digits: int,
	) -> int:
		"""Compute next index during collision resolution.

		Args:
		    key (str): Numeric string key being inserted or searched.
		    initial (int): Initial index produced by primary hash.
		    attempt (int): Current probing attempt number.
		    size (int): Size of the hash table.
		    digits (int): Required number of digits for the key.

		Returns:
		    int: Next index to probe (0-based).

		"""
		pass


class LinearResolver(CollisionResolver):
	"""Resolve collisions using linear probing."""

	def get_next(
		self,
		key: str,
		initial: int,
		attempt: int,
		size: int,
		digits: int,
	) -> int:
		"""Compute next index using linear increment.

		Args:
		    key (str): Numeric string key.
		    initial (int): Initial hash index.
		    attempt (int): Current probing attempt.
		    size (int): Size of the hash table.
		    digits (int): Required number of digits for the key.

		Returns:
		    int: Next index computed as (initial + attempt) % size.

		"""
		return (initial + attempt) % size


class QuadraticResolver(CollisionResolver):
	"""Resolve collisions using quadratic probing."""

	def get_next(
		self,
		key: str,
		initial: int,
		attempt: int,
		size: int,
		digits: int,
	) -> int:
		"""Compute next index using quadratic increment.

		Args:
		    key (str): Numeric string key.
		    initial (int): Initial hash index.
		    attempt (int): Current probing attempt.
		    size (int): Size of the hash table.
		    digits (int): Required number of digits for the key.

		Returns:
		    int: Next index computed as (initial + attempt^2) % size.

		"""
		return (initial + attempt * attempt) % size


class DoubleHashResolver(CollisionResolver):
	"""Resolve collisions using double hashing strategy."""

	def __init__(self, second_hash_func: HashFunction):
		"""Initialize resolver with secondary hash function.

		Args:
		    second_hash_func (HashFunction): Secondary hash strategy
		        used for generating probe sequence.

		"""
		self.second_hash = second_hash_func

	def get_next(
		self,
		key: str,
		initial: int,
		attempt: int,
		size: int,
		digits: int,
	) -> int:
		"""Compute next index using repeated secondary hashing.

		For attempt 0, return the initial index. For subsequent
		attempts, repeatedly apply the secondary hash transformation
		starting from the 1-based representation of the initial
		position.

		Args:
		    key (str): Numeric string key.
		    initial (int): Initial hash index (0-based).
		    attempt (int): Current probing attempt.
		    size (int): Size of the hash table.
		    digits (int): Required number of digits for the key.

		Returns:
		    int: Next index to probe (0-based).

		"""
		if attempt == 0:
			return initial

		current_1based = initial + 1

		for _ in range(attempt):
			numero = current_1based + 1
			raw = self.second_hash.hash(str(numero), digits, size)
			current_1based = (raw % size) + 1

		return current_1based - 1
