"""
Expose REST endpoints for MultipleResidueTree operations.

Provide API routes to create, insert, search, delete,
and visualize a digital search tree structure.
Handle input validation, state verification,
error management, and dynamic image generation.

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

from typing import Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.services.search.tree.multiple_residue_tree import MultipleResidueTree

from .common import (
	MultipleResidueCreateRequest,
	TreeInsertRequest,
	send_image,
	validate_letter,
)

multiple_service: Optional[MultipleResidueTree] = None
router = APIRouter(prefix='/multiple-residue', tags=['Multiple Residue Tree'])


@router.post('/create')
async def multiple_create(request: MultipleResidueCreateRequest):
	"""
	Create and initialize multiple residue tree structure.

	Instantiate tree with provided chunk size m if needed.
	"""
	global multiple_service
	try:
		if multiple_service is None:
			multiple_service = MultipleResidueTree(m=request.m, encoding='ABC')
		multiple_service.create(size=request.size, digits=request.digits)
		return {
			'message': 'Estructura de residuos múltiple creada',
			'm': multiple_service.m,
			'size': multiple_service.size,
			'digits': multiple_service.digits,
		}
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))


@router.post('/insert')
async def multiple_insert(request: TreeInsertRequest):
	"""Insert a letter into multiple residue tree."""
	global multiple_service
	if multiple_service is None or not multiple_service.initialized:
		raise HTTPException(status_code=400, detail='Estructura no inicializada')
	letter = validate_letter(request.letter)
	try:
		position = multiple_service.insert(letter)
		return {
			'message': f"Letra '{letter}' insertada en la dirección {position}",
			'position': position,
		}
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))


@router.get('/search/{letter}')
async def multiple_search(letter: str):
	"""Search for a letter in multiple residue tree."""
	global multiple_service
	if multiple_service is None or not multiple_service.initialized:
		return {'position': [], 'value': letter, 'message': 'Estructura no inicializada'}
	letter = validate_letter(letter)
	positions = multiple_service.search(letter)
	if positions:
		return {
			'position': positions,
			'value': letter,
			'message': f'Letra encontrada en la dirección {positions}',
		}
	return {
		'position': [],
		'value': letter,
		'message': 'Letra no encontrada en la estructura',
	}


@router.delete('/delete/{letter}')
async def multiple_delete(letter: str):
	"""Remove a letter from multiple residue tree."""
	global multiple_service
	if multiple_service is None or not multiple_service.initialized:
		return {'message': 'Estructura no inicializada', 'position': []}
	letter = validate_letter(letter)
	positions = multiple_service.delete(letter)
	if not positions:
		return {'message': f"Letra '{letter}' no encontrada", 'position': []}
	return {
		'message': f"Letra '{letter}' eliminada de la dirección {positions}",
		'position': positions,
	}


@router.get('/plot')
async def multiple_plot(background_tasks: BackgroundTasks):
	"""Generate visualization image of multiple residue tree."""
	global multiple_service
	if multiple_service is None or multiple_service.root is None:
		raise HTTPException(status_code=400, detail='Árbol vacío')
	return await send_image(background_tasks, multiple_service.plot)


@router.get('/search-plot/{letter}')
async def multiple_search_plot(letter: str, background_tasks: BackgroundTasks):
	"""Generate visualization highlighting searched letter in multiple residue tree."""
	global multiple_service
	if multiple_service is None or multiple_service.root is None:
		raise HTTPException(status_code=400, detail='Árbol vacío')
	letter = validate_letter(letter)
	positions = multiple_service.search(letter)
	if not positions:
		raise HTTPException(status_code=404, detail='Letra no encontrada')
	return await send_image(background_tasks, multiple_service.search_plot, letter)
