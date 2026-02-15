"""Define the FastAPI router for linear search operations.

It provides endpoints to create, manage, and query a linear search data structure,
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

from app.services.search.linear_search import LinearSearchService as LinearSearch

router = APIRouter(prefix='/linear-search', tags=['Linear Search'])
service = LinearSearch()


class CreateRequest(BaseModel):
	"""Request model for creating a new linear search structure.

	Attributes:
	    size (int): The maximum size of the data structure.
	    digits (int): The exact number of digits required for each value.

	"""

	size: int
	digits: int


class InsertRequest(BaseModel):
	"""Request model for inserting a value into the linear search structure.

	Attributes:
	    value (str): The numeric value to insert.

	"""

	value: str

def normalize_value(value: str, digits: int) -> str:
    """Normalize value to required digit length."""
    if not value.isdigit():
        raise HTTPException(status_code=400, detail="Value must be numeric")

    if len(value) > digits:
        raise HTTPException(
            status_code=400,
            detail=f"Value cannot exceed {digits} digits",
        )

    return value.zfill(digits)

@router.post('/create')
async def create_structure(request: CreateRequest):
	"""Create a new linear search data structure with specified parameters.

	Args:
	    request (CreateRequest): The request containing size and digits parameters.

	Returns:
	    dict: A message confirming successful creation with the provided parameters.

	Raises:
	    HTTPException: If an unexpected error occurs during structure creation.

	"""
	try:
		service.create(request.size, request.digits)
		return {
			'message': 'Estructura creada',
			'size': request.size,
			'digits': request.digits,
		}
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))


@router.get('/state')
async def get_state():
	"""Retrieve the current state of the linear search structure.

	Returns:
	    dict: Contains the size, digits constraint, and current data array.
	          Returns default values if the structure is not initialized.

	"""
	try:
		return {'size': service.size, 'digits': service.digits, 'data': service.data}
	except Exception:
		return {'size': 0, 'digits': 0, 'data': []}


@router.post('/insert')
async def insert_value(request: InsertRequest):
	"""Insert a numeric value into the linear search structure.

	Args:
	    request (InsertRequest): The request containing the value to insert.

	Returns:
	    dict: A message confirming insertion with the position where it was inserted.

	Raises:
	    HTTPException: If the structure is not initialized, value length doesn't match
	                  digits constraint, value is not numeric, or other errors occur.

	"""
	try:
		if not service.initialized:
			raise HTTPException(status_code=400, detail='Estructura no inicializada')

		value = normalize_value(request.value, service.digits)

		if value in service.data:
			raise HTTPException(
				status_code=400,
				detail=f'La clave debe tener exactamente {service.digits} digitos',
			)

		if not request.value.isdigit():
			raise HTTPException(status_code=400, detail='Clave debe ser numerica')

		position = service.insert(value)
		ordered_position = service.search(request.value)
		return {
			'message': (
				f'Clave {request.value} insertada en la dirección '
				f'{ordered_position} luego de ordenar'
			),
			'position': position,
		}
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))


@router.get('/search/{value}')
async def search_value(value: str):
	"""Search for a value in the linear search structure.

	Args:
	    value (str): The value to search for.

	Returns:
	    dict: Contains the search results with positions where the value was found.

	Raises:
	    HTTPException: If an unexpected error occurs during the search.

	"""
	try:
		if not service.initialized:
			return {'position': [], 'value': value}

		result = service.search(value)
		return {'position': result, 'value': value}
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))


@router.delete('/delete/{value}')
async def delete_value(value: str):
	"""Delete all occurrences of a value from the linear search structure.

	Args:
	    value (str): The value to delete.

	Returns:
	    dict: A message confirming deletion with the positions where it was deleted,
	          or a not found message if the value doesn't exist.

	Raises:
	    HTTPException: If an unexpected error occurs during deletion.

	"""
	try:
		if not service.initialized:
			return {'message': 'Estructura no incializada', 'position': []}

		result = service.delete(value)
		if not result:
			return {'message': f'Clave {value} no encontrada', 'position': []}
		return {'message': f'Clave {value} eliminada', 'position': result}
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))
