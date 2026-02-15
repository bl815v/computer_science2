"""Provide binary search operations for fixed-size numeric arrays.

The BinarySearchService provides a simple data structure simulation for binary search
with fixed-size arrays and digit-constrained numeric values. It supports creation,
insertion, search, and deletion operations with proper validation.

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


class BinarySearchService:
	"""Service class for binary search operations on a fixed-size numeric array.

	This class manages a data structure where values are stored in a fixed-size
	array. All values must be numeric strings with exactly the specified number
	of digits. The class provides methods to create, insert, search, and delete
	values using binary search algorithms.

	Attributes:
	    data (List[Optional[str]]): The underlying array storing the values.
	    size (int): The maximum capacity of the data structure.
	    digits (int): The exact number of digits required for each value.
	    initialized (bool): Whether the structure has been properly initialized.

	"""

	def __init__(self) -> None:
		"""Initialize a new BinarySearchService instance.

		Sets up an empty data structure with default values and marks it
		as uninitialized until the create() method is called.
		"""
		self.data: List[Optional[str]] = []
		self.size = 0
		self.digits = 0
		self.initialized = False
		print('BinarySearchService initialized')

	def create(self, size: int, digits: int) -> None:
		"""Create and initializes the binary search data structure.

		Sets up a fixed-size array with the specified dimensions and constraints.

		Args:
		    size (int): The maximum number of elements the structure can hold.
		    digits (int): The exact number of digits each value must have.

		Returns:
		    None

		Raises:
		    ValueError: If size or digits are not positive integers.

		"""
		if size <= 0:
			raise ValueError('El tamaño de la estructura debe ser positivo')
		if digits <= 0:
			raise ValueError('La cantidad de dígitos debe ser positiva')

		self.size = size
		self.digits = digits
		self.data = [None] * size
		self.initialized = True
		print(f'Estructura creada: tamaño={size}, digitos={digits}')

	def insert(self, value: str) -> int:
		"""Insert a value into the first available position in the array.

		Validates the value against the structure's constraints and ensures
		the value doesn't already exist in the array.

		Args:
		    value (str): The numeric string value to insert.

		Returns:
		    int: The 1-based index position where the value was inserted.

		Raises:
		    ValueError: If the structure is not initialized, value doesn't
		               match digit constraint, value is not numeric, value
		               already exists, or no space is available.

		"""
		if not self.initialized:
			raise ValueError('Estructura no inicializada. Usa create() primero.')

		if len(value) != self.digits:
			raise ValueError(f'La clave debe ser de exactamente {self.digits} digitos')

		if not value.isdigit():
			raise ValueError('La clave debe ser numerica')

		if value in self.data:
			print(f'Clave {value} ya existe en la estructura: {self.data}')
			raise ValueError(f'La clave {value} ya existe')

		try:
			index = self.data.index(None)
		except ValueError as exc:
			raise ValueError('No hay espacio disponible') from exc

		self.data[index] = value
		self.sort()
		print(f'Clave {value} insertada en la dirección {index + 1}')
		print(f'Clave {value} en la dirección {self.search(value)} luego de ordenar')
		return index + 1

	def search(self, value: str) -> List[int]:
		"""Search for all occurrences of a value in the array.

		Performs a binary search through the array and returns all positions
		where the value is found. Returns an empty list if the value is not
		found or if the structure is not properly initialized.

		Args:
		    value (str): The value to search for.

		Returns:
		    List[int]: List of 1-based index positions where the value was found.
		              Returns empty list if value not found or structure invalid.

		"""
		if not self.initialized:
			return []

		if len(value) != self.digits:
			return []

		if not value.isdigit():
			return []

		valid_data = [v for v in self.data if v is not None]

		left = 0
		right = len(valid_data) - 1
		found_index = -1

		while left <= right:
			mid = (left + right) // 2

			if valid_data[mid] == value:
				found_index = mid
				break
			elif valid_data[mid] < value:
				left = mid + 1
			else:
				right = mid - 1

		if found_index == -1:
			return []

		positions = []

		i = found_index
		while i >= 0 and valid_data[i] == value:
			i -= 1
		i += 1

		while i < len(valid_data) and valid_data[i] == value:
			positions.append(i + 1)
			i += 1

		print(f'Clave {value} encontrada en la dirección: {positions}')
		return positions

	def delete(self, value: str) -> List[int]:
		"""Delete all occurrences of a value from the array.

		Performs a binary search and removes all instances of the specified value
		by setting their positions to None. Returns the positions where deletions
		occurred.

		Args:
		    value (str): The value to delete from the array.

		Returns:
		    List[int]: List of 1-based index positions where the value was deleted.
		              Returns empty list if value not found or structure invalid.

		"""
		if not self.initialized:
			return []

		positions = self.search(value)

		if not positions:
			print(f'Clave {value} no encontrada para eliminar')
			return []

		for pos in positions:
			self.data[pos - 1] = None

		self.sort()
		print(f'Clave {value} eliminada de la dirección: {positions}')
		return positions

	def sort(self) -> None:
		"""Sort the values in the array in ascending order.

		Sorts the non-None values in the array while keeping None values at the end.
		Does not return anything but modifies the internal state of the data structure.

		Returns:
		    None

		Raises:
		    ValueError: If the structure is not initialized.

		"""
		if not self.initialized:
			raise ValueError('Estructura no inicializada. Usa create() primero.')

		self.data = sorted((v for v in self.data if v is not None)) + [None] * self.data.count(None)
		print(f'Estructura ordenada: {self.data}')
