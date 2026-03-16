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


def create_external_search_router(get_service, prefix: str, tag: str) -> APIRouter:
	"""
	Create a FastAPI router for an external search structure.

	The router does not store the service instance directly. Instead it
	receives a function that returns the current service instance. This
	avoids capturing a None reference when the router is created.
	"""
	router = APIRouter(prefix=prefix, tags=[tag])

	def _service():
		service = get_service()
		if service is None:
			raise HTTPException(status_code=400, detail='Estructura no creada')
		return service

	@router.post('/create')
	def create_structure(request: CreateExternalRequest):
		"""Create and initialize the external search structure."""
		return handle_external_create(_service(), request)

	@router.get('/state')
	async def get_state():
		"""Retrieve the current internal state of the structure."""
		service = _service()

		return {
			'size': service.size,
			'digits': service.digits,
			'block_size': service.block_size,
			'blocks': service.blocks,
		}

	@router.post('/insert')
	def insert_value(request: InsertRequest):
		"""Insert a new key into the external structure."""
		return handle_external_insert(_service(), request)

	@router.get('/search/{value}')
	def search_value(value: str):
		"""Search for a key in the structure."""
		return handle_search(_service(), value)

	@router.delete('/delete/{value}')
	def delete_value(value: str):
		"""Delete a key from the structure."""
		return handle_delete(_service(), value)

	return router
