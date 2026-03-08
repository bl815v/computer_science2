"""
Binary external search implementation.

This module defines the `BinaryExternalSearch` class, which performs
efficient searches over a block-based external search structure.

The structure divides the dataset into ordered blocks of approximately
√n elements. Each block stores values in ascending order, and the
maximum value of each block forms a non-decreasing sequence across
the structure.

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

from typing import Dict, List

from app.services.search.external.base_external import BaseExternalSearch


class BinaryExternalSearch(BaseExternalSearch):
	"""
	Binary search implementation for block-based external structures.

	This class performs a two-level binary search over an ordered
	external structure composed of fixed-size blocks.

	The search strategy works as follows:

	1. **Block-level search**
		A binary search is applied over the blocks to locate the first
		block whose maximum value is greater than or equal to the target.

	2. **Block internal search**
		Once the candidate block is identified, a binary search is
		executed inside the block to determine the exact position
		of the key.

	Because both the blocks and their contents are sorted, the search
	space is reduced significantly at each step.

	Inherited Attributes:
	blocks (List[List[Optional[str]]]):
		Block-based storage structure containing ordered keys.

	block_size (int):
		Maximum number of elements stored in each block.
	"""

	def search(self, value: str) -> List[Dict[str, int]]:
		"""
		Search for a key using a two-level binary search strategy.

		The algorithm performs:

			1. Validation of the structure and key format.
			2. Binary search across the blocks to locate the candidate block.
			3. Binary search inside the selected block.
			4. Return the exact position if the key exists.

		Empty positions (`None`) appear only at the end of each block and
		are treated as greater than any valid key during comparisons.

		Args:
			value (str):
				Numeric key to search for. The value must contain the
				exact number of digits defined for the structure.

		Returns:
			List[Dict[str, int]]:
				A list containing a dictionary that describes the position
				where the key was found. Since duplicates are not allowed,
				the list contains at most one element.

				Each dictionary contains:

					- ``global_position`` (int):
						1-based index in the entire structure.

					- ``block_index`` (int):
						1-based index of the block containing the key.

					- ``block_position`` (int):
						1-based position of the key inside the block.

				Returns an empty list if the key does not exist in the
				structure or if the structure is not initialized.

		"""
		if not self.initialized:
			return []
		if len(value) != self.digits or not value.isdigit():
			return []

		low, high = 0, len(self.blocks)
		while low < high:
			mid = (low + high) // 2
			block = self.blocks[mid]

			max_val = None
			for i in range(len(block) - 1, -1, -1):
				if block[i] is not None:
					max_val = block[i]
					break

			if max_val is None:
				high = mid
			else:
				if value <= max_val:
					high = mid
				else:
					low = mid + 1

		if low >= len(self.blocks):
			return []

		candidate_block = self.blocks[low]

		global_offset = 0
		for i in range(low):
			global_offset += len(self.blocks[i])

		left, right = 0, len(candidate_block)
		while left < right:
			mid = (left + right) // 2
			if candidate_block[mid] is None or candidate_block[mid] >= value:
				right = mid
			else:
				left = mid + 1

		if (
			left < len(candidate_block)
			and candidate_block[left] is not None
			and candidate_block[left] == value
		):
			global_pos = global_offset + left + 1
			return [
				{
					'global_position': global_pos,
					'block_index': low + 1,
					'block_position': left + 1,
				}
			]

		return []
