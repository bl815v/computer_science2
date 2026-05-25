"""
Expose REST endpoints for SimpleResidueTree operations.

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
from app.services.search.tree.simple_residue_tree import SimpleResidueTree

from .common import (
	SimpleResidueCreateRequest,
	TreeInsertRequest,
	send_image,
	validate_letter,
)

simple_service = SimpleResidueTree(encoding='ABC')
router = APIRouter(prefix='/simple-residue', tags=['Simple Residue Tree'])


@router.post('/create')
async def simple_create(request: SimpleResidueCreateRequest):
	"""Create and initialize the simple residue tree structure.

	This endpoint initializes the internal simple residue tree
	using the provided configuration parameters.

	The structure becomes ready to store and search encoded
	letters after successful initialization.

	Args:
		request (SimpleResidueCreateRequest):
			Request containing:

			    - size:
			        Total structure size.

			    - digits:
			        Number of digits used for address generation.

	Returns:
		dict:
			Dictionary containing:

			    - message:
			        Confirmation message.

			    - size:
			        Configured structure size.

			    - digits:
			        Configured number of digits.

	Raises:
		HTTPException:
			If an unexpected error occurs during initialization.

	"""
	try:
		simple_service.create(size=request.size, digits=request.digits)
		return {
			'message': 'Estructura de residuos simple creada',
			'size': simple_service.size,
			'digits': simple_service.digits,
		}
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))


@router.post('/insert')
async def simple_insert(request: TreeInsertRequest):
	"""Insert a letter into the simple residue tree.

	The endpoint validates that the structure has been
	initialized and verifies that the provided letter
	is valid before performing the insertion.

	Args:
		request (TreeInsertRequest):
			Request containing the letter to insert.

	Returns:
		dict:
			Dictionary containing:

			    - message:
			        Human-readable insertion result.

			    - position:
			        Address generated for the inserted letter.

	Raises:
		HTTPException:
			If the structure has not been initialized.

		HTTPException:
			If the insertion fails due to validation
			or internal structure constraints.

	"""
	if not simple_service.initialized:
		raise HTTPException(status_code=400, detail='Estructura no inicializada')
	letter = validate_letter(request.letter)
	try:
		position = simple_service.insert(letter)
		return {
			'message': f"Letra '{letter}' insertada en la dirección {position}",
			'position': position,
		}
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))


@router.get('/search/{letter}')
async def simple_search(letter: str):
	"""Search for a letter inside the simple residue tree.

	The endpoint validates the provided letter and
	searches all matching positions associated with it.

	Args:
		letter (str):
			Letter to search inside the structure.

	Returns:
		dict:
			Dictionary containing:

			    - position:
			        List of matching positions or an empty list.

			    - value:
			        Searched letter.

			    - message:
			        Human-readable search result.

	"""
	if not simple_service.initialized:
		return {'position': [], 'value': letter, 'message': 'Estructura no inicializada'}
	letter = validate_letter(letter)
	positions = simple_service.search(letter)
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
async def simple_delete(letter: str):
	"""Delete a letter from the simple residue tree.

	The endpoint removes all occurrences associated
	with the specified letter from the structure.

	Args:
		letter (str):
			Letter to remove from the structure.

	Returns:
		dict:
			Dictionary containing:

			    - message:
			        Human-readable deletion result.

			    - position:
			        Deleted positions or an empty list
			        if the letter does not exist.

	"""
	if not simple_service.initialized:
		return {'message': 'Estructura no inicializada', 'position': []}
	letter = validate_letter(letter)
	positions = simple_service.delete(letter)
	if not positions:
		return {'message': f"Letra '{letter}' no encontrada", 'position': []}
	return {
		'message': f"Letra '{letter}' eliminada de la dirección {positions}",
		'position': positions,
	}


@router.get('/plot')
async def simple_plot(background_tasks: BackgroundTasks):
	"""Generate a visualization image of the simple residue tree.

	The generated image represents the current tree
	structure and node organization.

	Args:
		background_tasks (BackgroundTasks):
			FastAPI background task manager used for
			temporary file cleanup.

	Returns:
		FileResponse:
			Generated visualization image.

	Raises:
		HTTPException:
			If the structure is empty.

	"""
	if simple_service.root is None:
		raise HTTPException(status_code=400, detail='Árbol vacío')
	return await send_image(background_tasks, simple_service.plot)


@router.get('/search-plot/{letter}')
async def simple_search_plot(letter: str, background_tasks: BackgroundTasks):
	"""Generate a highlighted visualization for a searched letter.

	The generated image highlights the traversal path
	and matching position associated with the specified
	letter inside the tree.

	Args:
		letter (str):
			Letter to highlight in the visualization.

		background_tasks (BackgroundTasks):
			FastAPI background task manager used for
			temporary file cleanup.

	Returns:
		FileResponse:
			Generated highlighted visualization image.

	Raises:
		HTTPException:
			If the structure is empty.

		HTTPException:
			If the specified letter does not exist.

	"""
	if simple_service.root is None:
		raise HTTPException(status_code=400, detail='Árbol vacío')
	letter = validate_letter(letter)
	positions = simple_service.search(letter)
	if not positions:
		raise HTTPException(status_code=404, detail='Letra no encontrada')
	return await send_image(background_tasks, simple_service.search_plot, letter)


@router.post('/export')
async def simple_export():
	"""Export the current simple residue tree snapshot.

	The exported snapshot contains the complete internal
	state and configuration required to restore the tree
	later.

	Returns:
		dict:
			Serialized snapshot representing the current
			simple residue tree state.

	"""
	return simple_service.save_state()


@router.post('/import')
async def simple_import(request: SnapshotRequest):
	"""Restore the simple residue tree from a snapshot.

	This endpoint restores the internal configuration
	and stored values from a previously exported snapshot.

	Args:
		request (SnapshotRequest):
			Request containing the serialized snapshot data.

	Returns:
		dict:
			Serialized snapshot representing the restored state.

	Raises:
		HTTPException:
			If the snapshot data is invalid or incompatible.

	"""
	try:
		simple_service.load_state(request.snapshot)
		return simple_service.save_state()
	except ValueError as exc:
		raise HTTPException(status_code=400, detail=str(exc))
