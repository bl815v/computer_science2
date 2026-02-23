"""
Expose API endpoints to configure and operate a hash table structure.

Provide routes to configure the hash function and collision resolution
strategy dynamically. Offer endpoints for creating the structure,
inserting values, searching elements, deleting entries, and retrieving
the current table state.

Raise HTTP errors when required configuration steps are missing or when
invalid parameters are provided.

Author: Juan Esteban Bedoya <jebedoyal@udistrital.edu.co>
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
	"""Configure the primary hash function."""
	global service

	hash_func = build_hash_function(request)
	service = HashTable(hash_func)

	return {'message': 'Función hash configurada'}


@router.post('/set-collision')
async def set_collision_strategy(request: CollisionStrategyRequest):
	"""Configure the collision resolution strategy."""
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
	"""Initialize the hash table structure."""
	if service is None:
		raise HTTPException(status_code=400, detail='Defina primero la función hash')

	try:
		return handle_create(service, request)
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.get('/state')
async def get_state():
	"""Retrieve the current hash table state."""
	if service is None:
		raise HTTPException(status_code=400, detail='Defina primero la función hash')

	return {
		'size': service.size,
		'digits': service.digits,
		'data': service.data,
	}


@router.post('/insert')
async def insert_value(request: InsertRequest):
	"""Insert a value into the hash table and handle logic errors."""
	if service is None:
		raise HTTPException(status_code=400, detail='Defina primero la función hash')

	try:
		return handle_insert(service, request)
	except (CollisionWithoutStrategyError, ValueError) as e:
		# Atrapa tanto colisiones como duplicados o tabla llena
		raise HTTPException(status_code=400, detail=str(e))


@router.get('/search/{value}')
async def search_value(value: str):
	"""Search for a value in the hash table."""
	if service is None:
		raise HTTPException(status_code=400, detail='Defina primero la función hash')
	try:
		return handle_search(service, value)
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.delete('/delete/{value}')
async def delete_value(value: str):
	"""Delete a value from the hash table."""
	if service is None:
		raise HTTPException(status_code=400, detail='Defina primero la función hash')

	try:
		return handle_delete(service, value)
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))