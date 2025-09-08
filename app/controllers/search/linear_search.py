from fastapi import APIRouter, HTTPException
from app.services.search.linear_search import LinearSearchService as LinearSearch
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter(prefix="/linear-search", tags=["Linear Search"])

# Usamos una instancia global para mantener el estado
service = LinearSearch()

# Modelo para la solicitud de creación
class CreateRequest(BaseModel):
    size: int
    digits: int

# Modelo para la solicitud de inserción
class InsertRequest(BaseModel):
    value: str

@router.post("/create")
async def create_structure(request: CreateRequest):
    try:
        service.create(request.size, request.digits)
        return {
            "message": "Structure created", 
            "size": request.size, 
            "digits": request.digits
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/state")
async def get_state():
    try:
        return {
            "size": service.size,
            "digits": service.digits,
            "data": service.data
        }
    except:
        return {"size": 0, "digits": 0, "data": []}

@router.post("/insert")
async def insert_value(request: InsertRequest):
    try:
        # Validaciones adicionales
        if not service.initialized:
            raise HTTPException(status_code=400, detail="Structure not initialized")
            
        if len(request.value) != service.digits:
            raise HTTPException(
                status_code=400, 
                detail=f"Value must have exactly {service.digits} digits"
            )
            
        if not request.value.isdigit():
            raise HTTPException(status_code=400, detail="Value must be numeric")
            
        position = service.insert(request.value)
        return {
            "message": f"Value {request.value} inserted at position {position}", 
            "position": position
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search/{value}")
async def search_value(value: str):
    try:
        if not service.initialized:
            return {"positions": [], "value": value}
            
        result = service.search(value)
        return {"positions": result, "value": value}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete/{value}")
async def delete_value(value: str):
    try:
        if not service.initialized:
            return {"message": "Structure not initialized", "deleted_positions": []}
            
        result = service.delete(value)
        if not result:
            return {"message": f"Value {value} not found", "deleted_positions": []}
        return {
            "message": f"Value {value} deleted", 
            "deleted_positions": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
