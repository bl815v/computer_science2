# app/controllers/search/tree_controller.py

import os
import tempfile
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.services.search.tree.digital_tree import DigitalTree
from app.services.search.tree.multiple_residue_tree import MultipleResidueTree
from app.services.search.tree.simple_residue_tree import SimpleResidueTree

# ----------------------------------------------------------------------
# Modelos de solicitud
# ----------------------------------------------------------------------


class DigitalCreateRequest(BaseModel):
	size: Optional[int] = Field(None, description='Tamaño máximo opcional')
	digits: Optional[int] = Field(None, description='Número de bits por letra')


class SimpleResidueCreateRequest(BaseModel):
	size: Optional[int] = Field(None, description='Tamaño máximo opcional')
	digits: Optional[int] = Field(None, description='Número de bits por letra')


class MultipleResidueCreateRequest(BaseModel):
	size: Optional[int] = Field(None, description='Tamaño máximo opcional')
	digits: Optional[int] = Field(None, description='Número de bits por letra')
	m: int = Field(2, description='Tamaño de fragmento en bits (solo para árbol múltiple)')


class TreeInsertRequest(BaseModel):
	letter: str = Field(..., description='Una sola letra del alfabeto español (incluye Ñ)')


# ----------------------------------------------------------------------
# Utilidades
# ----------------------------------------------------------------------


def validate_spanish_letter(letter: str) -> str:
	"""Valida que la entrada sea una letra mayúscula del alfabeto español."""
	if len(letter) != 1:
		raise HTTPException(status_code=400, detail='Debe ingresar una sola letra')
	alfabeto = 'ABCDEFGHIJKLMNÑOPQRSTUVWXYZ'
	letter = letter.upper()
	if letter not in alfabeto:
		raise HTTPException(
			status_code=400,
			detail=f"Letra '{letter}' no válida. Use solo letras del alfabeto español (incluye Ñ).",
		)
	return letter


async def send_image(background_tasks: BackgroundTasks, plot_func, *args, **kwargs):
	"""
	Genera una imagen usando la función plot (que guarda en archivo) y la devuelve como FileResponse.
	El archivo temporal se elimina después de enviarse.
	"""
	fd, path = tempfile.mkstemp(suffix='.png')
	os.close(fd)
	try:
		plot_func(*args, filename=path, **kwargs)
		background_tasks.add_task(os.unlink, path)
		return FileResponse(path, media_type='image/png')
	except Exception as e:
		# Si hay error, limpiamos el archivo inmediatamente
		os.unlink(path)
		raise HTTPException(status_code=500, detail=str(e))


# ----------------------------------------------------------------------
# Router para DigitalTree
# ----------------------------------------------------------------------

digital_service = DigitalTree(encoding='ABC')
digital_router = APIRouter(prefix='/digital', tags=['Digital Tree'])


@digital_router.post('/create')
async def digital_create(request: DigitalCreateRequest):
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
	if not digital_service.initialized:
		raise HTTPException(status_code=400, detail='Estructura no inicializada')
	letter = validate_spanish_letter(request.letter)
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
	if not digital_service.initialized:
		return {'position': [], 'value': letter, 'message': 'Estructura no inicializada'}
	letter = validate_spanish_letter(letter)
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
	if not digital_service.initialized:
		return {'message': 'Estructura no inicializada', 'position': []}
	letter = validate_spanish_letter(letter)
	positions = digital_service.delete(letter)
	if not positions:
		return {'message': f"Letra '{letter}' no encontrada", 'position': []}
	return {
		'message': f"Letra '{letter}' eliminada de la dirección {positions}",
		'position': positions,
	}


@digital_router.get('/plot')
async def digital_plot(background_tasks: BackgroundTasks):
	if digital_service.root is None:
		raise HTTPException(status_code=400, detail='Árbol vacío')
	return await send_image(background_tasks, digital_service.plot)


@digital_router.get('/search-plot/{letter}')
async def digital_search_plot(letter: str, background_tasks: BackgroundTasks):
	if digital_service.root is None:
		raise HTTPException(status_code=400, detail='Árbol vacío')
	letter = validate_spanish_letter(letter)
	# Verificar que la letra exista
	positions = digital_service.search(letter)
	if not positions:
		raise HTTPException(status_code=404, detail='Letra no encontrada')
	return await send_image(background_tasks, digital_service.search_plot, letter)


# ----------------------------------------------------------------------
# Router para SimpleResidueTree
# ----------------------------------------------------------------------

simple_service = SimpleResidueTree(encoding='ABC')
simple_router = APIRouter(prefix='/simple-residue', tags=['Simple Residue Tree'])


@simple_router.post('/create')
async def simple_create(request: SimpleResidueCreateRequest):
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
	if not simple_service.initialized:
		raise HTTPException(status_code=400, detail='Estructura no inicializada')
	letter = validate_spanish_letter(request.letter)
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
	if not simple_service.initialized:
		return {'position': [], 'value': letter, 'message': 'Estructura no inicializada'}
	letter = validate_spanish_letter(letter)
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
	if not simple_service.initialized:
		return {'message': 'Estructura no inicializada', 'position': []}
	letter = validate_spanish_letter(letter)
	positions = simple_service.delete(letter)
	if not positions:
		return {'message': f"Letra '{letter}' no encontrada", 'position': []}
	return {
		'message': f"Letra '{letter}' eliminada de la dirección {positions}",
		'position': positions,
	}


@simple_router.get('/plot')
async def simple_plot(background_tasks: BackgroundTasks):
	if simple_service.root is None:
		raise HTTPException(status_code=400, detail='Árbol vacío')
	return await send_image(background_tasks, simple_service.plot)


@simple_router.get('/search-plot/{letter}')
async def simple_search_plot(letter: str, background_tasks: BackgroundTasks):
	if simple_service.root is None:
		raise HTTPException(status_code=400, detail='Árbol vacío')
	letter = validate_spanish_letter(letter)
	positions = simple_service.search(letter)
	if not positions:
		raise HTTPException(status_code=404, detail='Letra no encontrada')
	return await send_image(background_tasks, simple_service.search_plot, letter)


# ----------------------------------------------------------------------
# Router para MultipleResidueTree (con m configurable en primera creación)
# ----------------------------------------------------------------------

# Variable para almacenar la instancia (inicialmente None)
multiple_service: Optional[MultipleResidueTree] = None

multiple_router = APIRouter(prefix='/multiple-residue', tags=['Multiple Residue Tree'])


@multiple_router.post('/create')
async def multiple_create(request: MultipleResidueCreateRequest):
	global multiple_service
	try:
		if multiple_service is None:
			# Primera creación: instanciamos con el m proporcionado
			multiple_service = MultipleResidueTree(m=request.m, encoding='ABC')
		# Llamamos a create (reinicia la estructura, pero mantiene m)
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
	global multiple_service
	if multiple_service is None or not multiple_service.initialized:
		raise HTTPException(status_code=400, detail='Estructura no inicializada')
	letter = validate_spanish_letter(request.letter)
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
	global multiple_service
	if multiple_service is None or not multiple_service.initialized:
		return {'position': [], 'value': letter, 'message': 'Estructura no inicializada'}
	letter = validate_spanish_letter(letter)
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
	global multiple_service
	if multiple_service is None or not multiple_service.initialized:
		return {'message': 'Estructura no inicializada', 'position': []}
	letter = validate_spanish_letter(letter)
	positions = multiple_service.delete(letter)
	if not positions:
		return {'message': f"Letra '{letter}' no encontrada", 'position': []}
	return {
		'message': f"Letra '{letter}' eliminada de la dirección {positions}",
		'position': positions,
	}


@multiple_router.get('/plot')
async def multiple_plot(background_tasks: BackgroundTasks):
	global multiple_service
	if multiple_service is None or multiple_service.root is None:
		raise HTTPException(status_code=400, detail='Árbol vacío')
	return await send_image(background_tasks, multiple_service.plot)


@multiple_router.get('/search-plot/{letter}')
async def multiple_search_plot(letter: str, background_tasks: BackgroundTasks):
	global multiple_service
	if multiple_service is None or multiple_service.root is None:
		raise HTTPException(status_code=400, detail='Árbol vacío')
	letter = validate_spanish_letter(letter)
	positions = multiple_service.search(letter)
	if not positions:
		raise HTTPException(status_code=404, detail='Letra no encontrada')
	return await send_image(background_tasks, multiple_service.search_plot, letter)
