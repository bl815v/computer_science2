"""
Router factory for external search services.

This module defines a reusable FastAPI router builder used to expose
external search structures through REST endpoints.

The router provides a standardized interface for external search
implementations based on block storage. Each router supports the
following operations:

    - Structure creation
    - State inspection
    - Value insertion
    - Value search
    - Value deletion

The module uses controller helper functions to separate HTTP
handling from the core service logic.

It also instantiates a concrete router for the linear external
search implementation.

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

from app.controllers.search.external.external_router_factory import (
	create_external_search_router,
)
from app.services.search.external.linear_external import LinearExternalSearch

service = LinearExternalSearch()

def get_service():
	"""Return the linear external search service instance."""
	return service

router = create_external_search_router(
	get_service,
	prefix='/external/linear',
	tag='External Linear Search',
)
