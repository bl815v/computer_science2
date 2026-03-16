"""
API router for the dynamic external hash search structure.

This module exposes FastAPI endpoints for configuring and interacting with
a dynamic external hash structure. The structure supports configurable
hash functions, dynamic bucket expansion, and bucket reduction based on
load factor thresholds.

The router allows clients to:

- Configure the hash function.
- Create the dynamic hash structure.
- Inspect the current internal state.
- Use standard external search operations provided by the shared router
  factory (insert, search, delete).

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

from app.controllers.search.external.external_router_factory import (
	create_external_search_router,
)
from app.services.search.external.dynamic_hash import DynamicHashExternalSearch
from app.services.search.hash.hash_function import (
	FoldingHash,
	ModHash,
	SquareHash,
	TruncationHash,
)

router = APIRouter(prefix='/dynamic-hash', tags=['Dynamic Hash External'])

service: Optional[DynamicHashExternalSearch] = None
hash_func = None


class HashFunctionRequest(BaseModel):
	"""Request model used to configure the hash function.

	Attributes:
	    type (str): Type of hash function to configure.
	        Supported values include:
	        - "mod"
	        - "square"
	        - "truncation"
	        - "folding"

	    positions (Optional[List[int]]): Positions used by the truncation
	        hash function to extract digits from the key.

	    group_size (Optional[int]): Size of digit groups used by the
	        folding hash function.

	    operation (Optional[str]): Operation applied in the folding method
	        (e.g., "sum").

	"""

	type: str
	positions: Optional[List[int]] = None
	group_size: Optional[int] = None
	operation: Optional[str] = None


class CreateDynamicHashRequest(BaseModel):
	"""Request model used to create a dynamic hash structure.

	Attributes:
	    digits (int): Number of digits expected in the keys.
	    initial_num_buckets (int): Initial number of buckets in the structure.
	    bucket_size (int): Capacity of each bucket.
	    expansion_policy (str): Bucket expansion strategy. Supported values:
	        - "total": bucket count doubles.
	        - "partial": bucket count grows in intermediate steps.
	    expansion_threshold (float): Load factor threshold that triggers
	        expansion of the structure.
	    reduction_threshold (float): Load factor threshold that triggers
	        reduction of the structure.

	"""

	digits: int
	initial_num_buckets: int
	bucket_size: int
	expansion_policy: str = 'total'
	expansion_threshold: float = 0.75
	reduction_threshold: float = 0.5


def get_service():
	"""Return the current dynamic hash service instance.

	This function is used by the router factory to access the current
	instance of the search structure.

	Returns:
	    Optional[DynamicHashExternalSearch]: The active service instance
	    or None if the structure has not been created yet.

	"""
	return service


def build_hash_function(request: HashFunctionRequest):
	"""Build a hash function instance from the request configuration.

	Args:
	    request (HashFunctionRequest): Configuration parameters for
	        the desired hash function.

	Returns:
	    HashFunction: An initialized hash function instance.

	Raises:
	    HTTPException: If required parameters are missing or the hash
	    function type is invalid.

	"""
	if request.type == 'mod':
		return ModHash()

	if request.type == 'square':
		return SquareHash()

	if request.type == 'truncation':
		if not request.positions:
			raise HTTPException(status_code=400, detail='Se requieren posiciones')
		return TruncationHash(request.positions)

	if request.type == 'folding':
		if not request.group_size:
			raise HTTPException(status_code=400, detail='Se requiere group_size')
		return FoldingHash(request.group_size, request.operation or 'sum')

	raise HTTPException(status_code=400, detail='Tipo de hash no válido')


@router.post('/set-hash')
def set_hash_function(request: HashFunctionRequest):
	"""Configure the hash function used by the dynamic hash structure.

	This endpoint must be called before creating the structure.

	Args:
	    request (HashFunctionRequest): Configuration describing which
	    hash function to use.

	Returns:
	    dict: Confirmation message indicating the hash function
	    was successfully configured.

	"""
	global hash_func
	hash_func = build_hash_function(request)
	return {'message': 'Función hash configurada'}


@router.post('/create')
def create_structure(request: CreateDynamicHashRequest):
	"""Create and initialize the dynamic hash structure.

	This endpoint instantiates the service and initializes the
	internal bucket structure according to the provided parameters.

	Args:
	    request (CreateDynamicHashRequest): Parameters used to
	    initialize the dynamic hash structure.

	Returns:
	    dict: Confirmation message indicating the structure
	    was successfully created.

	Raises:
	    HTTPException: If the hash function has not been configured.

	"""
	global service

	if hash_func is None:
		raise HTTPException(status_code=400, detail='Defina primero la función hash')

	service = DynamicHashExternalSearch(
		hash_func=hash_func,
		initial_num_buckets=request.initial_num_buckets,
		bucket_size=request.bucket_size,
		expansion_policy=request.expansion_policy,
		expansion_threshold=request.expansion_threshold,
		reduction_threshold=request.reduction_threshold,
	)

	service.create(digits=request.digits)

	return {'message': 'Estructura creada'}


@router.get('/state')
def get_state():
	"""Return the internal state of the dynamic hash structure.

	This endpoint exposes the internal configuration and contents of
	the structure, which can be useful for debugging or visualization.

	Returns:
	    dict: A dictionary containing the current structure state,
	    including bucket configuration, stored values, and load factor.

	Raises:
	    HTTPException: If the structure has not been created.

	"""
	if service is None:
		raise HTTPException(status_code=400, detail='Estructura no creada')

	return {
		'digits': service.digits,
		'bucket_size': service.bucket_size,
		'num_buckets': service.current_num_buckets,
		'size': service.size,
		'blocks': service.blocks,
		'overflow': service.overflow,
		'count': service._count,
		'load_factor': service._count / service.size if service.size else 0,
	}


router.include_router(create_external_search_router(get_service, '', 'Dynamic Hash External'))
