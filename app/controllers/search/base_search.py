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
	"""Handle structure creation logic."""
	service.create(request.size, request.digits)
	return {
		'message': 'Estructura creada',
		'size': request.size,
		'digits': request.digits,
	}


def handle_insert(service, request: InsertRequest) -> dict:
	"""Handle insertion logic."""
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
	"""Handle search logic."""
	if not service.initialized:
		return {
			'position': [],
			'value': value,
			'message': 'EStructura no inicializada'
		}

	result = service.search(value)

	if result:
		return {
			'position': result,
			'value': value,
			'message': f'Clave encontrada en la dirección {result}'
		}

	return {
		'position': [],
		'value': value,
		'message': 'Clave no encontrada en la estructura'
	}


def handle_delete(service, value: str) -> dict:
	"""Handle delete logic."""
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
	"""Build and return an APIRouter for a search service.

	Expose endpoints for structure creation, state retrieval,
	insertion, search, and deletion operations.

	Args:
	    service: Instance of a search service implementing
	        create, insert, search, and delete methods.
	    prefix (str): URL prefix for the router.
	    tag (str): Tag name used for API documentation grouping.

	Returns:
	    APIRouter: Configured router instance.

	"""
	router = APIRouter(prefix=prefix, tags=[tag])

	@router.post('/create')
	async def create_structure(request: CreateRequest):
		try:
			return handle_create(service, request)
		except Exception as e:
			raise HTTPException(status_code=500, detail=str(e))

	@router.get('/state')
	async def get_state():
		return {
			'size': service.size,
			'digits': service.digits,
			'data': service.data,
		}

	@router.post('/insert')
	async def insert_value(request: InsertRequest):
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
		return handle_search(service, value)

	@router.delete('/delete/{value}')
	async def delete_value(value: str):
		return handle_delete(service, value)

	return router
