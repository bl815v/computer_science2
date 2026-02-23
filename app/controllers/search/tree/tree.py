from fastapi import APIRouter

from app.controllers.search.tree.tree_controller import (
	digital_router,
	multiple_router,
	simple_router,
)

router = APIRouter()
router.include_router(digital_router)
router.include_router(simple_router)
router.include_router(multiple_router)
