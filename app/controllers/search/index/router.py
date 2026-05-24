"""Routes for disk index calculations.

This module defines the API endpoints responsible for calculating
different types of disk index statistics used in database systems.

The available calculations include:

    - Primary indexes.
    - Secondary indexes.
    - Multilevel primary indexes.
    - Multilevel secondary indexes.

Each endpoint receives the required storage parameters,
configures the corresponding service, executes the calculation,
and returns the computed statistics as a validated response model.

The calculations are based on classical database indexing formulas,
including:

    - Blocking factors.
    - Number of data and index blocks.
    - Binary search access estimation.
    - Multilevel hierarchy generation.

Routes:
    POST /search/index/primary
        Calculate primary index statistics.

    POST /search/index/secondary
        Calculate secondary index statistics.

    POST /search/index/multilevel-primary
        Calculate multilevel primary index statistics.

    POST /search/index/multilevel-secondary
        Calculate multilevel secondary index statistics.

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

from fastapi import APIRouter

from app.controllers.search.index.schemas import (
	IndexRequest,
	IndexResponse,
)
from app.services.search.index.multilevel_index import (
	MultilevelPrimaryIndexService,
	MultilevelSecondaryIndexService,
)
from app.services.search.index.primary_index import (
	PrimaryIndexService,
)
from app.services.search.index.secondary_index import (
	SecondaryIndexService,
)

router = APIRouter(
	prefix='/search/index',
	tags=['Search - Index'],
)


@router.post(
	'/primary',
	response_model=IndexResponse,
)
def calculate_primary_index(
	request: IndexRequest,
) -> IndexResponse:
	"""Calculate primary index statistics.

	This endpoint computes the storage and access metrics
	for a primary index structure.

	The calculation includes:

	    - Data blocking factor.
	    - Number of data blocks.
	    - Index blocking factor.
	    - Number of index blocks.
	    - Estimated disk accesses.

	Args:
		request (IndexRequest):
			Input parameters required for index calculations.

	Returns:
		IndexResponse:
			Validated response containing the calculated
			primary index statistics.

	Raises:
		ValueError:
			If any request parameter is invalid.

	"""
	service = PrimaryIndexService()

	service.configure(
		r=request.r,
		block_size=request.block_size,
		record_length=request.record_length,
		index_record_length=request.index_record_length,
	)

	result = service.calculate()

	return IndexResponse.model_validate(result)


@router.post(
	'/secondary',
	response_model=IndexResponse,
)
def calculate_secondary_index(
	request: IndexRequest,
) -> IndexResponse:
	"""Calculate secondary index statistics.

	This endpoint computes the storage and search metrics
	for a secondary index structure.

	Unlike primary indexes, secondary indexes contain
	one index entry per record.

	The calculation includes:

	    - Data blocking factor.
	    - Number of data blocks.
	    - Index blocking factor.
	    - Number of index blocks.
	    - Estimated binary search accesses.

	Args:
		request (IndexRequest):
			Input parameters required for index calculations.

	Returns:
		IndexResponse:
			Validated response containing the calculated
			secondary index statistics.

	Raises:
		ValueError:
			If any request parameter is invalid.

	"""
	service = SecondaryIndexService()

	service.configure(
		r=request.r,
		block_size=request.block_size,
		record_length=request.record_length,
		index_record_length=request.index_record_length,
	)

	result = service.calculate()

	return IndexResponse.model_validate(result)


@router.post(
	'/multilevel-primary',
	response_model=IndexResponse,
)
def calculate_multilevel_primary_index(
	request: IndexRequest,
) -> IndexResponse:
	"""Calculate multilevel primary index statistics.

	This endpoint computes the metrics associated with
	a multilevel primary index structure.

	In addition to standard primary index calculations,
	the service generates the multilevel hierarchy and
	estimates the total number of disk accesses required
	for searches.

	The response includes:

	    - Primary index statistics.
	    - Number of index levels.
	    - Blocks per hierarchy level.
	    - Estimated multilevel access cost.

	Args:
		request (IndexRequest):
			Input parameters required for index calculations.

	Returns:
		IndexResponse:
			Validated response containing the calculated
			multilevel primary index statistics.

	Raises:
		ValueError:
			If any request parameter is invalid.

	"""
	service = MultilevelPrimaryIndexService()

	service.configure(
		r=request.r,
		block_size=request.block_size,
		record_length=request.record_length,
		index_record_length=request.index_record_length,
	)

	result = service.calculate()

	return IndexResponse.model_validate(result)


@router.post(
	'/multilevel-secondary',
	response_model=IndexResponse,
)
def calculate_multilevel_secondary_index(
	request: IndexRequest,
) -> IndexResponse:
	"""Calculate multilevel secondary index statistics.

	This endpoint computes the metrics associated with
	a multilevel secondary index structure.

	The calculation extends the secondary index model
	by building additional hierarchical index levels
	to reduce search cost.

	The response includes:

	    - Secondary index statistics.
	    - Hierarchical index levels.
	    - Number of blocks per level.
	    - Estimated multilevel access cost.

	Args:
		request (IndexRequest):
			Input parameters required for index calculations.

	Returns:
		IndexResponse:
			Validated response containing the calculated
			multilevel secondary index statistics.

	Raises:
		ValueError:
			If any request parameter is invalid.

	"""
	service = MultilevelSecondaryIndexService()

	service.configure(
		r=request.r,
		block_size=request.block_size,
		record_length=request.record_length,
		index_record_length=request.index_record_length,
	)

	result = service.calculate()

	return IndexResponse.model_validate(result)
