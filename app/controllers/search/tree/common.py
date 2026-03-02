"""
Define request schemas and utility helpers for tree API operations.

Provide Pydantic models used to validate incoming requests
for DigitalTree, SimpleResidueTree, and MultipleResidueTree
creation and insertion. Include input validation utilities
and image generation helpers for tree visualization endpoints.

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

from fastapi import BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field


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
		return FileResponse(
			path,
			media_type='image/png',
			headers={
				'Cache-Control': 'no-cache, no-store, must-revalidate',
				'Pragma': 'no-cache',
				'Expires': '0',
			},
		)
	except Exception as e:
		os.unlink(path)
		raise HTTPException(status_code=500, detail=str(e))
