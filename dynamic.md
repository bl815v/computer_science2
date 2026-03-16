Buena idea reducirlo 👍.
Como ya tienes **`external_router_factory`**, podemos reutilizar casi todo y solo agregar lo que es **específico del hash dinámico**:

* configurar función hash
* crear estructura con parámetros extra
* `state` extendido

El resto (`insert`, `search`, `delete`) lo dejamos al **factory**, manteniendo **DRY** y **Open/Closed**.

---

# Archivo reducido

`dynamic_hash_external_router.py`

```python
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.controllers.search.external.external_router_factory import (
    create_external_search_router,
)
from app.services.search.external.dynamic_hash_external import DynamicHashExternalSearch
from app.services.search.hash.hash_function import (
    FoldingHash,
    ModHash,
    SquareHash,
    TruncationHash,
)

router = APIRouter(prefix="/dynamic-hash-external", tags=["Dynamic Hash External"])

service: Optional[DynamicHashExternalSearch] = None
hash_func = None


class HashFunctionRequest(BaseModel):
    type: str
    positions: Optional[List[int]] = None
    group_size: Optional[int] = None
    operation: Optional[str] = None


class CreateDynamicHashRequest(BaseModel):
    digits: int
    initial_num_buckets: int
    bucket_size: int
    expansion_policy: str = "total"
    expansion_threshold: float = 0.75
    reduction_threshold: float = 0.5


def build_hash_function(request: HashFunctionRequest):
    if request.type == "mod":
        return ModHash()

    if request.type == "square":
        return SquareHash()

    if request.type == "truncation":
        if not request.positions:
            raise HTTPException(status_code=400, detail="Se requieren posiciones")
        return TruncationHash(request.positions)

    if request.type == "folding":
        if not request.group_size:
            raise HTTPException(status_code=400, detail="Se requiere group_size")
        return FoldingHash(request.group_size, request.operation or "sum")

    raise HTTPException(status_code=400, detail="Tipo de hash no válido")


@router.post("/set-hash")
def set_hash_function(request: HashFunctionRequest):
    """Configure the hash function."""
    global hash_func
    hash_func = build_hash_function(request)
    return {"message": "Función hash configurada"}


@router.post("/create")
def create_structure(request: CreateDynamicHashRequest):
    """Create dynamic hash structure."""
    global service

    if hash_func is None:
        raise HTTPException(status_code=400, detail="Defina primero la función hash")

    service = DynamicHashExternalSearch(
        hash_func=hash_func,
        initial_num_buckets=request.initial_num_buckets,
        bucket_size=request.bucket_size,
        expansion_policy=request.expansion_policy,
        expansion_threshold=request.expansion_threshold,
        reduction_threshold=request.reduction_threshold,
    )

    service.create(digits=request.digits)

    return {"message": "Estructura creada"}


@router.get("/state")
def get_state():
    """Return internal state."""
    if service is None:
        raise HTTPException(status_code=400, detail="Estructura no creada")

    return {
        "digits": service.digits,
        "bucket_size": service.bucket_size,
        "num_buckets": service.current_num_buckets,
        "size": service.size,
        "blocks": service.blocks,
        "overflow": service.overflow,
        "count": service._count,
        "load_factor": service._count / service.size if service.size else 0,
    }


# reutilizamos endpoints estándar
router.include_router(
    create_external_search_router(service, "", "Dynamic Hash External")
)
```

---

# Endpoints disponibles

Prefijo:

```
/dynamic-hash-external
```

---

# 1️⃣ Configurar hash

```
POST /dynamic-hash-external/set-hash
```

body:

```json
{
  "type": "mod"
}
```

otros:

```json
{
  "type": "square"
}
```

```json
{
  "type": "truncation",
  "positions": [1,3]
}
```

```json
{
  "type": "folding",
  "group_size": 2,
  "operation": "sum"
}
```

---

# 2️⃣ Crear estructura

```
POST /dynamic-hash-external/create
```

body:

```json
{
  "digits": 2,
  "initial_num_buckets": 4,
  "bucket_size": 3,
  "expansion_policy": "partial",
  "expansion_threshold": 0.75,
  "reduction_threshold": 0.5
}
```

---

# 3️⃣ Ver estado

```
GET /dynamic-hash-external/state
```

ejemplo respuesta

```json
{
  "digits": 2,
  "bucket_size": 3,
  "num_buckets": 4,
  "size": 12,
  "blocks": [
    ["21", null, null],
    ["45", "32", null],
    [null, null, null],
    ["78", null, null]
  ],
  "overflow": [
    [],
    ["91"],
    [],
    []
  ],
  "count": 5,
  "load_factor": 0.41
}
```

---

# 4️⃣ Insertar

```
POST /dynamic-hash-external/insert
```

```json
{
  "value": "21"
}
```

respuesta

```json
{
  "message": "Clave 21 insertada",
  "position": 1
}
```

Si ocurre expansión automática:

```json
{
  "message": "Clave 33 insertada",
  "position": 14
}
```

y `num_buckets` cambiará en `/state`.

---

# 5️⃣ Buscar

```
GET /dynamic-hash-external/search/21
```

respuesta

```json
[
  {
    "global_position": 1,
    "block_index": 1,
    "block_position": 1
  }
]
```

---

# 6️⃣ Eliminar

```
DELETE /dynamic-hash-external/delete/21
```

respuesta

```json
{
  "deleted_positions": [1]
}
```

Si baja el **load factor**, puede ocurrir **reducción automática de buckets**.

---

# Flujo típico de uso

```text
1. POST /set-hash
2. POST /create
3. POST /insert
4. GET  /search/{value}
5. DELETE /delete/{value}
6. GET  /state
```

---

💡 Si quieres, también puedo mostrarte **una mejora muy fuerte en tu arquitectura**:
cómo hacer que **TODAS tus estructuras (hash normal, hash externo, hash dinámico, búsquedas externas)** se creen automáticamente con **un único router factory genérico**, reduciendo todo el proyecto probablemente **400-500 líneas de código repetido**.
Eso sería una arquitectura que impresiona bastante cuando revisan el proyecto.
