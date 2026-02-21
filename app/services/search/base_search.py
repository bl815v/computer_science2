"""Base abstract service for search structures with fixed-size numeric keys.

Define the BaseSearchService abstract class, which provides common
behavior for search-based data structures that store fixed-length
numeric string keys. It includes validation logic, insertion, deletion,
automatic sorting, and structural initialization. Concrete search strategies
must implement the `search` method to define how keys are located within
the internal structure.

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
from typing import List, Optional


class BaseSearchService(ABC):
	"""Abstract base class for fixed-size search structures.

	This class provides shared functionality for managing a search
	structure that stores numeric string keys of fixed length. It handles
	structure initialization, validation, insertion, deletion, and
	automatic ordering of elements.

	Attributes:
		data (List[Optional[str]]): Internal storage for the keys.
			Empty positions are represented by None.
		size (int): Maximum number of elements the structure can store.
		digits (int): Required length of each numeric key.
		initialized (bool): Indicates whether the structure has been
			initialized using the create method.

	"""

	def __init__(self) -> None:
		"""Initialize an empty, unconfigured search structure."""
		self.data: List[Optional[str]] = []
		self.size = 0
		self.digits = 0
		self.initialized = False

	def create(self, size: int, digits: int) -> None:
		"""Initialize the search structure with a fixed size and key length.

		Args:
			size (int): Maximum number of elements the structure can store.
			digits (int): Required number of digits for each key.

		Raises:
			ValueError: If size or digits is not a positive integer.

		"""
		if size <= 0:
			raise ValueError('El tamaño de la estructura debe ser un entero positivo')

		if digits <= 0:
			raise ValueError('La cantidad de dígitos debe ser un entero positivo')

		self.size = size
		self.digits = digits
		self.data = [None] * size
		self.initialized = True

	def _validate_structure(self) -> None:
		"""Validate that the structure has been initialized.

		Raises:
			ValueError: If the structure has not been initialized.

		"""
		if not self.initialized:
			raise ValueError('Estructura no inicializada')

	def _validate_value(self, value: str) -> None:
		"""Validate that a key meets the required format constraints.

		Args:
			value (str): The key to validate.

		Raises:
			ValueError: If the key does not have the required number
				of digits or contains non-numeric characters.

		"""
		if len(value) != self.digits:
			raise ValueError(f'La clave debe tener exactamente {self.digits} digitos')

		if not value.isdigit():
			raise ValueError('La clave debe ser un valor numérico')

	def insert(self, value: str) -> int:
		"""Insert a new key into the structure.

		The key is placed in the first available position and the
		structure is automatically sorted after insertion.

		Args:
			value (str): The numeric key to insert.

		Returns:
			int: The 1-based position where the key was initially inserted.

		Raises:
			ValueError: If the structure is not initialized, the key
				is invalid, already exists, or there is no available space.

		"""
		self._validate_structure()
		self._validate_value(value)

		if value in self.data:
			raise ValueError(f'La clave {value} ya existe en la estructura')

		try:
			index = self.data.index(None)
		except ValueError as exc:
			raise ValueError('No hay espacio disponible en la estructura') from exc

		self.data[index] = value
		self.sort()

		return index + 1

	def delete(self, value: str) -> List[int]:
		"""Delete all occurrences of a key from the structure.

		Args:
			value (str): The numeric key to delete.

		Returns:
			List[int]: A list of 1-based positions where the key
				was found and removed. Returns an empty list if
				the key is not present.

		Raises:
			ValueError: If the structure is not initialized.

		"""
		self._validate_structure()

		positions = self.search(value)

		if not positions:
			return []

		for pos in positions:
			self.data[pos - 1] = None

		self.sort()
		return positions

	def sort(self) -> None:
		"""Sort the structure while preserving empty positions at the end.

		Non-null values are sorted in ascending order and all None
		values are moved to the end of the internal list.

		Raises:
			ValueError: If the structure is not initialized.

		"""
		self._validate_structure()

		self.data = sorted(v for v in self.data if v is not None) + [None] * self.data.count(None)

	@abstractmethod
	def search(self, value: str) -> List[int]:
		"""Search for a key in the structure.

		This method must be implemented by subclasses to define
		the specific search strategy (e.g., linear search, binary search).

		Args:
			value (str): The numeric key to search for.

		Returns:
			List[int]: A list of 1-based positions where the key
				is found. Returns an empty list if the key is not present.

		"""
		pass
