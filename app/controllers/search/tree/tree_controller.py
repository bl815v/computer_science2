"""
Expose REST endpoints for digital and residue tree structures.

Provide API routes to create, insert, search, delete, and visualize
DigitalTree, SimpleResidueTree, and MultipleResidueTree structures.
Handle input validation, error management, and dynamic image
generation for tree visualization.

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

import os
import tempfile
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.services.search.tree.digital_tree import DigitalTree
from app.services.search.tree.multiple_residue_tree import MultipleResidueTree
from app.services.search.tree.simple_residue_tree import SimpleResidueTree


class DigitalCreateRequest(BaseModel):
	"""
	Represent request payload for digital tree creation.

	Attributes:
		size: Optional maximum storage size.
		digits: Optional number of bits per letter.

	"""

	size: Optional[int] = Field(None, description='Tamaño máximo opcional')
	digits: Optional[int] = Field(None, description='Número de bits por letra')


class SimpleResidueCreateRequest(BaseModel):
	"""
	Represent request payload for simple residue tree creation.

	Attributes:
		size: Optional maximum storage size.
		digits: Optional number of bits per letter.

	"""

	size: Optional[int] = Field(None, description='Tamaño máximo opcional')
	digits: Optional[int] = Field(None, description='Número de bits por letra')


class MultipleResidueCreateRequest(BaseModel):
	"""
	Represent request payload for multiple residue tree creation.

	Attributes:
		size: Optional maximum storage size.
		digits: Optional number of bits per letter.
		m: Chunk size in bits used to partition binary representation.

	"""

	size: Optional[int] = Field(None, description='Tamaño máximo opcional')
	digits: Optional[int] = Field(None, description='Número de bits por letra')
	m: int = Field(2, description='Tamaño de fragmento en bits (solo para árbol múltiple)')


class TreeInsertRequest(BaseModel):
	"""
	Represent request payload for inserting a letter.

	Attributes:
	    letter: Single alphabet letter to insert.

	"""

	letter: str = Field(..., description='Una sola letra del alfabeto americano')


def validate_letter(letter: str) -> str:
	"""
	Validate and normalize a single-letter input.

	Ensure that the input contains exactly one uppercase
	letter from the American alphabet.

	Args:
		letter: Letter to validate.

	Returns:
		str: Uppercase validated letter.

	Raises:
		HTTPException: If input is invalid.

	"""
	if len(letter) != 1:
		raise HTTPException(status_code=400, detail='Debe ingresar una sola letra')
	alfabeto = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
	letter = letter.upper()
	if letter not in alfabeto:
		raise HTTPException(
			status_code=400,
			detail=f"Letra '{letter}' no válida. Use solo letras del alfabeto americano.",
		)
	return letter


async def send_image(background_tasks: BackgroundTasks, plot_func, *args, **kwargs):
	"""
	Generate a temporary tree visualization image.

	Execute the provided plotting function, return the
	generated PNG file, and schedule automatic cleanup.

	Args:
		background_tasks: FastAPI background task manager.
		plot_func: Plotting function to execute.
		*args: Positional arguments for plotting function.
		**kwargs: Keyword arguments for plotting function.

	Returns:
		FileResponse: PNG image response.

	Raises:
		HTTPException: If image generation fails.

	"""
	fd, path = tempfile.mkstemp(suffix='.png')
	os.close(fd)
	try:
		plot_func(*args, filename=path, **kwargs)
		background_tasks.add_task(os.unlink, path)
		return FileResponse(path, media_type='image/png')
	except Exception as e:
		os.unlink(path)
		raise HTTPException(status_code=500, detail=str(e))


digital_service = DigitalTree(encoding='ABC')
digital_router = APIRouter(prefix='/digital', tags=['Digital Tree'])


@digital_router.post('/create')
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


@digital_router.post('/insert')
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


@digital_router.get('/search/{letter}')
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


@digital_router.delete('/delete/{letter}')
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


@digital_router.get('/plot')
async def digital_plot(background_tasks: BackgroundTasks):
	"""Generate visualization image of digital tree."""
	if digital_service.root is None:
		raise HTTPException(status_code=400, detail='Árbol vacío')
	return await send_image(background_tasks, digital_service.plot)


@digital_router.get('/search-plot/{letter}')
async def digital_search_plot(letter: str, background_tasks: BackgroundTasks):
	"""Generate visualization highlighting searched letter."""
	if digital_service.root is None:
		raise HTTPException(status_code=400, detail='Árbol vacío')
	letter = validate_letter(letter)
	positions = digital_service.search(letter)
	if not positions:
		raise HTTPException(status_code=404, detail='Letra no encontrada')
	return await send_image(background_tasks, digital_service.search_plot, letter)


simple_service = SimpleResidueTree(encoding='ABC')
simple_router = APIRouter(prefix='/simple-residue', tags=['Simple Residue Tree'])


@simple_router.post('/create')
async def simple_create(request: SimpleResidueCreateRequest):
	"""Create and initialize simple residue tree structure."""
	try:
		simple_service.create(size=request.size, digits=request.digits)
		return {
			'message': 'Estructura de residuos simple creada',
			'size': simple_service.size,
			'digits': simple_service.digits,
		}
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))


@simple_router.post('/insert')
async def simple_insert(request: TreeInsertRequest):
	"""Insert a letter into simple residue tree."""
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


@simple_router.get('/search/{letter}')
async def simple_search(letter: str):
	"""Search for a letter in simple residue tree."""
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


@simple_router.delete('/delete/{letter}')
async def simple_delete(letter: str):
	"""Remove a letter from simple residue tree."""
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


@simple_router.get('/plot')
async def simple_plot(background_tasks: BackgroundTasks):
	"""Generate visualization image of simple residue tree."""
	if simple_service.root is None:
		raise HTTPException(status_code=400, detail='Árbol vacío')
	return await send_image(background_tasks, simple_service.plot)


@simple_router.get('/search-plot/{letter}')
async def simple_search_plot(letter: str, background_tasks: BackgroundTasks):
	"""Generate visualization highlighting searched letter in simple residue tree."""
	if simple_service.root is None:
		raise HTTPException(status_code=400, detail='Árbol vacío')
	letter = validate_letter(letter)
	positions = simple_service.search(letter)
	if not positions:
		raise HTTPException(status_code=404, detail='Letra no encontrada')
	return await send_image(background_tasks, simple_service.search_plot, letter)


multiple_service: Optional[MultipleResidueTree] = None

multiple_router = APIRouter(prefix='/multiple-residue', tags=['Multiple Residue Tree'])


@multiple_router.post('/create')
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


@multiple_router.post('/insert')
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


@multiple_router.get('/search/{letter}')
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


@multiple_router.delete('/delete/{letter}')
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


@multiple_router.get('/plot')
async def multiple_plot(background_tasks: BackgroundTasks):
	"""Generate visualization image of multiple residue tree."""
	global multiple_service
	if multiple_service is None or multiple_service.root is None:
		raise HTTPException(status_code=400, detail='Árbol vacío')
	return await send_image(background_tasks, multiple_service.plot)


@multiple_router.get('/search-plot/{letter}')
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
