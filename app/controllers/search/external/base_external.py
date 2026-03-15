"""
Controller utilities for external search structures.

This module provides helper functions used by FastAPI controllers
to manage external search structures organized in blocks.

It defines request models and handler functions responsible for:

    - Creating an external search structure
    - Inserting new values into the structure

These helpers delegate the actual data operations to the corresponding
search service while handling input validation and response formatting.

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

from fastapi import HTTPException
from pydantic import BaseModel

from app.controllers.search.base_search import (
    InsertRequest,
    handle_delete,
    handle_search,
    normalize_value,
)


class CreateExternalRequest(BaseModel):
    """
    Request body model for external structure creation.

    Attributes:
        size (int):
            Maximum number of elements allowed in the structure.

        digits (int):
            Required number of digits for each stored key.

    """

    size: int
    digits: int


def handle_external_create(service, request: CreateExternalRequest) -> dict:
    """
    Handle the creation of an external search structure.

    This function initializes the structure using the provided
    size and digit constraints. The underlying service is responsible
    for organizing the storage into blocks.

    Args:
        service:
            External search service instance responsible for managing
            the data structure.

        request (CreateExternalRequest):
            Request object containing creation parameters.

    Returns:
        dict:
            Dictionary describing the created structure, including:

                - message: Confirmation message
                - size: Maximum structure capacity
                - digits: Required number of digits per key
                - block_size: Computed block size
                - blocks: Total number of blocks

    """
    service.create(request.size, request.digits)

    return {
        'message': 'Estructura externa creada',
        'size': request.size,
        'digits': request.digits,
        'block_size': service.block_size,
        'blocks': len(service.blocks),
    }


def handle_external_insert(service, request: InsertRequest) -> dict:
    """
    Handle insertion of a new key into an external search structure.

    The function validates that the structure has been initialized,
    normalizes the input value, inserts it into the structure,
    and returns its resulting position.

    Args:
        service:
            External search service instance responsible for managing
            the data structure.

        request (InsertRequest):
            Request object containing the value to insert.

    Returns:
        dict:
            Dictionary describing the insertion result, including:

                - message: Confirmation message
                - position: Location of the inserted key in the structure

    Raises:
        HTTPException:
            If the structure has not been initialized or if insertion fails.

    """
    if not service.initialized:
        raise HTTPException(
            status_code=400,
            detail='Estructura no inicializada',
        )

    value = normalize_value(request.value, service.digits)

    try:
        service.insert(value)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    position = service.search(value)

    return {
        'message': f'Clave {value} insertada',
        'position': position,
    }
