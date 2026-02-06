"""Provide linear search operations for fixed-size numeric arrays.

The LinearSearchService provides a simple data structure simulation for linear search
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


class LinearSearchService:
	"""Service class for linear search operations on a fixed-size numeric array.

	This class manages a data structure where values are stored in a fixed-size
	array. All values must be numeric strings with exactly the specified number
	of digits. The class provides methods to create, insert, search, and delete
	values using linear search algorithms.

	Attributes:
	    data (List[Optional[str]]): The underlying array storing the values.
	    size (int): The maximum capacity of the data structure.
	    digits (int): The exact number of digits required for each value.
	    initialized (bool): Whether the structure has been properly initialized.

	"""

	def __init__(self) -> None:
		"""Initialize a new LinearSearchService instance.

		Sets up an empty data structure with default values and marks it
		as uninitialized until the create() method is called.
		"""
		self.data: List[Optional[str]] = []
		self.size = 0
		self.digits = 0
		self.initialized = False
		print('LinearSearchService initialized')

	def create(self, size: int, digits: int) -> None:
		"""Create and initializes the linear search data structure.

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
			raise ValueError('Size must be positive')
		if digits <= 0:
			raise ValueError('Digits must be positive')

		self.size = size
		self.digits = digits
		self.data = [None] * size
		self.initialized = True
		print(f'Structure created: size={size}, digits={digits}')

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
			raise ValueError('Structure not initialized. Call create() first.')

		if len(value) != self.digits:
			raise ValueError(f'Value must have exactly {self.digits} digits')

		if not value.isdigit():
			raise ValueError('Value must be numeric')

		if value in self.data:
			print(f'Value {value} already exists in data: {self.data}')
			raise ValueError(f'Value {value} already exists')

		try:
			index = self.data.index(None)
		except ValueError as exc:
			raise ValueError('No empty space available') from exc

		self.data[index] = value
		print(f'Value {value} inserted at position {index + 1}')
		return index + 1  # Return 1-based index for user convenience

	def search(self, value: str) -> List[int]:
		"""Search for all occurrences of a value in the array.

		Performs a linear search through the array and returns all positions
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

		return [i + 1 for i, v in enumerate(self.data) if v == value]

	def delete(self, value: str) -> List[int]:
		"""Delete all occurrences of a value from the array.

		Performs a linear search and removes all instances of the specified value
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

		if len(value) != self.digits:
			return []

		if not value.isdigit():
			return []

		positions = []
		for i, v in enumerate(self.data):
			if v == value:
				self.data[i] = None
				positions.append(i + 1)

		print(f'Value {value} deleted from positions: {positions}')
		return positions
