"""
Provide calculations for primary disk index structures.

This module implements the logic required to analyze a
primary index organization in secondary storage systems.

A primary index is built over an ordered data file where
each index entry references a data block. The service
computes:

    - Data blocking factor.
    - Number of data blocks.
    - Index blocking factor.
    - Number of index blocks.
    - Estimated binary search accesses.

Classes:
    PrimaryIndexService:
        Service responsible for primary index calculations.

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

import math

from app.services.search.index.base_index import (
	BaseIndexService,
)
from app.services.search.index.models import (
	IndexCalculationResult,
)


class PrimaryIndexService(BaseIndexService):
	"""
	Provide calculations for primary index structures.

	A primary index is defined over an ordered data file,
	where each index entry points to a data block instead
	of an individual record.

	The service calculates:

	    - Data blocking factor (BFR).
	    - Number of data blocks (B).
	    - Index blocking factor (BFR_i).
	    - Number of index blocks (B_i).
	    - Estimated binary search accesses.

	The access estimation assumes binary search over
	the primary index followed by one additional access
	to retrieve the target data block.

	Inherited Attributes:
	    r (int):
	        Total number of records.

	    block_size (int):
	        Disk block size in bytes.

	    record_length (int):
	        Data record length in bytes.

	    index_record_length (int):
	        Index record length in bytes.

	"""

	def calculate(self) -> IndexCalculationResult:
		"""
		Calculate primary index statistics.

		The method performs the complete set of calculations
		required for a primary index structure.

		Calculation process:

		    1. Compute the data blocking factor (BFR).
		    2. Compute the number of data blocks (B).
		    3. Compute the index blocking factor (BFR_i).
		    4. Compute the number of index blocks (B_i).
		    5. Estimate binary search accesses over the index.
		    6. Add one additional access to retrieve the
		       corresponding data block.

		Formulas:
		    BFR = floor(block_size / record_length)

		    B = ceil(r / BFR)

		    BFR_i = floor(block_size / index_record_length)

		    B_i = ceil(B / BFR_i)

		    accesses = ceil(log2(B_i)) + 1

		Returns:
		    IndexCalculationResult:
		        Object containing all calculated statistics
		        for the primary index structure.

		Raises:
		    ValueError:
		        If the service has not been configured.

		"""
		self._validate_structure()

		bfr = self.calculate_bfr()

		b = self.calculate_b()

		bfr_i = self.calculate_bfr_i()

		b_i = math.ceil(b / bfr_i)

		log_value = math.log2(b_i)

		accesses = math.ceil(log_value) + 1

		return IndexCalculationResult(
			bfr=bfr,
			b=b,
			bfr_i=bfr_i,
			b_i=b_i,
			accesses=accesses,
			log_value=log_value,
			levels=[],
		)
