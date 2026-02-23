## 1. Digital Tree (`/digital`)

### a) Crear estructura
- **Método:** `POST`
- **URL:** `http://localhost:8000/digital/create`
- **Body (JSON):** 
  ```json
  {
    "size": 1000,
    "digits": 5
  }
  ```
  *Ambos campos son opcionales; si no se envían, se usan valores por defecto (size=1000, digits=5 para codificación ABC).*

### b) Insertar letra
- **Método:** `POST`
- **URL:** `http://localhost:8000/digital/insert`
- **Body (JSON):** 
  ```json
  {
    "letter": "P"
  }
  ```
  *La letra debe ser una única del alfabeto español (A-Z incluyendo Ñ).*

### c) Buscar letra
- **Método:** `GET`
- **URL:** `http://localhost:8000/digital/search/P`
- **Body:** No aplica.

### d) Eliminar letra
- **Método:** `DELETE`
- **URL:** `http://localhost:8000/digital/delete/P`
- **Body:** No aplica.

### e) Ver imagen del árbol actual
- **Método:** `GET`
- **URL:** `http://localhost:8000/digital/plot`
- **Respuesta:** Archivo PNG.

### f) Búsqueda con imagen resaltada
- **Método:** `GET`
- **URL:** `http://localhost:8000/digital/search-plot/P`
- **Respuesta:** Archivo PNG con el nodo de la letra `P` resaltado (si existe).

---

## 2. Simple Residue Tree (`/simple-residue`)

### a) Crear estructura
- **Método:** `POST`
- **URL:** `http://localhost:8000/simple-residue/create`
- **Body (JSON):** 
  ```json
  {
    "size": 1000,
    "digits": 5
  }
  ```

### b) Insertar letra
- **Método:** `POST`
- **URL:** `http://localhost:8000/simple-residue/insert`
- **Body (JSON):** 
  ```json
  {
    "letter": "R"
  }
  ```

### c) Buscar letra
- **Método:** `GET`
- **URL:** `http://localhost:8000/simple-residue/search/R`

### d) Eliminar letra
- **Método:** `DELETE`
- **URL:** `http://localhost:8000/simple-residue/delete/R`

### e) Ver imagen del árbol
- **Método:** `GET`
- **URL:** `http://localhost:8000/simple-residue/plot`

### f) Búsqueda con imagen resaltada
- **Método:** `GET`
- **URL:** `http://localhost:8000/simple-residue/search-plot/R`

---

## 3. Multiple Residue Tree (`/multiple-residue`)

### a) Crear estructura (primera vez)
- **Método:** `POST`
- **URL:** `http://localhost:8000/multiple-residue/create`
- **Body (JSON):** 
  ```json
  {
    "m": 2,
    "size": 1000,
    "digits": 5
  }
  ```
  *El campo `m` es obligatorio en la primera creación; en llamadas posteriores se puede omitir (se usará el mismo `m` ya configurado).*

### b) Insertar letra
- **Método:** `POST`
- **URL:** `http://localhost:8000/multiple-residue/insert`
- **Body (JSON):** 
  ```json
  {
    "letter": "U"
  }
  ```

### c) Buscar letra
- **Método:** `GET`
- **URL:** `http://localhost:8000/multiple-residue/search/U`

### d) Eliminar letra
- **Método:** `DELETE`
- **URL:** `http://localhost:8000/multiple-residue/delete/U`

### e) Ver imagen del árbol
- **Método:** `GET`
- **URL:** `http://localhost:8000/multiple-residue/plot`

### f) Búsqueda con imagen resaltada
- **Método:** `GET`
- **URL:** `http://localhost:8000/multiple-residue/search-plot/U`

---
