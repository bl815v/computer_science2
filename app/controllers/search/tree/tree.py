"""
Register and aggregate tree search API routers.

Combine DigitalTree, SimpleResidueTree, and
MultipleResidueTree route groups into a single
APIRouter instance for centralized inclusion
in the main FastAPI application.

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

from fastapi import APIRouter

from app.controllers.search.tree.digital import router as digital_router
from app.controllers.search.tree.multiple import router as multiple_router
from app.controllers.search.tree.simple import router as simple_router

router = APIRouter()
router.include_router(digital_router)
router.include_router(simple_router)
router.include_router(multiple_router)
