"""
API router for external hash-based search structures.

This module exposes REST endpoints that allow clients to interact with an
external hash search structure. The structure stores data in blocks and
uses a hash function to determine the ideal position for each key. When
collisions occur, values are stored in overflow lists associated with
each block.

The router allows clients to:

    - Configure the hash function used by the structure
    - Initialize the external structure
    - Inspect the internal state (blocks and overflow areas)
    - Insert new keys
    - Search for keys
    - Delete keys

Hash functions supported:

    - mod
    - square
    - truncation
    - folding
    - base_conversion (custom implementation)

The structure must be configured with a hash function before it can be
created or used.

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

from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.controllers.search.base_search import InsertRequest, handle_delete, handle_search
from app.controllers.search.external.base_external import (
	CreateExternalRequest,
	handle_external_create,
	handle_external_insert,
)
from app.services.search.external.hash_external import (
	BaseConversionHash,
	HashExternalSearch,
)
from app.services.search.hash.hash_function import (
	FoldingHash,
	HashFunction,
	ModHash,
	SquareHash,
	TruncationHash,
)
from app.services.search.hash.hash_table import HashTable

router = APIRouter(prefix='/hash-external', tags=['Hash External'])
service: Optional[HashExternalSearch] = None


class ExternalHashFunctionRequest(BaseModel):
	"""Request model used to configure the hash function.

	This model defines the parameters required to build a hash function
	for the external hash structure.

	Supported hash types:

	    - "mod"
	    - "square"
	    - "truncation"
	    - "folding"
	    - "base_conversion"

	Some types require additional parameters.

	Attributes:
	    type (str):
	        Type of hash function to use.

	    positions (Optional[List[int]]):
	        Positions used by the truncation hash function.

	    group_size (Optional[int]):
	        Size of digit groups used by the folding hash function.

	    operation (Optional[str]):
	        Operation used in folding (e.g., "sum").

	    base (Optional[int]):
	        Base used in the base conversion hash function.

	"""

	type: str
	positions: Optional[List[int]] = None
	group_size: Optional[int] = None
	operation: Optional[str] = None
	base: Optional[int] = None


def _build_external_hash_function(req: ExternalHashFunctionRequest) -> HashFunction:
	"""Build the hash function used by the external structure.

	This helper function constructs the appropriate hash function
	based on the configuration received from the client.

	It supports both standard hash functions already implemented
	in the system and the custom ``BaseConversionHash``.

	Args:
	    req (ExternalHashFunctionRequest):
	        Configuration describing the desired hash function.

	Returns:
	    HashFunction:
	        Instantiated hash function ready to be used by the
	        external hash structure.

	Raises:
	    HTTPException:
	        If the request parameters are invalid or incomplete.

	"""
	t = req.type
	if t == 'base_conversion':
		if req.base is None:
			raise HTTPException(status_code=400, detail='Se requiere "base" para base_conversion')
		return BaseConversionHash(req.base)

	if t == 'mod':
		return ModHash()
	if t == 'square':
		return SquareHash()
	if t == 'truncation':
		if not req.positions:
			raise HTTPException(status_code=400, detail='Se requieren posiciones para truncation')
		return TruncationHash(req.positions)
	if t == 'folding':
		if not req.group_size:
			raise HTTPException(status_code=400, detail='Se requiere group_size para folding')
		return FoldingHash(req.group_size, req.operation or 'sum')

	raise HTTPException(status_code=400, detail='Tipo de hash no válido')


@router.post('/set-hash')
async def set_hash_function(request: ExternalHashFunctionRequest):
	"""Configure the primary hash function for the external structure.

	This endpoint must be called before creating the structure. It
	initializes the global service instance with the selected hash
	function.

	Args:
	    request (ExternalHashFunctionRequest):
	        Configuration describing the hash function.

	Returns:
	    dict:
	        Confirmation message indicating that the hash function
	        was successfully configured.

	"""
	global service

	hash_func = _build_external_hash_function(request)
	service = HashExternalSearch(hash_func)
	return {'message': 'Función hash configurada para HashExternalSearch'}


@router.post('/create')
def create_structure(request: CreateExternalRequest):
	"""Initialize the external hash structure.

	This endpoint creates the block-based structure and prepares
	the overflow lists used for collision handling.

	Args:
	    request (CreateExternalRequest):
	        Request containing the size of the structure and the
	        number of digits used for key validation.

	Returns:
	    dict:
	        Information about the created structure.

	Raises:
	    HTTPException:
	        If the hash function has not been configured or if
	        the creation parameters are invalid.

	"""
	if service is None:
		raise HTTPException(status_code=400, detail='Defina primero la función hash con /set-hash')

	try:
		return handle_external_create(service, request)
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.get('/state')
async def get_state():
	"""Retrieve the current internal state of the structure.

	This endpoint returns debugging and visualization information
	about the external hash structure.

	The response includes:

	    - Table size
	    - Digit configuration
	    - Block size
	    - Main blocks
	    - Overflow lists
	    - Block offsets

	Returns:
	    dict:
	        Complete internal representation of the structure.

	Raises:
	    HTTPException:
	        If the structure has not been initialized.

	"""
	if service is None:
		raise HTTPException(status_code=400, detail='Defina primero la función hash con /set-hash')

	return {
		'size': service.size,
		'digits': service.digits,
		'block_size': service.block_size,
		'blocks': service.blocks,
		'overflow': service.overflow,
		'block_offsets': service.block_offsets,
	}


@router.post('/insert')
def insert_value(request: InsertRequest):
	"""Insert a new key into the external hash structure.

	Args:
	    request (InsertRequest):
	        Request containing the key to insert.

	Returns:
	    dict:
	        Information about the insertion result.

	Raises:
	    HTTPException:
	        If the structure is not initialized or if the
	        insertion fails (duplicate keys, validation errors,
	        or internal constraints).

	"""
	if service is None:
		raise HTTPException(status_code=400, detail='Defina primero la función hash con /set-hash')

	try:
		return handle_external_insert(service, request)
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.get('/search/{value}')
def search_value(value: str):
	"""Search a value in the external hash structure."""
	if service is None:
		raise HTTPException(
			status_code=400,
			detail='Defina primero la función hash con /set-hash',
		)

	try:
		results = service.search(value)

		formatted = []

		for r in results:

			if r['global_position'] > service.size:
				formatted.append(
					{
						'global_position': r['global_position'],
						'block_index': r['block_index'],
						'location': 'overflow',
						'overflow_position': r['block_position'],
					}
				)
			else:
				formatted.append(
					{
						'global_position': r['global_position'],
						'block_index': r['block_index'],
						'location': 'block',
						'block_position': r['block_position'],
					}
				)

		return formatted

	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.delete('/delete/{value}')
def delete_value(value: str):
	"""Elimina una clave de la estructura externa."""
	if service is None:
		raise HTTPException(status_code=400, detail='Defina primero la función hash con /set-hash')

	try:
		return handle_delete(service, value)
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))
