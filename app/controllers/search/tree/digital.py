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

from app.controllers.search.snapshot import SnapshotRequest
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
	Create and initialize the digital tree structure.

	This endpoint allocates the internal storage required
	for the digital search tree and configures the number
	of digits used for key encoding.

	The structure must be initialized before insert,
	search, delete, or visualization operations can be used.

	Args:
		request (DigitalCreateRequest):
			Request containing the tree size and digit
			configuration.

	Returns:
		dict:
			Dictionary containing:

			- Confirmation message.
			- Configured structure size.
			- Digit configuration.

	Raises:
		HTTPException:
			If the structure cannot be created due to
			internal initialization errors.

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
	Insert a letter into the digital tree.

	This endpoint validates the input character,
	checks whether the structure has been initialized,
	and inserts the letter into the corresponding
	position in the digital search tree.

	Args:
		request (TreeInsertRequest):
			Request containing the letter to insert.

	Returns:
		dict:
			Dictionary containing:

			- Confirmation message.
			- Position where the letter was inserted.

	Raises:
		HTTPException:
			If the structure is not initialized,
			the input is invalid,
			or the insertion operation fails.

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
	Search for a letter in the digital tree.

	This endpoint locates the specified character
	within the digital search tree and returns
	its associated storage positions.

	If the letter does not exist, an empty result
	is returned.

	Args:
		letter (str):
			Character to search for.

	Returns:
		dict:
			Dictionary containing:

			- Search result message.
			- Searched value.
			- List of matching positions.

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
	Delete a letter from the digital tree.

	This endpoint removes the specified character
	from the digital search tree and returns the
	positions affected by the deletion.

	If the character is not present, an empty
	result is returned.

	Args:
		letter (str):
			Character to remove.

	Returns:
		dict:
			Dictionary containing:

			- Confirmation or error message.
			- List of deleted positions.

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
	"""
	Generate a visualization of the digital tree.

	This endpoint creates an image representation
	of the current digital search tree structure.

	The generated image is returned as a temporary
	file response and automatically cleaned up
	after delivery.

	Args:
		background_tasks (BackgroundTasks):
			FastAPI background task manager used
			to schedule temporary file cleanup.

	Returns:
		FileResponse:
			Image containing the rendered digital tree.

	Raises:
		HTTPException:
			If the tree is empty or has not been initialized.

	"""
	if digital_service.root is None:
		raise HTTPException(status_code=400, detail='Árbol vacío')
	return await send_image(background_tasks, digital_service.plot)


@router.get('/search-plot/{letter}')
async def digital_search_plot(letter: str, background_tasks: BackgroundTasks):
	"""
	Generate a visualization highlighting a searched letter.

	This endpoint creates an image representation
	of the digital search tree and highlights the
	node associated with the searched character.

	Args:
		letter (str):
			Character to highlight in the visualization.

		background_tasks (BackgroundTasks):
			FastAPI background task manager used
			to schedule temporary file cleanup.

	Returns:
		FileResponse:
			Image containing the highlighted tree visualization.

	Raises:
		HTTPException:
			If the tree is empty,
			the character is invalid,
			or the letter does not exist in the structure.

	"""
	if digital_service.root is None:
		raise HTTPException(status_code=400, detail='Árbol vacío')
	letter = validate_letter(letter)
	positions = digital_service.search(letter)
	if not positions:
		raise HTTPException(status_code=404, detail='Letra no encontrada')
	return await send_image(background_tasks, digital_service.search_plot, letter)


@router.post('/export')
async def digital_export():
	"""
	Export the current digital tree snapshot.

	This endpoint serializes the current state
	of the digital tree into a snapshot that can
	later be restored using the import endpoint.

	The exported snapshot includes configuration,
	structure state, and stored data.

	Returns:
		dict:
			Serialized snapshot representing the
			current digital tree state.

	"""
	return digital_service.save_state()


@router.post('/import')
async def digital_import(request: SnapshotRequest):
	"""
	Restore the digital tree from a snapshot.

	This endpoint reconstructs the digital tree
	using a previously exported snapshot and
	restores its internal state and configuration.

	Args:
		request (SnapshotRequest):
			Request containing the serialized snapshot.

	Returns:
		dict:
			Serialized representation of the restored
			digital tree state.

	Raises:
		HTTPException:
			If the snapshot is invalid or incompatible
			with the digital tree structure.

	"""
	try:
		digital_service.load_state(request.snapshot)
		return digital_service.save_state()
	except ValueError as exc:
		raise HTTPException(status_code=400, detail=str(exc))
