"""Multilevel index calculation services.

This module provides services for calculating the statistics of
multilevel primary and secondary indexes used in database systems.

A multilevel index extends a traditional index structure by creating
additional index layers over existing index blocks. This reduces the
number of disk accesses required during searches by organizing index
entries hierarchically.

The module includes:

    - `MultilevelPrimaryIndexService`:
        Calculates statistics for multilevel primary indexes.

    - `MultilevelSecondaryIndexService`:
        Calculates statistics for multilevel secondary indexes.

Both services extend their corresponding single-level index services
and add support for:

    - Hierarchical index level generation.
    - Multilevel access cost estimation.
    - Level-by-level block distribution analysis.

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

from app.services.search.index.models import (
	IndexCalculationResult,
)
from app.services.search.index.primary_index import (
	PrimaryIndexService,
)
from app.services.search.index.secondary_index import (
	SecondaryIndexService,
)


class MultilevelPrimaryIndexService(
	PrimaryIndexService,
):
	"""Provide calculations for multilevel primary indexes.

	A multilevel primary index organizes primary index blocks into
	multiple hierarchical levels until a single root block remains.

	This structure improves search efficiency by reducing the number
	of disk accesses required to locate a record.

	The service extends `PrimaryIndexService` by adding:

	    - Calculation of the total number of index levels.
	    - Construction of the multilevel hierarchy.
	    - Estimation of multilevel access cost.

	The total number of accesses is computed as:

	    number_of_levels + 1

	where the additional access corresponds to retrieving
	the actual data block.

	"""

	def calculate(self) -> IndexCalculationResult:
		"""Calculate multilevel primary index statistics.

		The method first computes the standard primary index
		statistics using the parent implementation and then
		builds the multilevel hierarchy.

		The generated hierarchy stores the number of blocks
		present at each level of the index.

		Returns:
			IndexCalculationResult:
				Object containing:

				- Data blocking factor.
				- Number of data blocks.
				- Index blocking factor.
				- Number of index blocks.
				- Estimated disk accesses.
				- Multilevel hierarchy information.

		Raises:
			ValueError:
				If the service has not been configured before
				calculation.

		"""
		result = super().calculate()

		levels_count = self.calculate_levels(
			result.bfr_i,
			result.b,
		)

		levels = self.build_multilevel_levels(
			result.b_i,
			result.bfr_i,
		)

		result.levels = levels
		result.accesses = levels_count + 1

		return result


class MultilevelSecondaryIndexService(
	SecondaryIndexService,
):
	"""Provide calculations for multilevel secondary indexes.

	A multilevel secondary index creates additional index layers
	over a secondary index structure to reduce search cost.

	Unlike primary indexes, secondary indexes contain one entry
	per record. Therefore, the hierarchy calculations are based
	on the total number of records rather than the number of
	data blocks.

	This service extends `SecondaryIndexService` by adding:

	    - Calculation of multilevel hierarchy depth.
	    - Construction of hierarchical index levels.
	    - Estimation of multilevel disk accesses.

	The total number of accesses is computed as:

	    number_of_levels + 1

	where the additional access corresponds to retrieving
	the final data record block.

	"""

	def calculate(self) -> IndexCalculationResult:
		"""Calculate multilevel secondary index statistics.

		The method first computes the standard secondary index
		statistics and then generates the multilevel hierarchy.

		The hierarchy stores the number of index blocks present
		at each level until a single root block is reached.

		Returns:
			IndexCalculationResult:
				Object containing:

				- Data blocking factor.
				- Number of data blocks.
				- Index blocking factor.
				- Number of index blocks.
				- Estimated disk accesses.
				- Multilevel hierarchy information.

		Raises:
			ValueError:
				If the service has not been configured before
				calculation.

		"""
		result = super().calculate()

		levels_count = self.calculate_levels(
			result.bfr_i,
			self.r,
		)

		levels = self.build_multilevel_levels(
			result.b_i,
			result.bfr_i,
		)

		result.levels = levels
		result.accesses = levels_count + 1

		return result
