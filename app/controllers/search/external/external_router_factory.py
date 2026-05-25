"""
Router factory for external search structures.

This module defines a reusable router generator used to expose
REST endpoints for external search structures implemented in the
services layer.

External search structures store keys in ordered blocks rather than
a single linear array. Because of this, the router exposes additional
state information such as the block size and the block layout.

The router created by this module provides the following operations:

    - Create and initialize the structure
    - Retrieve the current structure state
    - Insert a new key
    - Search for a key
    - Delete an existing key

The router delegates all operational logic to the provided
service instance, which must implement the external search
structure behavior.

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
from app.controllers.search.snapshot import (
	SnapshotRequest,
	handle_export_snapshot,
	handle_import_snapshot,
)


def create_external_search_router(get_service, prefix: str, tag: str) -> APIRouter:
	"""Create a FastAPI router for an external search structure.

	This factory function generates a reusable router that exposes
	common REST endpoints for external search structures implemented
	in the services layer.

	Instead of storing a direct reference to the service instance,
	the router receives a callable that returns the current service.
	This design prevents stale references when the service is created
	or replaced dynamically after router initialization.

	The generated router provides endpoints for:

	    - Structure creation
	    - State inspection
	    - Snapshot export/import
	    - Insert operations
	    - Search operations
	    - Delete operations

	Args:
	    get_service:
	        Callable that returns the current external search
	        service instance.

	    prefix (str):
	        URL prefix assigned to the router.

	    tag (str):
	        OpenAPI tag used to group the router endpoints.

	Returns:
	    APIRouter:
	        Configured FastAPI router for the external structure.

	"""
	router = APIRouter(prefix=prefix, tags=[tag])

	def _service():
		"""Retrieve and validate the current service instance.

		This helper ensures that the external structure has been
		initialized before executing any operation.

		Returns:
		    BaseSearchService:
		        Active external search structure service.

		Raises:
		    HTTPException:
		        If the structure has not been created yet.

		"""
		service = get_service()
		if service is None:
			raise HTTPException(status_code=400, detail='Estructura no creada')
		return service

	@router.post('/create')
	def create_structure(request: CreateExternalRequest):
		"""Create and initialize the external search structure.

		This endpoint allocates the block-based structure and
		configures its internal storage according to the
		parameters provided in the request.

		Args:
		    request (CreateExternalRequest):
		        Configuration parameters for the structure,
		        including size, digits, and block size.

		Returns:
		    dict:
		        Information about the created structure.

		"""
		return handle_external_create(_service(), request)

	@router.get('/state')
	async def get_state():
		"""Retrieve the current internal state of the structure.

		This endpoint exposes debugging and visualization data
		related to the external search structure.

		The response includes:

		    - Total structure size
		    - Digit configuration
		    - Block size
		    - Current block contents

		Returns:
		    dict:
		        Internal representation of the structure.

		"""
		service = _service()

		return {
			'size': service.size,
			'digits': service.digits,
			'block_size': service.block_size,
			'blocks': service.blocks,
		}

	@router.post('/export')
	async def export_state():
		"""Export the current structure snapshot.

		This endpoint serializes the current state of the external
		search structure into a snapshot representation that can
		be stored and later restored.

		The snapshot includes:

		    - Structure configuration
		    - Internal metadata
		    - Stored blocks and values

		Returns:
		    dict:
		        Serializable snapshot representing the current
		        state of the structure.

		"""
		return handle_export_snapshot(_service())

	@router.post('/import')
	async def import_state(request: SnapshotRequest):
		"""Restore the structure from a snapshot.

		This endpoint loads a previously exported snapshot and
		reconstructs the external search structure state.

		Args:
		    request (SnapshotRequest):
		        Request containing the serialized snapshot.

		Returns:
		    dict:
		        Information about the restored structure state.

		"""
		return handle_import_snapshot(_service(), request)

	@router.post('/insert')
	def insert_value(request: InsertRequest):
		"""Insert a new key into the external structure.

		Args:
		    request (InsertRequest):
		        Request containing the value to insert.

		Returns:
		    dict:
		        Information about the insertion result.

		"""
		return handle_external_insert(_service(), request)

	@router.get('/search/{value}')
	def search_value(value: str):
		"""Search for a key in the external structure.

		Args:
		    value (str):
		        Key to search for.

		Returns:
		    list:
		        List containing the positions where the key
		        was found.

		"""
		return handle_search(_service(), value)

	@router.delete('/delete/{value}')
	def delete_value(value: str):
		"""Delete a key from the external structure.

		Args:
		    value (str):
		        Key to remove from the structure.

		Returns:
		    dict:
		        Information about the deletion result.

		"""
		return handle_delete(_service(), value)

	return router
