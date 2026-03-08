"""
Linear external search implementation using block-based storage.

This module provides a concrete implementation of an external search
algorithm based on sequential scanning of ordered blocks.

The structure inherits from `BaseExternalSearch`, which organizes data
into fixed-size blocks of size floor(sqrt(n)). Each block is internally
sorted, and blocks are globally ordered.

The search strategy follows these steps:

    1. Iterate through blocks sequentially.
    2. Compare the target value with the largest element of each block.
    3. If the value is less than or equal to the block maximum,
       perform a linear search within that block.
    4. Stop early if a value greater than the target is encountered
       inside the block (because the block is sorted).

This approach reduces the search space compared to a full sequential
search while maintaining simplicity.

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


class LinearExternalSearch(BaseExternalSearch):
	"""
	Implement linear search over ordered external blocks.

	The algorithm scans blocks sequentially and decides whether to
	search inside a block by comparing the target value with the
	maximum value stored in that block.

	If the target value is smaller than or equal to the block's
	largest element, a linear search is performed inside that block.

	Because both the blocks and their contents are ordered, the
	search can terminate early when encountering a value greater
	than the target.

	Inherited Attributes:
		blocks (List[List[Optional[str]]]):
			Block-based storage structure.

		block_size (int):
			Maximum number of elements per block.
	"""

	def search(self, value: str) -> List[Dict[str, int]]:
		"""
		Search for a key using block-based linear search.

		The algorithm performs the following steps:

			1. Iterate through blocks in order.
			2. For each block, determine the largest non-null value.
			3. If the target value is less than or equal to that value,
			perform a sequential search inside the block.
			4. If a value larger than the target is encountered,
			terminate the search early.

		Args:
			value (str):
				Numeric key to search for.

		Returns:
			List[Dict[str, int]]:
				List containing a dictionary describing the position
				where the value was found. Since duplicates are not
				allowed, at most one result will be returned.

				Each dictionary contains:

					- 'global_position': 1-based index in the full structure
					- 'block_index': block index (1-based)
					- 'block_position': 1-based position within the block

				Returns an empty list if the value is not found.

		"""
		if not self.initialized:
			return []
		if len(value) != self.digits or not value.isdigit():
			return []

		global_offset = 0
		for block_idx, block in enumerate(self.blocks):
			last = None
			for v in reversed(block):
				if v is not None:
					last = v
					break

			if last is None:
				global_offset += len(block)
				continue

			if value <= last:
				for j, v in enumerate(block):
					if v is not None:
						if v == value:
							global_pos = global_offset + j + 1
							return [
								{
									'global_position': global_pos,
									'block_index': block_idx + 1,
									'block_position': j + 1,
								}
							]
						if v > value:
							return []
				return []
			else:
				global_offset += len(block)

		return []
