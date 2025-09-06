"""This module initializes and configures the FastAPI application.

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

import sys
import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()


if getattr(sys, 'frozen', False):
    BASE_PATH = getattr(sys, '_MEIPASS', os.path.abspath("."))
else:
    BASE_PATH = os.path.abspath(".")
static_path = os.path.join(BASE_PATH, "static")

app.mount("/static", StaticFiles(directory=static_path), name="static")


@app.get("/")
def read_root() -> FileResponse:
    """Returns the main index.html file.

    This endpoint serves the initial HTML page of the application,
    located inside the `static` directory.

    Returns:
        FileResponse: The `index.html` file from the static folder.
    """
    return FileResponse(os.path.join(static_path, "index.html"))
