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
from app.controllers.search.snapshot import SnapshotRequest
from app.services.search.hash.collision_simple import (
	DoubleHashResolver,
	LinearResolver,
	QuadraticResolver,
)
from app.services.search.hash.hash_table import (
	CollisionWithoutStrategyError,
	HashTable,
)
from app.services.search.persistence import hash_function_from_snapshot

from .helpers import build_hash_function
from .schemas import CollisionStrategyRequest, HashFunctionRequest

router = APIRouter(prefix='/hash', tags=['Hash Table'])

service: HashTable | None = None


@router.post('/set-hash')
async def set_hash_function(request: HashFunctionRequest):
	"""Configure the primary hash function for the hash table.

	This endpoint initializes the global hash table service using
	the hash function specified in the request.

	The configured hash function will later be used to calculate
	the positions of inserted keys.

	Supported hash functions include:

	    - mod
	    - square
	    - truncation
	    - folding

	Args:
	    request (HashFunctionRequest):
	        Request containing the hash function configuration.

	Returns:
	    dict:
	        Confirmation message indicating that the hash
	        function was successfully configured.

	"""
	global service

	hash_func = build_hash_function(request)
	service = HashTable(hash_func)

	return {'message': 'Función hash configurada'}


@router.post('/set-collision')
async def set_collision_strategy(request: CollisionStrategyRequest):
	"""Configure the collision resolution strategy.

	This endpoint defines how collisions will be handled when
	multiple keys are mapped to the same table position.

	Supported collision strategies:

	    - chaining
	    - linear probing
	    - quadratic probing
	    - double hashing

	Double hashing requires a second hash function.

	Args:
	    request (CollisionStrategyRequest):
	        Request containing the collision strategy type
	        and optional secondary hash configuration.

	Returns:
	    dict:
	        Confirmation message describing the activated
	        collision strategy.

	Raises:
	    HTTPException:
	        If the hash table has not been initialized,
	        if the request parameters are invalid,
	        or if a required secondary hash function
	        is missing.

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


@router.post('/create')
async def create_structure(request: CreateRequest):
	"""Initialize the hash table structure.

	This endpoint allocates the internal table storage and
	configures validation parameters such as the number of
	slots and the number of digits allowed for stored keys.

	Args:
	    request (CreateRequest):
	        Request containing the structure configuration.

	Returns:
	    dict:
	        Information about the initialized structure.

	Raises:
	    HTTPException:
	        If the hash function has not been configured
	        or if the creation parameters are invalid.

	"""
	if service is None:
		raise HTTPException(status_code=400, detail='Defina primero la función hash')

	try:
		return handle_create(service, request)
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.get('/state')
async def get_state():
	"""Retrieve the current hash table state.

	This endpoint exposes the internal representation of the
	hash table for debugging and visualization purposes.

	The response includes:

	    - Table size
	    - Digit configuration
	    - Stored data

	Returns:
	    dict:
	        Internal state of the hash table.

	Raises:
	    HTTPException:
	        If the hash table has not been initialized.

	"""
	if service is None:
		raise HTTPException(status_code=400, detail='Defina primero la función hash')

	return {
		'size': service.size,
		'digits': service.digits,
		'data': service.data,
	}


@router.post('/export')
async def export_state():
	"""Export the current hash table snapshot.

	This endpoint serializes the complete state of the hash
	table into a snapshot representation that can later be
	restored using the ``/import`` endpoint.

	The exported snapshot includes:

	    - Hash function configuration
	    - Collision strategy configuration
	    - Table metadata
	    - Stored values and internal state

	Returns:
	    dict:
	        Serializable snapshot representing the current
	        hash table state.

	Raises:
	    HTTPException:
	        If the hash table has not been initialized.

	"""
	if service is None:
		raise HTTPException(status_code=400, detail='Defina primero la función hash')

	return service.save_state()


@router.post('/import')
async def import_state(request: SnapshotRequest):
	"""Restore the hash table from a snapshot.

	This endpoint recreates a previously exported hash table
	using the snapshot provided in the request.

	If the service instance does not exist yet, the endpoint
	automatically reconstructs the corresponding hash function
	before loading the snapshot state.

	The imported snapshot restores:

	    - Hash function configuration
	    - Collision strategy configuration
	    - Table metadata
	    - Stored data and internal state

	Args:
	    request (SnapshotRequest):
	        Request containing the serialized snapshot.

	Returns:
	    dict:
	        Snapshot representing the restored hash table state.

	Raises:
	    HTTPException:
	        If the snapshot is invalid or cannot be restored.

	"""
	global service

	if service is None:
		hash_func = hash_function_from_snapshot(
			request.snapshot.get('config', {}).get('hash_function')
		)
		service = HashTable(hash_func)

	try:
		service.load_state(request.snapshot)
		return service.save_state()
	except ValueError as exc:
		raise HTTPException(status_code=400, detail=str(exc))


@router.post('/insert')
async def insert_value(request: InsertRequest):
	"""Insert a value into the hash table.

	This endpoint inserts a new key into the configured
	hash table using the active collision resolution strategy.

	Args:
	    request (InsertRequest):
	        Request containing the value to insert.

	Returns:
	    dict:
	        Information about the insertion result.

	Raises:
	    HTTPException:
	        If the hash table has not been initialized,
	        if a collision occurs without a configured
	        strategy, or if insertion constraints fail
	        (duplicate keys, full table, invalid values).

	"""
	if service is None:
		raise HTTPException(status_code=400, detail='Defina primero la función hash')

	try:
		return handle_insert(service, request)
	except (CollisionWithoutStrategyError, ValueError) as e:
		# Atrapa tanto colisiones como duplicados o tabla llena
		raise HTTPException(status_code=400, detail=str(e))


@router.get('/search/{value}')
async def search_value(value: str):
	"""Search for a value in the hash table.

	This endpoint searches the hash table for the specified key
	and returns its matching positions if found.

	Args:
	    value (str):
	        Value to search for.

	Returns:
	    dict:
	        Search result containing the matching positions.

	Raises:
	    HTTPException:
	        If the hash table has not been initialized
	        or if the search operation fails.

	"""
	if service is None:
		raise HTTPException(status_code=400, detail='Defina primero la función hash')
	try:
		return handle_search(service, value)
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.delete('/delete/{value}')
async def delete_value(value: str):
	"""Delete a value from the hash table.

	This endpoint removes the specified key from the hash table.

	Args:
	    value (str):
	        Value to remove.

	Returns:
	    dict:
	        Information about the deletion result.

	Raises:
	    HTTPException:
	        If the hash table has not been initialized
	        or if the deletion operation fails.

	"""
	if service is None:
		raise HTTPException(status_code=400, detail='Defina primero la función hash')

	try:
		return handle_delete(service, value)
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))
