"""Define the FastAPI router for linear search operations.

It provides endpoints to create, manage, and query a linear search data structure,
including operations to insert values, search for values, and delete values
from the structure.

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

from app.controllers.search.base_search import create_search_router
from app.services.search.linear_search import LinearSearchService

service = LinearSearchService()

router = create_search_router(
    service=service,
    prefix="/linear-search",
    tag="Linear Search",
)
