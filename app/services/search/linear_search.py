"""Provide linear search operations for fixed-size numeric arrays.

Implement sequential search to locate numeric string keys within the
internal storage. Return all 1-based positions where the searched value
appears, or an empty list if validation fails or the value is not found.

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


class LinearSearchService(BaseSearchService):
	"""Implement linear search strategy for locating keys.

	Perform sequential traversal over the internal data managed by
	the base service and collect all positions where the key matches.
	"""

	def search(self, value: str) -> List[int]:
		"""Search for a key using the linear search algorithm.

		Validate initialization state and key format before scanning
		the entire structure sequentially.

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

		return [i + 1 for i, v in enumerate(self.data) if v == value]
