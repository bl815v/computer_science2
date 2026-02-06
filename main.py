"""Iinitialize and configures the FastAPI application.

It mounts a static files directory to serve HTML, CSS, and JavaScript
resources and defines the root endpoint that returns the main
`index.html` file of the project.

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
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.controllers import linear_search_router

app = FastAPI(
	title='ComputerScience2',
	description='Simulator of different data structures.',
	version='0.0.1',
)
app.add_middleware(
	CORSMiddleware,
	allow_origins=['http://localhost:8000', 'http://127.0.0.1:8000'],
	allow_credentials=True,
	allow_methods=['*'],
	allow_headers=['*'],
)
app.include_router(linear_search_router)

if getattr(sys, 'frozen', False):
	BASE_PATH = getattr(sys, '_MEIPASS', os.path.abspath('.'))
else:
	BASE_PATH = os.path.abspath('.')
static_path = os.path.join(BASE_PATH, 'static')

app.mount('/static', StaticFiles(directory=static_path), name='static')


@app.get('/')
def read_root() -> FileResponse:
	"""Return the main index.html file.

	This endpoint serves the initial HTML page of the application,
	located inside the `static` directory.

	Returns:
	    FileResponse: The `index.html` file from the static folder.

	"""
	return FileResponse(os.path.join(static_path, 'index.html'))
