"""Create reusable FastAPI router for search services.

Define request models, input normalization utilities, and a factory
function that builds an APIRouter exposing common CRUD endpoints
for search-based services such as linear or binary search.

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
from pydantic import BaseModel

from app.controllers.search.snapshot import (
	SnapshotRequest,
	handle_export_snapshot,
	handle_import_snapshot,
)


class CreateRequest(BaseModel):
	"""Represent request body for structure creation.

	Attributes:
	    size (int): Maximum number of elements allowed.
	    digits (int): Required number of digits per key.

	"""

	size: int
	digits: int


class InsertRequest(BaseModel):
	"""Represent request body for key insertion.

	Attributes:
	    value (str): Numeric key to insert.

	"""

	value: str


def normalize_value(value: str, digits: int) -> str:
	"""Normalize numeric value to required digit length.

	Validate that the value is numeric and does not exceed the
	configured digit length. Pad the value with leading zeros
	if necessary.

	Args:
	    value (str): Raw value provided by the client.
	    digits (int): Required number of digits.

	Returns:
	    str: Zero-padded numeric string with exact digit length.

	Raises:
	    HTTPException: If the value is not numeric or exceeds
	        the allowed number of digits.

	"""
	if not value.isdigit():
		raise HTTPException(status_code=400, detail='Clave debe ser un valor numérico')

	if len(value) > digits:
		raise HTTPException(
			status_code=400,
			detail=f'La clave no puede excederse de {digits} digitos',
		)

	return value.zfill(digits)


def handle_create(service, request: CreateRequest) -> dict:
	"""Handle structure creation logic.

	This helper function initializes the provided search
	structure using the configuration received in the request.

	Args:
		service:
			Search service instance implementing the
			``create`` method.

		request (CreateRequest):
			Request containing the structure configuration.

	Returns:
		dict:
			Dictionary containing:

			    - message:
			        Confirmation message.

			    - size:
			        Configured structure size.

			    - digits:
			        Configured digit length.

	"""
	service.create(request.size, request.digits)
	return {
		'message': 'Estructura creada',
		'size': request.size,
		'digits': request.digits,
	}


def handle_insert(service, request: InsertRequest) -> dict:
	"""Handle insertion logic for search structures.

	The function validates that the structure has been
	initialized, normalizes the provided value according
	to the configured digit length, inserts the value,
	and retrieves its resulting position.

	Args:
		service:
			Search service instance implementing
			``insert`` and ``search``.

		request (InsertRequest):
			Request containing the value to insert.

	Returns:
		dict:
			Dictionary containing:

			    - message:
			        Human-readable insertion result.

			    - position:
			        Position generated for the inserted value.

	Raises:
		HTTPException:
			If the structure has not been initialized.

	"""
	if not service.initialized:
		raise HTTPException(
			status_code=400,
			detail='Estructura no inicializada',
		)

	value = normalize_value(request.value, service.digits)
	service.insert(value)
	position = service.search(value)
	return {
		'message': f'Clave {value} insertada en la dirección {position}',
		'position': position,
	}


def handle_search(service, value: str) -> dict:
	"""Handle search logic for search structures.

	The function searches the provided value inside
	the structure and formats the response in a
	consistent API-friendly format.

	Args:
		service:
			Search service instance implementing
			the ``search`` method.

		value (str):
			Value to search inside the structure.

	Returns:
		dict:
			Dictionary containing:

			    - position:
			        Matching positions or an empty list.

			    - value:
			        Searched value.

			    - message:
			        Human-readable search result.

	"""
	if not service.initialized:
		return {'position': [], 'value': value, 'message': 'EStructura no inicializada'}

	result = service.search(value)

	if result:
		return {
			'position': result,
			'value': value,
			'message': f'Clave encontrada en la dirección {result}',
		}

	return {'position': [], 'value': value, 'message': 'Clave no encontrada en la estructura'}


def handle_delete(service, value: str) -> dict:
	"""Handle deletion logic for search structures.

	The function removes the specified value from
	the structure and formats the operation result.

	Args:
		service:
			Search service instance implementing
			the ``delete`` method.

		value (str):
			Value to remove from the structure.

	Returns:
		dict:
			Dictionary containing:

			    - message:
			        Human-readable deletion result.

			    - position:
			        Deleted positions or an empty list
			        if the value was not found.

	"""
	if not service.initialized:
		return {
			'message': 'Estructura no inicializada',
			'position': [],
		}

	result = service.delete(value)

	if not result:
		return {
			'message': f'Clave {value} no encontrada',
			'position': [],
		}

	return {
		'message': f'Clave {value} eliminada de la dirección {result}',
		'position': result,
	}


def create_search_router(service, prefix: str, tag: str) -> APIRouter:
	"""Build and configure a reusable FastAPI router.

	The generated router exposes common CRUD operations
	for search-based structures, including creation,
	state inspection, insertion, searching, deletion,
	reset, export, and import operations.

	The router delegates all operational logic to the
	provided service instance.

	Args:
		service:
			Search service instance implementing
			the required CRUD operations.

		prefix (str):
			URL prefix assigned to the router.

		tag (str):
			Tag used to group endpoints in the
			OpenAPI documentation.

	Returns:
		APIRouter:
			Configured FastAPI router instance
			containing all generated endpoints.

		Endpoints:
			POST /create:
				Create and initialize the structure.

			GET /state:
				Retrieve the current internal state.

			POST /export:
				Export the current structure snapshot.

			POST /import:
				Restore the structure from a snapshot.

			POST /reset:
				Reset the structure state.

			POST /insert:
				Insert a value into the structure.

			GET /search/{value}:
				Search for a value.

			DELETE /delete/{value}:
				Delete a value from the structure.

	"""
	router = APIRouter(prefix=prefix, tags=[tag])

	@router.post('/create')
	async def create_structure(request: CreateRequest):
		"""Create and initialize the search structure.

		Args:
			request (CreateRequest):
				Request containing the structure configuration.

		Returns:
			dict:
				Structure creation result.

		Raises:
			HTTPException:
				If an unexpected internal error occurs.

		"""
		try:
			return handle_create(service, request)
		except Exception as e:
			raise HTTPException(status_code=500, detail=str(e))

	@router.get('/state')
	async def get_state():
		"""Retrieve the current internal state of the structure.

		Returns:
			dict:
				Dictionary containing:

					- size:
						Structure capacity.

					- digits:
						Configured digit length.

					- data:
						Internal stored values.

		"""
		return {
			'size': service.size,
			'digits': service.digits,
			'data': service.data,
		}

	@router.post('/export')
	async def export_state():
		"""Export the current structure snapshot.

		Returns:
			dict:
				Serialized snapshot representing the
				current structure state.

		"""
		return handle_export_snapshot(service)

	@router.post('/import')
	async def import_state(request: SnapshotRequest):
		"""Restore the structure from a snapshot.

		Args:
			request (SnapshotRequest):
				Request containing serialized snapshot data.

		Returns:
			dict:
				Restored structure snapshot.

		"""
		return handle_import_snapshot(service, request)

	@router.post('/reset')
	async def reset_structure():
		"""Reset the search structure state.

		The operation clears all stored values and restores
		the structure to its initial empty state.

		Returns:
			dict:
				Confirmation message.

		"""
		service.reset()
		return {'message': 'Estructura reseteada'}

	@router.post('/insert')
	async def insert_value(request: InsertRequest):
		"""Insert a value into the search structure.

		Args:
			request (InsertRequest):
				Request containing the value to insert.

		Returns:
			dict:
				Insertion result including generated position.

		Raises:
			HTTPException:
				If the insertion fails due to validation
				or internal structure errors.

		"""
		try:
			return handle_insert(service, request)
		except ValueError as e:
			raise HTTPException(status_code=400, detail=str(e))
		except HTTPException:
			raise
		except Exception as e:
			raise HTTPException(status_code=500, detail=str(e))

	@router.get('/search/{value}')
	async def search_value(value: str):
		"""Search for a value inside the structure.

		Args:
			value (str):
				Value to search.

		Returns:
			dict:
				Search result information.

		"""
		return handle_search(service, value)

	@router.delete('/delete/{value}')
	async def delete_value(value: str):
		"""Delete a value from the structure.

		Args:
			value (str):
				Value to remove.

		Returns:s
			dict:
				Deletion result information.

		"""
		return handle_delete(service, value)

	return router
