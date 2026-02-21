"""Provide binary search operations for fixed-size numeric arrays.

Implement binary search to locate numeric string keys within an ordered
internal list. Return all 1-based positions where the searched value
appears, or an empty list if the value is not found or validation fails.

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


class BinarySearchService(BaseSearchService):
	"""Implement binary search strategy for locating keys.

	Perform efficient lookup over the sorted internal data managed by
	the base service. Assume that non-null values are kept in ascending
	order and grouped before None entries.
	"""

	def search(self, value: str) -> List[int]:
		"""Search for a key using the binary search algorithm.

		Validate initialization state and key format before performing
		the search. Locate one occurrence using binary search and then
		expand to collect all contiguous matches.

		Args:
			value (str): Numeric key to search for.

		Returns:
			List[int]: List of 1-based positions where the key appears.
				Return an empty list if the structure is not initialized,
				the key format is invalid, or the key is not found.

		"""
		if not self.initialized:
			return []

		if len(value) != self.digits or not value.isdigit():
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

		return positions
