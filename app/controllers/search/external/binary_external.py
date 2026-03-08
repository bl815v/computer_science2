"""
FastAPI router for the external binary search structure.

This module exposes REST endpoints that allow clients to interact
with the block-based binary external search structure implemented
by `BinaryExternalSearch`.

The router provides operations to:

    - Create the external structure
    - Retrieve the current structure state
    - Insert new keys
    - Search for existing keys
    - Delete keys from the structure

The structure organizes keys in ordered blocks of approximately √n
elements. Binary search is applied both across blocks and inside the
selected block to efficiently locate values.

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
from app.services.search.external.binary_external import BinaryExternalSearch

service = BinaryExternalSearch()

router = create_external_search_router(
	service,
	prefix='/external/binary',
	tag='External Binary Search',
)
