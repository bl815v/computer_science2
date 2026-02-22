"""Registers all routers for the application.

It integrates:
- Linear search endpoints
- Binary search endpoints
- Hash table endpoints

These routers are later included in the main FastAPI application
to expose search functionalities via HTTP endpoints.

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

from app.controllers.search.binary_search import router as binary_search_router
from app.controllers.search.hash.router import router as hash_router
from app.controllers.search.linear_search import router as linear_search_router
