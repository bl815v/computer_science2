/* eslint-disable no-console */
(() => {
  "use strict";
  const API_BASE = "http://127.0.0.1:8000/hash";
  let lastValueAttempt = ""; 
  let currentDigits = 0;
  let isNotifying = false;
  let currentState = { size: 0, digits: 0, data: [] }; // Estado local

  // --- Utilidades ---
  function clearInput() {
    const inp = document.getElementById("value-input");
    if (inp) {
      inp.value = "";
      inp.focus();
    }
  }

  function toDigits(v, digits) {
    if (v === null || v === undefined || v === "") return "";
    // Si el valor es numérico o string numérico, rellenar con ceros
    if (!isNaN(v) && v !== "DELETED") {
        return String(v).padStart(digits, "0");
    }
    return v;
  }

  function enforceNumericDigits(input, digits) {
    const originalValue = input.value;
    const numericValue = originalValue.replace(/\D+/g, "");
    
    if (digits > 0 && numericValue.length > digits) {
      input.value = numericValue.slice(0, digits);
      if (!isNotifying) {
        isNotifying = true;
        notifyError(`La clave solo puede tener ${digits} dígitos.`);
        setTimeout(() => { isNotifying = false; }, 1500);
      }
    } else {
      input.value = numericValue;
    }
  }

  function validateKey(val) {
    if (!val) {
      notifyError("Ingresa una clave.");
      clearInput();
      return false;
    }
    if (val.length !== currentDigits) {
      notifyError(`La clave debe tener exactamente ${currentDigits} dígitos.`);
      clearInput();
      return false;
    }
    return true;
  }

  // --- Función para resaltar celdas ---
  function highlightCells(positions, className, duration = 1500) {
    if (!positions || !Array.isArray(positions) || positions.length === 0) return;
    const grid = document.getElementById("visualization");
    if (!grid) return;
    positions.forEach(pos => {
      // Buscar celda por el atributo data-pos (número de dirección 1-based)
      const cell = grid.querySelector(`[data-pos="${pos}"]`);
      if (cell) {
        cell.classList.add(className);
        setTimeout(() => {
          cell.classList.remove(className);
        }, duration);
      }
    });
  }

  // --- Función para extraer número de dirección de un mensaje de colisión ---
  function extractPositionFromMessage(message) {
    // Busca un número en el mensaje, ej: "Colisión detectada en la dirección 5"
    const match = message.match(/\d+/);
    return match ? [parseInt(match[0], 10)] : null;
  }

  // --- Renderizado (usa currentState) ---
  function renderGrid() {
    const grid = document.getElementById("visualization");
    if (!grid) return;
    grid.innerHTML = "";
    
    currentState.data.forEach((val, i) => {
      const cell = document.createElement("div");
      cell.className = "cell";
      cell.dataset.index = `Dir: ${i+1}`;
      cell.dataset.pos = i + 1; // Para búsqueda por posición

      if (Array.isArray(val)) {
        cell.innerHTML = val.length > 0 
          ? val.map(v => `<span class="hash-item">${toDigits(v, currentDigits)}</span>`).join("") 
          : "";
      } else {
        cell.textContent = (val === null || val === undefined) 
          ? "" 
          : (val === "DELETED" ? "🗑️" : toDigits(val, currentDigits));
      }
      
      if (!cell.textContent && (!Array.isArray(val) || val.length === 0)) {
        cell.classList.add("empty");
      }
      grid.appendChild(cell);
    });
  }

  // --- Cargar estado desde el backend ---
  async function loadState() {
    try {
      const res = await fetch(`${API_BASE}/state`);
      if (!res.ok) throw new Error("Error al cargar estado");
      currentState = await res.json();
      renderGrid();
    } catch (err) {
      console.error(err);
      notifyError("No se pudo cargar el estado.");
    }
  }

  async function initHashing() {
    const createBtn = document.getElementById("create-structure");
    const insertBtn = document.getElementById("insert-btn");
    const searchBtn = document.getElementById("search-btn");
    const deleteBtn = document.getElementById("delete-btn");
    const collisionMenu = document.getElementById("collision-menu");
    const applyCollisionBtn = document.getElementById("apply-collision");
    const valInp = document.getElementById("value-input");

    if (valInp) {
      valInp.addEventListener("input", () => {
        const d = currentDigits || parseInt(document.getElementById("digits").value) || 0;
        enforceNumericDigits(valInp, d);
      });
    }

    // --- Inicializar ---
    createBtn.addEventListener("click", async () => {
      const hType = document.getElementById("hash-type").value;
      const size = parseInt(document.getElementById("size").value);
      const digits = parseInt(document.getElementById("digits").value);

      if (isNaN(size) || size <= 0) return notifyError("Tamaño inválido.");
      if (isNaN(digits) || digits <= 0) return notifyError("Dígitos inválidos.");

      try {
        currentDigits = digits;
        valInp.placeholder = `Ej: ${"1".padStart(digits, "0")}`;
        
        await fetch(`${API_BASE}/set-hash`, {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({ type: hType, positions: [1, 2], group_size: 2 })
        });

        const res = await fetch(`${API_BASE}/create`, {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({ size, digits })
        });

        if (!res.ok) {
           const errData = await res.json();
           throw new Error(errData.detail || "Error al crear");
        }

        await loadState(); // Carga el estado inicial
        
        collisionMenu.style.display = "none";
        document.getElementById("actions-section").style.display = "block";
        notifySuccess(`Estructura lista para ${digits} dígitos.`);
        clearInput();
      } catch (err) { notifyError(err.message); }
    });

    // --- Insertar (ACTUALIZACIÓN LOCAL) ---
    insertBtn.addEventListener("click", async () => {
      const rawValue = valInp.value.trim();
      if (!rawValue) { notifyError("Ingresa una clave."); clearInput(); return; }
      const value = toDigits(rawValue, currentDigits);
      if (!validateKey(value)) return;
      lastValueAttempt = rawValue;

      try {
        const res = await fetch(`${API_BASE}/insert`, {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({ value })
        });

        const data = await res.json();

        if (res.ok) {
          // Insert exitoso
          let positionsToHighlight = [];
          if (data.position && Array.isArray(data.position)) {
            positionsToHighlight = data.position;
          } else if (data.position && typeof data.position === 'number') {
            positionsToHighlight = [data.position];
          }

          // Actualizar estado local
          if (positionsToHighlight.length > 0) {
            for (const pos of positionsToHighlight) {
              const index = pos - 1;
              if (index >= 0 && index < currentState.data.length) {
                const cell = currentState.data[index];
                if (Array.isArray(cell)) {
                  // Encadenamiento: agregar el valor a la lista
                  if (!cell.includes(value)) {
                    currentState.data[index] = [...cell, value];
                  }
                } else {
                  // Celda simple: reemplazar con el valor (incluso si estaba DELETED)
                  currentState.data[index] = value;
                }
              }
            }
            renderGrid();
            notifySuccess(`Clave ${value} insertada en Dir: ${positionsToHighlight.join(", ")}`);
            highlightCells(positionsToHighlight, 'highlight-insert');
          } else {
            // Si no hay posición, recargamos
            await loadState();
            notifySuccess(`Clave ${value} insertada.`);
          }
          
          collisionMenu.style.display = "none";
          clearInput();
        } else {
          // Error, posible colisión
          if (data.detail && data.detail.includes("Colisión")) {
            notifyError(data.detail);
            // Intentar resaltar la celda donde ocurrió la colisión
            const collisionPos = extractPositionFromMessage(data.detail);
            if (collisionPos) {
              highlightCells(collisionPos, 'highlight-collision', 2000);
            }
            collisionMenu.style.display = "flex";
          } else {
            notifyError(data.detail || "Error al insertar");
            collisionMenu.style.display = "none";
          }
          clearInput();
        }
      } catch (e) { 
        console.error(e);
        notifyError("Error de conexión al insertar."); 
        clearInput(); 
      }
    });

    // --- Aplicar Colisión ---
    applyCollisionBtn.addEventListener("click", async () => {
      const cType = document.getElementById("collision-type").value;
      const endpoint = cType === 'chaining' ? `${API_BASE}/set-chaining` : `${API_BASE}/set-collision`;
      
      try {
        const res = await fetch(endpoint, {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({ type: cType, second_hash_type: "mod" })
        });

        if (res.ok) {
          collisionMenu.style.display = "none";
          notifySuccess(`Estrategia aplicada. Reintentando...`);
          valInp.value = lastValueAttempt;
          insertBtn.click();
        } else {
           const data = await res.json();
           notifyError(data.detail || "No se pudo aplicar la estrategia.");
        }
      } catch (e) { notifyError("Error al aplicar estrategia."); clearInput(); }
    });

    // --- Buscar ---
    searchBtn.addEventListener("click", async () => {
      const rawValue = valInp.value.trim();
      if (!rawValue) { notifyError("Ingresa una clave."); clearInput(); return; }
      const value = toDigits(rawValue, currentDigits);
      if (!validateKey(value)) return;

      try {
        const res = await fetch(`${API_BASE}/search/${encodeURIComponent(value)}`);
        const data = await res.json();
        
        if (res.ok) {
          if (data.position && Array.isArray(data.position) && data.position.length > 0) {
            const dirs = data.position.join(", ");
            notifySuccess(`Clave ${value} encontrada en Dir(s): ${dirs}`);
            highlightCells(data.position, 'highlight-search');
          } else {
            notifyError(`La clave ${value} no existe.`);
          }
        } else {
          notifyError(data.detail || "Error en la búsqueda.");
        }
      } catch (e) { 
        console.error("Error en búsqueda:", e);
        notifyError("Error de conexión al buscar."); 
      }
      clearInput();
    });

    // --- Borrar (ACTUALIZACIÓN LOCAL CON MARCADOR "DELETED") ---
    deleteBtn.addEventListener("click", async () => {
      const rawValue = valInp.value.trim();
      if (!rawValue) { notifyError("Ingresa una clave."); clearInput(); return; }
      const value = toDigits(rawValue, currentDigits);
      if (!validateKey(value)) return;

      try {
        console.log(`Enviando eliminación para clave: "${value}" (raw: "${rawValue}")`);
        const url = `${API_BASE}/delete/${encodeURIComponent(value)}`;
        console.log(`URL: ${url}`);
        
        const res = await fetch(url, { method: "DELETE" });
        const data = await res.json();
        console.log("Respuesta completa:", data);

        if (res.ok) {
          // Mostrar mensaje de éxito con la posición si existe
          if (data.position && Array.isArray(data.position) && data.position.length > 0) {
            const dirs = data.position.join(", ");
            notifySuccess(`Clave ${value} eliminada de Dir: ${dirs}`);
            highlightCells(data.position, 'highlight-delete');
          } else {
            notifySuccess(`Clave ${value} eliminada.`);
          }

          // Actualizar el estado local usando la información de la respuesta
          if (data.position && Array.isArray(data.position)) {
            for (const pos of data.position) {
              const index = pos - 1; // Convertir a 0-based
              if (index >= 0 && index < currentState.data.length) {
                const cell = currentState.data[index];
                if (Array.isArray(cell)) {
                  // Es una celda de encadenamiento: filtrar el valor eliminado
                  currentState.data[index] = cell.filter(item => String(item) !== value);
                } else {
                  // Es una celda simple: marcar como "DELETED"
                  currentState.data[index] = "DELETED";
                }
              }
            }
            // Refrescar la vista con el estado local actualizado
            renderGrid();
          } else {
            // Si no hay información de posición, recargamos del backend como fallback
            console.warn("No se recibió posición, recargando estado...");
            await loadState();
          }
        } else {
          // Si el servidor responde con error (ej. 404 no encontrada)
          notifyError(data.detail || "Error al eliminar.");
        }
      } catch (e) { 
        console.error("Error Delete:", e);
        notifyError("Error de conexión al eliminar."); 
      }
      clearInput();
    });
  }

  window.initSimulator = initHashing;
})();