"""
Expose API endpoints to configure and operate a hash table structure.

Provide routes to configure the hash function and collision resolution
strategy dynamically. Offer endpoints for creating the structure,
inserting values, searching elements, deleting entries, and retrieving
the current table state.

Raise HTTP errors when required configuration steps are missing or when
invalid parameters are provided.

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
	CreateRequest,
	InsertRequest,
	create_search_router,
	handle_create,
	handle_delete,
	handle_insert,
	handle_search,
)
from app.services.search.hash.collision_simple import (
	DoubleHashResolver,
	LinearResolver,
	QuadraticResolver,
)
from app.services.search.hash.hash_table import (
	CollisionWithoutStrategyError,
	HashTable,
)

from .helpers import build_hash_function
from .schemas import CollisionStrategyRequest, HashFunctionRequest

router = APIRouter(prefix='/hash', tags=['Hash Table'])

service: HashTable | None = None


@router.post('/set-hash')
async def set_hash_function(request: HashFunctionRequest):
	"""
	Configure the primary hash function.

	Build and assign a hash function implementation based on the
	provided configuration. Initialize a new hash table instance
	using the selected strategy.

	Args:
		request: Contain hash function configuration parameters.

	Returns:
		dict: Confirmation message indicating successful configuration.

	"""
	global service

	hash_func = build_hash_function(request)
	service = HashTable(hash_func)

	return {'message': 'Función hash configurada'}


@router.post('/set-collision')
async def set_collision_strategy(request: CollisionStrategyRequest):
	"""
	Configure the collision resolution strategy.

	Activate either chaining or open addressing with linear,
	quadratic, or double hashing strategies. Require a previously
	configured hash function.

	Args:
		request: Contain collision strategy configuration parameters.

	Returns:
		dict: Confirmation message indicating successful configuration.

	Raises:
		HTTPException: If the hash function is not defined, required
			parameters are missing, or the strategy type is invalid.

	"""
	if service is None:
		raise HTTPException(status_code=400, detail='Defina primero la función hash')

	if request.type == 'chaining':
		service.set_chaining()
		return {'message': 'Modo encadenamiento activado'}

	if request.type == 'linear':
		service.resolver = LinearResolver()
		service.mode = 'open'
		return {'message': 'Colisión lineal activada'}

	if request.type == 'quadratic':
		service.resolver = QuadraticResolver()
		service.mode = 'open'
		return {'message': 'Colisión cuadrática activada'}

	if request.type == 'double':
		if not request.second_hash_type:
			raise HTTPException(status_code=400, detail='Se requiere segunda función hash')

		second_hash = build_hash_function(HashFunctionRequest(type=request.second_hash_type))

		service.resolver = DoubleHashResolver(second_hash)
		service.mode = 'open'
		return {'message': 'Doble hashing activado'}

	raise HTTPException(status_code=400, detail='Estrategia inválida')


def get_base_router():
	"""
	Create and return a router exposing base search operations.

	Ensure the hash table is initialized before generating the router.

	Returns:
		APIRouter: Router configured with standard search endpoints.

	Raises:
		HTTPException: If the hash function has not been defined.

	"""
	if service is None:
		raise HTTPException(status_code=400, detail='Defina primero la función hash')

	base_router = create_search_router(service, prefix='', tag='Hash Table')
	return base_router


@router.post('/create')
async def create_structure(request: CreateRequest):
	"""
	Initialize the hash table structure.

	Create the internal table using the provided configuration
	parameters such as size and digit constraints.

	Args:
		request: Contain structure creation parameters.

	Returns:
		dict: Operation result.

	Raises:
		HTTPException: If the hash function has not been defined.

	"""
	if service is None:
		raise HTTPException(status_code=400, detail='Defina primero la función hash')

	return handle_create(service, request)


@router.get('/state')
async def get_state():
	"""
	Retrieve the current hash table state.

	Return table size, digit constraint, and stored data.

	Returns:
		dict: Current structure state.

	Raises:
		HTTPException: If the hash function has not been defined.

	"""
	if service is None:
		raise HTTPException(status_code=400, detail='Defina primero la función hash')

	return {
		'size': service.size,
		'digits': service.digits,
		'data': service.data,
	}


@router.post('/insert')
async def insert_value(request: InsertRequest):
	"""
	Insert a value into the hash table.

	Delegate insertion logic to the underlying service and
	handle collision configuration errors.

	Args:
		request: Contain value insertion parameters.

	Returns:
		dict: Operation result.

	Raises:
		HTTPException: If the structure is not configured or if
			a collision occurs without a defined strategy.

	"""
	if service is None:
		raise HTTPException(status_code=400, detail='Defina primero la función hash')

	try:
		return handle_insert(service, request)
	except CollisionWithoutStrategyError as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.get('/search/{value}')
async def search_value(value: str):
	"""
	Search for a value in the hash table.

	Delegate search operation to the underlying service.

	Args:
		value: Value to search.

	Returns:
		dict: Search result.

	"""
	return handle_search(service, value)


@router.delete('/delete/{value}')
async def delete_value(value: str):
	"""
	Delete a value from the hash table.

	Delegate deletion logic to the underlying service.

	Args:
		value: Value to remove.

	Returns:
		dict: Operation result.

	"""
	return handle_delete(service, value)
