# Endpoints de `HashExternalSearch`

## 1️⃣ Configurar función hash

### POST `/hash-external/set-hash`

Configura la función hash que usará la estructura.

### Body

```json
{
  "type": "base_conversion",
  "base": 7
}
```

### Otros tipos posibles

```json
{ "type": "mod" }
```

```json
{ 
  "type": "truncation",
  "positions": [1,3,5]
}
```

```json
{
  "type": "folding",
  "group_size": 2,
  "operation": "sum"
}
```

### Respuesta

```json
{
  "message": "Función hash configurada"
}
```

---

# 2️⃣ Crear la estructura

### POST `/hash-external/create`

Inicializa la estructura externa.

### Body

```json
{
  "size": 20,
  "digits": 4
}
```

### Respuesta

```json
{
  "message": "Estructura creada",
  "size": 20,
  "digits": 4,
  "block_size": 4
}
```

*(block_size depende de la implementación de `BaseExternalSearch`)*

---

# 3️⃣ Ver estado de la estructura

### GET `/hash-external/state`

Permite inspeccionar el estado interno.

### Respuesta

```json
{
  "size": 20,
  "digits": 4,
  "block_size": 4,
  "blocks": [
    [null, "1234", null, null],
    ["5678", null, null, null],
    [null, null, null, null]
  ],
  "overflow": [
    [],
    ["5678","9999"],
    []
  ],
  "block_offsets": [0,4,8]
}
```

---

# 4️⃣ Insertar clave

### POST `/hash-external/insert`

### Body

```json
{
  "value": "1234"
}
```

### Respuesta

```json
{
  "message": "Insertado",
  "position": 5
}
```

Si colisiona:

```json
{
  "message": "Insertado",
  "position": 21
}
```

(ya que los overflow se guardan después de los bloques).

---

# 5️⃣ Buscar clave

### GET `/hash-external/search/{value}`

Ejemplo

```
GET /hash-external/search/1234
```

### Respuesta

```json
[
  {
    "global_position": 5,
    "block_index": 2,
    "block_position": 1
  }
]
```

Si no existe:

```json
[]
```

---

# 6️⃣ Eliminar clave

### DELETE `/hash-external/delete/{value}`

Ejemplo

```
DELETE /hash-external/delete/1234
```

### Respuesta

```json
{
  "deleted_positions": [5]
}
```

Si no existe:

```json
{
  "deleted_positions": []
}
```

---
