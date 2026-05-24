"""Define data models used for index structure calculations.

This module contains lightweight data containers used to represent
the intermediate and final results of index analysis algorithms,
particularly for multilevel indexing structures in secondary storage.

The models encapsulate:

    - Blocking factor calculations.
    - Number of data and index blocks.
    - Estimated access counts.
    - Multilevel index hierarchy information.

Classes:
    IndexLevel:
        Represent a single level in a multilevel index structure.

    IndexCalculationResult:
        Store the complete result of an index calculation process.

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

from dataclasses import dataclass
from typing import List


@dataclass
class IndexLevel:
	"""
	Represent a level within a multilevel index structure.

	Each level stores the number of blocks required for that
	specific index layer.

	Attributes:
	    level (int):
	        Sequential level number in the index hierarchy.

	    blocks (int):
	        Number of blocks required for this level.

	"""

	level: int
	blocks: int


@dataclass
class IndexCalculationResult:
	"""
	Store the complete result of an index calculation.

	This model aggregates all relevant statistics generated
	during index analysis, including blocking factors,
	block counts, access estimations, logarithmic values,
	and multilevel index hierarchy information.

	Attributes:
	    bfr (int):
	        Blocking factor of the data file.

	        Represents the number of records that fit
	        into a single data block.

	    b (int):
	        Total number of data blocks required
	        to store the file.

	    bfr_i (int):
	        Blocking factor of the index file.

	        Represents the number of index entries
	        that fit into a single index block.

	    b_i (int):
	        Total number of first-level index blocks.

	    accesses (int):
	        Estimated number of block accesses required
	        to locate a record using the index structure.

	    log_value (float):
	        Logarithmic value used in multilevel index
	        calculations and access estimations.

	    levels (List[IndexLevel]):
	        List describing each level of the multilevel
	        index hierarchy.

	"""

	bfr: int
	b: int
	bfr_i: int
	b_i: int
	accesses: int
	log_value: float
	levels: List[IndexLevel]
