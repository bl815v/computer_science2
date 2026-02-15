"""Define the FastAPI router for binary search operations.

It provides endpoints to create, manage, and query a binary search data structure,
including operations to insert values, search for values, and delete values
from the structure.

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

from app.services.search.binary_search import BinarySearchService as BinarySearch

router = APIRouter(prefix='/binary-search', tags=['Binary Search'])
service = BinarySearch()


class CreateRequest(BaseModel):
	"""Request model for creating a new binary search structure.

	Attributes:
	    size (int): The maximum size of the data structure.
	    digits (int): The exact number of digits required for each value.

	"""

	size: int
	digits: int


class InsertRequest(BaseModel):
	"""Request model for inserting a value into the binary search structure.

	Attributes:
	    value (str): The numeric value to insert.

	"""

	value: str


@router.post('/create')
async def create_structure(request: CreateRequest):
	"""Create a new binary search data structure with specified parameters."""
	try:
		service.create(request.size, request.digits)
		return {
			'mensaje': 'Estructura creada',
			'tamaño': request.size,
			'digitos': request.digits,
		}
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))


@router.get('/state')
async def get_state():
	"""Retrieve the current state of the binary search structure."""
	try:
		return {
			'tamaño': service.size,
			'digitos': service.digits,
			'datos': service.data,
		}
	except Exception:
		return {'tamaño': 0, 'digitos': 0, 'datos': []}


@router.post('/insert')
async def insert_value(request: InsertRequest):
	"""Insert a numeric value into the binary search structure."""
	try:
		if not service.initialized:
			raise HTTPException(status_code=400, detail='Estructura no inicializada')

		if len(request.value) != service.digits:
			raise HTTPException(
				status_code=400,
				detail=f'La clave debe tener exactamente {service.digits} digitos',
			)

		if not request.value.isdigit():
			raise HTTPException(status_code=400, detail='Clave debe ser numerica')

		position = service.insert(request.value)
		ordered_position = service.search(request.value)

		return {
			'mensaje': (
				f'Clave {request.value} insertada en la dirección '
				f'{ordered_position} luego de ordenar'
			),
			'dirección': position,
		}

	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))


@router.get('/search/{value}')
async def search_value(value: str):
	"""Search for a value in the binary search structure."""
	try:
		if not service.initialized:
			return {'dirección': [], 'clave': value}

		result = service.search(value)
		return {'dirección': result, 'clave': value}

	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))


@router.delete('/delete/{value}')
async def delete_value(value: str):
	"""Delete all occurrences of a value from the binary search structure."""
	try:
		if not service.initialized:
			return {'mensaje': 'Estructura no incializada', 'dirección eliminada': []}

		result = service.delete(value)

		if not result:
			return {'mensaje': f'Clave {value} no encontrada', 'dirección': []}

		return {'mensaje': f'Clave {value} eliminada', 'dirección': result}

	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))
