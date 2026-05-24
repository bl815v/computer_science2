"""Schemas for index calculations.

This module defines the Pydantic schemas used for validating
requests and formatting responses related to disk index
calculations.

The schemas are used by the API routes responsible for
computing:

    - Primary indexes.
    - Secondary indexes.
    - Multilevel primary indexes.
    - Multilevel secondary indexes.

The module includes:

    - `IndexRequest`:
        Input schema containing the parameters required
        for index calculations.

    - `IndexLevelResponse`:
        Representation of a single multilevel index layer.

    - `IndexResponse`:
        Response schema containing all calculated index
        statistics and optional multilevel hierarchy data.

All schemas support validation from ORM-style objects
through `from_attributes=True`.

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

from typing import List

from pydantic import BaseModel, ConfigDict, Field

model_config = ConfigDict(from_attributes=True)


class IndexRequest(BaseModel):
	"""Validate input parameters for index calculations.

	This schema contains the configuration values required
	to compute disk index statistics.

	Attributes:
		r (int):
			Total number of records in the data file.

		block_size (int):
			Size of a disk block in bytes.

		record_length (int):
			Length of each data record in bytes.

		index_record_length (int):
			Length of each index record in bytes.

	Validation Rules:
		All fields must be positive integers greater than zero.

	"""

	r: int = Field(
		...,
		gt=0,
		description='Total number of records in the data file.',
	)

	block_size: int = Field(
		...,
		gt=0,
		description='Disk block size in bytes.',
	)

	record_length: int = Field(
		...,
		gt=0,
		description='Length of each data record in bytes.',
	)

	index_record_length: int = Field(
		...,
		gt=0,
		description='Length of each index record in bytes.',
	)


class IndexLevelResponse(BaseModel):
	"""Represent a level in a multilevel index hierarchy.

	This schema stores the number of blocks associated
	with a specific index level.

	Attributes:
		level (int):
			Hierarchy level number.

		blocks (int):
			Number of blocks present at the level.

	"""

	model_config = ConfigDict(
		from_attributes=True,
	)

	level: int
	blocks: int


class IndexResponse(BaseModel):
	"""Represent the result of an index calculation.

	This schema contains the calculated metrics for
	disk indexing structures, including optional
	multilevel hierarchy information.

	Attributes:
		bfr (int):
			Data blocking factor.

		b (int):
			Total number of data blocks.

		bfr_i (int):
			Index blocking factor.

		b_i (int):
			Total number of index blocks.

		accesses (int):
			Estimated number of disk accesses required
			for a search operation.

		log_value (float):
			Logarithmic value used during access
			calculation.

		levels (List[IndexLevelResponse]):
			Multilevel hierarchy information.
			Empty for single-level indexes.

	"""

	model_config = ConfigDict(
		from_attributes=True,
	)

	bfr: int
	b: int
	bfr_i: int
	b_i: int
	accesses: int
	log_value: float
	levels: List[IndexLevelResponse]
