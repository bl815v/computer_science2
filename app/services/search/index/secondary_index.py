"""Secondary index calculation service.

This module defines the service responsible for computing the
storage and access statistics associated with a secondary index.

Unlike a primary index, a secondary index contains one index
entry per record, meaning the total number of index entries is
equal to the number of records in the file.

The service calculates:

    - Data blocking factor (BFR).
    - Number of data blocks.
    - Index blocking factor.
    - Number of index blocks.
    - Estimated binary search accesses.

The calculations are based on classic database indexing formulas.

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


class SecondaryIndexService(BaseIndexService):
	"""Provide calculations for secondary index structures.

	A secondary index stores an index entry for every record in the
	data file. Because of this, the number of index entries is equal
	to the total number of records (`r`).

	This service computes the main metrics required to analyze the
	storage cost and search efficiency of a secondary index.

	Inherited configuration parameters:

	    - `r`: Total number of records.
	    - `block_size`: Disk block size in bytes.
	    - `record_length`: Length of each data record.
	    - `index_record_length`: Length of each index record.

	The resulting calculations include:

	    - Data blocking factor (`bfr`).
	    - Number of data blocks (`b`).
	    - Index blocking factor (`bfr_i`).
	    - Number of index blocks (`b_i`).
	    - Estimated number of binary search accesses.

	"""

	def calculate(self) -> IndexCalculationResult:
		"""Calculate secondary index statistics.

		The method applies standard secondary index formulas:

		    - `bfr = floor(block_size / record_length)`
		    - `b = ceil(r / bfr)`
		    - `bfr_i = floor(block_size / index_record_length)`
		    - `b_i = ceil(r / bfr_i)`

		The number of disk accesses is estimated using
		binary search over the index blocks plus one
		additional access to retrieve the data block.

		Returns:
			IndexCalculationResult:
				Object containing all calculated secondary
				index metrics.

		Raises:
			ValueError:
				If the service has not been configured before
				executing the calculation.

		"""
		self._validate_structure()

		bfr = self.calculate_bfr()

		b = self.calculate_b()

		bfr_i = self.calculate_bfr_i()

		b_i = math.ceil(self.r / bfr_i)

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
