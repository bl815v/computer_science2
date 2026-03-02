"""
Expose REST endpoints for DigitalTree operations.

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

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.services.search.tree.digital_tree import DigitalTree

from .common import (
	DigitalCreateRequest,
	TreeInsertRequest,
	send_image,
	validate_letter,
)

digital_service = DigitalTree(encoding='ABC')
router = APIRouter(prefix='/digital', tags=['Digital Tree'])


@router.post('/create')
async def digital_create(request: DigitalCreateRequest):
	"""
	Create and initialize digital tree structure.

	Return structure configuration after initialization.
	"""
	try:
		digital_service.create(size=request.size, digits=request.digits)
		return {
			'message': 'Estructura digital creada',
			'size': digital_service.size,
			'digits': digital_service.digits,
		}
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))


@router.post('/insert')
async def digital_insert(request: TreeInsertRequest):
	"""
	Insert a letter into digital tree.

	Validate structure state and input before insertion.
	Return insertion position.
	"""
	if not digital_service.initialized:
		raise HTTPException(status_code=400, detail='Estructura no inicializada')
	letter = validate_letter(request.letter)
	try:
		position = digital_service.insert(letter)
		return {
			'message': f"Letra '{letter}' insertada en la dirección {position}",
			'position': position,
		}
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))


@router.get('/search/{letter}')
async def digital_search(letter: str):
	"""
	Search for a letter in digital tree.

	Return its position if found, otherwise an empty result.
	"""
	if not digital_service.initialized:
		return {'position': [], 'value': letter, 'message': 'Estructura no inicializada'}
	letter = validate_letter(letter)
	positions = digital_service.search(letter)
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
async def digital_delete(letter: str):
	"""
	Remove a letter from digital tree.

	Return deleted positions if successful.
	"""
	if not digital_service.initialized:
		return {'message': 'Estructura no inicializada', 'position': []}
	letter = validate_letter(letter)
	positions = digital_service.delete(letter)
	if not positions:
		return {'message': f"Letra '{letter}' no encontrada", 'position': []}
	return {
		'message': f"Letra '{letter}' eliminada de la dirección {positions}",
		'position': positions,
	}


@router.get('/plot')
async def digital_plot(background_tasks: BackgroundTasks):
	"""Generate visualization image of digital tree."""
	if digital_service.root is None:
		raise HTTPException(status_code=400, detail='Árbol vacío')
	return await send_image(background_tasks, digital_service.plot)


@router.get('/search-plot/{letter}')
async def digital_search_plot(letter: str, background_tasks: BackgroundTasks):
	"""Generate visualization highlighting searched letter."""
	if digital_service.root is None:
		raise HTTPException(status_code=400, detail='Árbol vacío')
	letter = validate_letter(letter)
	positions = digital_service.search(letter)
	if not positions:
		raise HTTPException(status_code=404, detail='Letra no encontrada')
	return await send_image(background_tasks, digital_service.search_plot, letter)
