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

from typing import Optional

from fastapi import APIRouter, HTTPException

from app.controllers.search.index.schemas import (
	IndexRequest,
	IndexResponse,
)
from app.controllers.search.snapshot import SnapshotRequest
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

# Keep last configuration per endpoint so export can be called without body
_last_configs: dict = {
	'primary': None,
	'secondary': None,
	'multilevel_primary': None,
	'multilevel_secondary': None,
}


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

	_last_configs['primary'] = request.model_dump()

	result = service.calculate()

	return IndexResponse.model_validate(result)


@router.post('/primary/export', response_model=dict)
def export_primary_index(request: Optional[IndexRequest] = None) -> dict:
	"""
	Export the current primary index configuration as a snapshot.

	This endpoint serializes the current state of a primary index
	service into a portable snapshot representation that can later
	be restored using the corresponding import endpoint.

	The export process supports two modes:

	    - Direct export using a request body.
	    - Export using the last stored configuration associated
	      with the endpoint.

	If a request body is provided, its values replace the previously
	stored configuration before generating the snapshot.

	Args:
		request (Optional[IndexRequest], optional):
			Optional configuration used to initialize the
			primary index service before exporting.

	Returns:
		dict:
			Serialized snapshot containing the current
			service configuration and state.

	Raises:
		HTTPException:
			If no configuration is available for export.

	"""
	service = PrimaryIndexService()

	cfg = None
	if request is not None:
		cfg = request.model_dump()
		_last_configs['primary'] = cfg
	else:
		cfg = _last_configs.get('primary')

	if not cfg:
		raise HTTPException(status_code=400, detail='No configuration available for export')

	service.configure(
		r=cfg['r'],
		block_size=cfg['block_size'],
		record_length=cfg['record_length'],
		index_record_length=cfg['index_record_length'],
	)

	return service.save_state()


@router.post('/primary/import', response_model=IndexResponse)
def import_primary_index(request: SnapshotRequest) -> IndexResponse:
	"""
	Restore and recalculate a primary index from a snapshot.

	This endpoint loads a previously exported snapshot into
	a new primary index service instance and recalculates
	all derived statistics.

	The imported snapshot must contain a valid configuration
	compatible with the primary index service.

	Args:
		request (SnapshotRequest):
			Request containing the serialized snapshot.

	Returns:
		IndexResponse:
			Validated response containing the recalculated
			primary index statistics.

	Raises:
		HTTPException:
			If the snapshot is invalid or cannot be restored.

	"""
	service = PrimaryIndexService()
	try:
		service.load_state(request.snapshot)
		result = service.calculate()
		return IndexResponse.model_validate(result)
	except ValueError as exc:
		raise HTTPException(status_code=400, detail=str(exc))


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

	_last_configs['secondary'] = request.model_dump()

	result = service.calculate()

	return IndexResponse.model_validate(result)


@router.post('/secondary/export', response_model=dict)
def export_secondary_index(request: Optional[IndexRequest] = None) -> dict:
	"""
	Export the current secondary index configuration as a snapshot.

	This endpoint serializes the state of a secondary index
	service so it can later be restored through the import API.

	The endpoint accepts an optional configuration request.
	If provided, the configuration becomes the current stored
	state before export.

	Args:
		request (Optional[IndexRequest], optional):
			Optional configuration used to initialize the
			secondary index service.

	Returns:
		dict:
			Serialized snapshot representing the current
			secondary index configuration and state.

	Raises:
		HTTPException:
			If no configuration is available for export.

	"""
	service = SecondaryIndexService()

	cfg = None
	if request is not None:
		cfg = request.model_dump()
		_last_configs['secondary'] = cfg
	else:
		cfg = _last_configs.get('secondary')

	if not cfg:
		raise HTTPException(status_code=400, detail='No configuration available for export')

	service.configure(
		r=cfg['r'],
		block_size=cfg['block_size'],
		record_length=cfg['record_length'],
		index_record_length=cfg['index_record_length'],
	)

	return service.save_state()


@router.post('/secondary/import', response_model=IndexResponse)
def import_secondary_index(request: SnapshotRequest) -> IndexResponse:
	"""
	Restore and recalculate a secondary index from a snapshot.

	This endpoint reconstructs a secondary index service
	from a serialized snapshot and recalculates all index
	statistics associated with the structure.

	Args:
		request (SnapshotRequest):
			Request containing the serialized snapshot data.

	Returns:
		IndexResponse:
			Validated response containing the recalculated
			secondary index statistics.

	Raises:
		HTTPException:
			If the snapshot is invalid or incompatible.

	"""
	service = SecondaryIndexService()
	try:
		service.load_state(request.snapshot)
		result = service.calculate()
		return IndexResponse.model_validate(result)
	except ValueError as exc:
		raise HTTPException(status_code=400, detail=str(exc))


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

	_last_configs['multilevel_primary'] = request.model_dump()

	result = service.calculate()

	return IndexResponse.model_validate(result)


@router.post('/multilevel-primary/export', response_model=dict)
def export_multilevel_primary_index(request: Optional[IndexRequest] = None) -> dict:
	"""
	Export the current multilevel primary index configuration.

	This endpoint generates a serialized snapshot of a
	multilevel primary index service, including the
	configuration required to reconstruct the hierarchy.

	If a request body is provided, the configuration is
	stored as the latest active configuration before export.

	Args:
		request (Optional[IndexRequest], optional):
			Optional configuration used to initialize the
			multilevel primary index service.

	Returns:
		dict:
			Serialized snapshot containing the multilevel
			primary index state and configuration.

	Raises:
		HTTPException:
			If no configuration is available for export.

	"""
	service = MultilevelPrimaryIndexService()

	cfg = None
	if request is not None:
		cfg = request.model_dump()
		_last_configs['multilevel_primary'] = cfg
	else:
		cfg = _last_configs.get('multilevel_primary')

	if not cfg:
		raise HTTPException(status_code=400, detail='No configuration available for export')

	service.configure(
		r=cfg['r'],
		block_size=cfg['block_size'],
		record_length=cfg['record_length'],
		index_record_length=cfg['index_record_length'],
	)

	return service.save_state()


@router.post('/multilevel-primary/import', response_model=IndexResponse)
def import_multilevel_primary_index(request: SnapshotRequest) -> IndexResponse:
	"""
	Restore a multilevel primary index from a snapshot.

	This endpoint reconstructs a multilevel primary index
	service using a serialized snapshot and recalculates
	the associated hierarchy statistics.

	The restored response includes all multilevel access
	and block calculations.

	Args:
		request (SnapshotRequest):
			Request containing the serialized snapshot.

	Returns:
		IndexResponse:
			Validated response containing the recalculated
			multilevel primary index statistics.

	Raises:
		HTTPException:
			If the snapshot cannot be restored correctly.

	"""
	service = MultilevelPrimaryIndexService()
	try:
		service.load_state(request.snapshot)
		result = service.calculate()
		return IndexResponse.model_validate(result)
	except ValueError as exc:
		raise HTTPException(status_code=400, detail=str(exc))


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

	_last_configs['multilevel_secondary'] = request.model_dump()

	result = service.calculate()

	return IndexResponse.model_validate(result)


@router.post('/multilevel-secondary/export', response_model=dict)
def export_multilevel_secondary_index(request: Optional[IndexRequest] = None) -> dict:
	"""
	Export the current multilevel secondary index configuration.

	This endpoint serializes the state of a multilevel
	secondary index service into a reusable snapshot format.

	If a configuration request is provided, it replaces
	the previous stored configuration before export.

	Args:
		request (Optional[IndexRequest], optional):
			Optional configuration used to initialize the
			multilevel secondary index service.

	Returns:
		dict:
			Serialized snapshot containing the current
			multilevel secondary index configuration.

	Raises:
		HTTPException:
			If no configuration is available for export.

	"""
	service = MultilevelSecondaryIndexService()

	cfg = None
	if request is not None:
		cfg = request.model_dump()
		_last_configs['multilevel_secondary'] = cfg
	else:
		cfg = _last_configs.get('multilevel_secondary')

	if not cfg:
		raise HTTPException(status_code=400, detail='No configuration available for export')

	service.configure(
		r=cfg['r'],
		block_size=cfg['block_size'],
		record_length=cfg['record_length'],
		index_record_length=cfg['index_record_length'],
	)

	return service.save_state()


@router.post('/multilevel-secondary/import', response_model=IndexResponse)
def import_multilevel_secondary_index(request: SnapshotRequest) -> IndexResponse:
	"""
	Restore a multilevel secondary index from a snapshot.

	This endpoint loads a serialized snapshot into a new
	multilevel secondary index service instance and
	recalculates all hierarchy-related statistics.

	The resulting response includes block distribution,
	index levels, and estimated disk accesses.

	Args:
		request (SnapshotRequest):
			Request containing the serialized snapshot.

	Returns:
		IndexResponse:
			Validated response containing the recalculated
			multilevel secondary index statistics.

	Raises:
		HTTPException:
			If the snapshot data is invalid or incomplete.

	"""
	service = MultilevelSecondaryIndexService()
	try:
		service.load_state(request.snapshot)
		result = service.calculate()
		return IndexResponse.model_validate(result)
	except ValueError as exc:
		raise HTTPException(status_code=400, detail=str(exc))
