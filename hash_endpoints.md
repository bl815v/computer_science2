El orden correcto real debe ser:

1️⃣ Definir función hash

2️⃣ Crear estructura

3️⃣ Insertar

4️⃣ Si hay colisión → definir estrategia

5️⃣ Seguir insertando

---

# 🧪 PRUEBAS EN POSTMAN

---

# 🔹 1️⃣ Definir función hash

### POST

```
http://localhost:8000/hash/set-hash
```

### Body (JSON)

### ✔ MOD

```json
{
  "type": "mod"
}
```

### ✔ SQUARE

```json
{
  "type": "square"
}
```

### ✔ TRUNCATION

```json
{
  "type": "truncation",
  "positions": [1, 3]
}
```

### ✔ FOLDING

```json
{
  "type": "folding",
  "group_size": 2,
  "operation": "sum" (puede ser "mul")
}
```

---

# 🔹 2️⃣ Crear estructura

### POST

```
http://localhost:8000/hash/create
```

### Body

```json
{
  "size": 10,
  "digits": 4
}
```

✔ Respuesta esperada:

```json
{
  "message": "Estructura creada",
  "size": 10,
  "digits": 4
}
```

---

# 🔹 3️⃣ Insertar sin colisiones

### POST

```
http://localhost:8000/hash/insert
```

### Body

```json
{
  "value": "1234"
}
```

✔ Respuesta:

```json
{
  "message": "Clave 1234 insertada en la dirección 5",
  "position": [5]
}
```

---

# 🔹 4️⃣ Insertar y provocar colisión (sin estrategia)

Si insertas algo que choque:

```json
{
  "value": "1244"
}
```

💥 Respuesta:

```json
{
  "detail": "Colisión en la dirección 4 para la clave 1244. Define una solución de colisión."
}
```


---

# 🔹 5️⃣ Definir estrategia de colisión

---

## ✔ LINEAR

### POST

```
http://localhost:8000/hash/set-collision
```

```json
{
  "type": "linear"
}
```

---

## ✔ QUADRATIC

```json
{
  "type": "quadratic"
}
```

---

## ✔ DOUBLE HASH

```json
{
  "type": "double",
  "second_hash_type": "mod"
}
```

---

## ✔ CHAINING

```json
{
  "type": "chaining"
}
```

✔ Esto convierte la estructura sin perder datos.

---

# 🔹 6️⃣ Buscar

### GET

```
http://localhost:8000/hash/search/1234
```

Respuesta si existe:

```json
{
  "position": [5],
  "value": "1234",
  "message": "Clave encontrada en la dirección [5]"
}
```

Si no existe:

```json
{
  "position": [],
  "value": "9999",
  "message": "Clave no encontrada en la estructura"
}
```

---

# 🔹 7️⃣ Eliminar

### DELETE

```
http://localhost:8000/hash/delete/1234
```

Respuesta:

```json
{
  "message": "Clave 1234 eliminada de la dirección [5]",
  "position": [5]
}
```

---

# 🔹 8️⃣ Ver estado interno

### GET

```
http://localhost:8000/hash/state
```

Devuelve:

```json
{
  "size": 10,
  "digits": 4,
  "data": [...]
}
