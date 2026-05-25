"""Binary external search implementation.

This module defines the ``BinaryExternalSearch`` class, which
implements a two-level binary search strategy over a block-based
external storage structure.

The structure divides the dataset into ordered blocks containing
approximately √n elements. Both the blocks and the values stored
inside each block remain sorted in ascending order.

The search algorithm operates in two phases:

    1. Binary search across the blocks to identify the candidate block.
    2. Binary search inside the selected block to locate the key.

This organization significantly reduces the search space and
approximates classical indexed external search methods used in
file systems and database storage engines.

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

from app.services.search.external.base_external import (
	BaseExternalSearch,
)


class BinaryExternalSearch(BaseExternalSearch):
	"""Binary search implementation for external block structures.

	This class extends ``BaseExternalSearch`` by implementing
	an efficient two-level binary search strategy.

	The structure assumes that:

	    - Blocks are globally ordered.
	    - Values inside each block are internally ordered.
	    - Empty positions appear only at the end of blocks.

	The search process first identifies the candidate block
	using binary search and then performs another binary search
	inside that block to locate the requested key.

	Inherited Attributes:
		blocks (List[List[Optional[str]]]):
			Block-based storage structure containing ordered keys.

		block_size (int):
			Maximum number of elements stored per block.

	"""

	snapshot_type = 'binary_external_search'

	def search(self, value: str) -> List[Dict[str, int]]:
		"""Search for a key using binary search over blocks.

		The algorithm executes the following stages:

		    1. Validate the structure state and input value.
		    2. Locate the candidate block using binary search.
		    3. Perform binary search inside the selected block.
		    4. Return positional information if the key exists.

		Empty positions (``None``) are treated as greater than
		valid keys during comparisons and are expected to appear
		only at the end of blocks.

		Args:
			value (str):
				Numeric key to search for.

				The value must contain the exact number of
				digits configured for the structure.

		Returns:
			List[Dict[str, int]]:
				List containing positional information for
				the located key.

				Since duplicate keys are not allowed,
				the returned list contains at most one element.

				Each dictionary includes:

					- ``global_position``:
					  1-based global position in the structure.

					- ``block_index``:
					  1-based block number containing the key.

					- ``block_position``:
					  1-based position inside the block.

				Returns an empty list if the key does not exist
				or if the structure is not initialized.

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

			for i in range(
				len(block) - 1,
				-1,
				-1,
			):
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
