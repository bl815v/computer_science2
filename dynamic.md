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

