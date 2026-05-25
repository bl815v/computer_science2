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

from app.controllers.search.snapshot import SnapshotRequest
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
	"""Create and initialize the multiple residue tree structure.

	This endpoint creates a new ``MultipleResidueTree`` instance
	using the provided residue chunk size ``m`` and initializes
	the internal storage structure.

	If the service instance already exists, the existing object
	is reused and only the structure configuration is updated.

	Args:
		request (MultipleResidueCreateRequest):
			Request containing:

			    - m:
			        Residue chunk size used by the structure.

			    - size:
			        Total structure size.

			    - digits:
			        Number of digits allowed for addresses.

	Returns:
		dict:
			Dictionary containing:

			    - message:
			        Confirmation message.

			    - m:
			        Residue chunk size currently configured.

			    - size:
			        Configured structure size.

			    - digits:
			        Configured number of digits.

	Raises:
		HTTPException:
			If an unexpected error occurs during initialization.

	"""
	global multiple_service
	try:
		if multiple_service is None or getattr(multiple_service, 'm', None) != request.m:
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
	"""Insert a letter into the multiple residue tree.

	The endpoint validates that the structure has been initialized
	and verifies that the provided value is a valid letter before
	performing the insertion.

	Args:
		request (TreeInsertRequest):
			Request containing the letter to insert.

	Returns:
		dict:
			Dictionary containing:

			    - message:
			        Human-readable insertion result.

			    - position:
			        Address generated for the inserted value.

	Raises:
		HTTPException:
			If the structure has not been initialized.

		HTTPException:
			If the insertion operation fails due to validation
			or internal structure constraints.

	"""
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
	"""Search for a letter inside the multiple residue tree.

	The endpoint validates the input letter and searches all
	positions associated with the value inside the structure.

	Args:
		letter (str):
			Letter to search inside the tree.

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
	"""Delete a letter from the multiple residue tree.

	The endpoint removes all positions associated with the
	specified letter from the structure.

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
			        if the letter was not found.

	"""
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
	"""Generate a visualization of the multiple residue tree.

	The generated image represents the current internal
	tree structure and node organization.

	Args:
		background_tasks (BackgroundTasks):
			FastAPI background task manager used for temporary
			file cleanup after the response is sent.

	Returns:
		FileResponse:
			Generated visualization image.

	Raises:
		HTTPException:
			If the structure is empty or uninitialized.

	"""
	global multiple_service
	if multiple_service is None or multiple_service.root is None:
		raise HTTPException(status_code=400, detail='Árbol vacío')
	return await send_image(background_tasks, multiple_service.plot)


@router.get('/search-plot/{letter}')
async def multiple_search_plot(letter: str, background_tasks: BackgroundTasks):
	"""Generate a highlighted visualization for a searched letter.

	The generated image highlights the traversal path and
	position associated with the specified letter.

	Args:
		letter (str):
			Letter to highlight in the visualization.

		background_tasks (BackgroundTasks):
			FastAPI background task manager used for temporary
			file cleanup after the response is sent.

	Returns:
		FileResponse:
			Generated highlighted visualization image.

	Raises:
		HTTPException:
			If the structure is empty.

		HTTPException:
			If the specified letter does not exist.

	"""
	global multiple_service
	if multiple_service is None or multiple_service.root is None:
		raise HTTPException(status_code=400, detail='Árbol vacío')
	letter = validate_letter(letter)
	positions = multiple_service.search(letter)
	if not positions:
		raise HTTPException(status_code=404, detail='Letra no encontrada')
	return await send_image(background_tasks, multiple_service.search_plot, letter)


@router.post('/export')
async def multiple_export():
	"""Export the current multiple residue tree snapshot.

	The exported snapshot contains the complete structure
	configuration and internal state required to restore
	the tree later.

	Returns:
		dict:
			Serialized snapshot representing the current
			multiple residue tree state.

	Raises:
		HTTPException:
			If the structure has not been initialized.

	"""
	global multiple_service
	if multiple_service is None:
		raise HTTPException(status_code=400, detail='Estructura no inicializada')
	return multiple_service.save_state()


@router.post('/import')
async def multiple_import(request: SnapshotRequest):
	"""Restore the multiple residue tree from a snapshot.

	This endpoint recreates the internal structure using
	the configuration stored inside the snapshot and then
	loads the serialized tree state.

	If the service instance does not exist, a new
	``MultipleResidueTree`` is created automatically
	using the snapshot configuration.

	Args:
		request (SnapshotRequest):
			Request containing the serialized snapshot data.

	Returns:
		dict:
			Serialized snapshot representing the restored state.

	Raises:
		HTTPException:
			If the snapshot does not contain a valid ``m`` value.

		HTTPException:
			If the snapshot data is invalid or incompatible.

	"""
	global multiple_service
	if multiple_service is None:
		config = request.snapshot.get('config', {})
		m = config.get('m')
		encoding = config.get('encoding', 'ABC')
		if not isinstance(m, int) or m <= 0:
			raise HTTPException(status_code=400, detail='Snapshot requires a valid m value')
		multiple_service = MultipleResidueTree(m=m, encoding=encoding)

	try:
		multiple_service.load_state(request.snapshot)
		return multiple_service.save_state()
	except ValueError as exc:
		raise HTTPException(status_code=400, detail=str(exc))
