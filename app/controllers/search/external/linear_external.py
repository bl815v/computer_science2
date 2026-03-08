"""
Router factory for external search services.

This module defines a reusable FastAPI router builder used to expose
external search structures through REST endpoints.

The router provides a standardized interface for external search
implementations based on block storage. Each router supports the
following operations:

    - Structure creation
    - State inspection
    - Value insertion
    - Value search
    - Value deletion

The module uses controller helper functions to separate HTTP
handling from the core service logic.

It also instantiates a concrete router for the linear external
search implementation.

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

from fastapi import APIRouter, HTTPException

from app.controllers.search.base_search import (
	InsertRequest,
	handle_delete,
	handle_search,
)
from app.controllers.search.external.base_external import (
	CreateExternalRequest,
	handle_external_create,
	handle_external_insert,
)
from app.services.search.external.linear_external import LinearExternalSearch


def create_external_search_router(service, prefix: str, tag: str) -> APIRouter:
	"""
	Create a FastAPI router for an external search service.

	This factory function builds a router with a standard set of
	endpoints used by block-based external search structures.

	Args:
		service:
			Instance of a subclass of BaseExternalSearch responsible
			for managing the underlying data structure.

		prefix (str):
			URL prefix assigned to the router.

		tag (str):
			Tag used for grouping endpoints in the API documentation.

	Returns:
		APIRouter:
			Configured router instance exposing the search API.

	"""
	router = APIRouter(prefix=prefix, tags=[tag])

	@router.post('/create')
	async def create_structure(request: CreateExternalRequest):
		"""
		Initialize an external search structure.

		Args:
			request (CreateExternalRequest):
				Request body containing structure parameters.

		Returns:
			dict:
				Information describing the created structure.

		Raises:
			HTTPException:
				If an unexpected error occurs during creation.

		"""
		try:
			return handle_external_create(service, request)
		except Exception as e:
			raise HTTPException(status_code=500, detail=str(e))

	@router.get('/state')
	async def get_state():
		"""
		Retrieve the current state of the external structure.

		Returns:
			dict:
				Structure metadata including:

					- size: maximum capacity
					- digits: key length
					- block_size: computed block size
					- blocks: current block contents

		"""
		return {
			'size': service.size,
			'digits': service.digits,
			'block_size': service.block_size,
			'blocks': service.blocks,
		}

	@router.post('/insert')
	async def insert_value(request: InsertRequest):
		"""
		Insert a new key into the external structure.

		Args:
			request (InsertRequest):
				Request containing the value to insert.

		Returns:
			dict:
				Information about the inserted value and its position.

		Raises:
			HTTPException:
				400 if the value is invalid or insertion fails.
				500 if an unexpected server error occurs.

		"""
		try:
			return handle_external_insert(service, request)
		except ValueError as e:
			raise HTTPException(status_code=400, detail=str(e))
		except HTTPException:
			raise
		except Exception as e:
			raise HTTPException(status_code=500, detail=str(e))

	@router.get('/search/{value}')
	async def search_value(value: str):
		"""
		Search for a key in the external structure.

		Args:
			value (str):
				Key to search.

		Returns:
			dict:
				Search result describing the key location if found.

		"""
		return handle_search(service, value)

	@router.delete('/delete/{value}')
	async def delete_value(value: str):
		"""
		Remove a key from the external structure.

		Args:
			value (str):
				Key to delete.

		Returns:
			dict:
				Information about removed positions.

		"""
		return handle_delete(service, value)

	return router


linear_external_service = LinearExternalSearch()

linear_external_router = create_external_search_router(
	linear_external_service,
	prefix='/external/linear',
	tag='External Linear Search',
)
