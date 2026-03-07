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

  // --- Verificación local de duplicados ---
  function valueAlreadyExists(val) {
    for (let i = 0; i < currentState.data.length; i++) {
      const cell = currentState.data[i];
      // Ignorar celdas vacías o marcadores de eliminado
      if (cell === null || cell === undefined || cell === "DELETED") continue;
      if (Array.isArray(cell)) {
        if (cell.includes(val)) return true;
      } else {
        if (cell === val) return true;
      }
    }
    return false;
  }

  // --- Función para resaltar celdas ---
  function highlightCells(positions, className, duration = 1500) {
    if (!positions || !Array.isArray(positions) || positions.length === 0) return;
    const grid = document.getElementById("visualization");
    if (!grid) return;
    positions.forEach(pos => {
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
    const match = message.match(/\d+/);
    return match ? [parseInt(match[0], 10)] : null;
  }

  // --- Renderizado dinámico con puntos suspensivos ---
  function renderGrid() {
    const grid = document.getElementById("visualization");
    if (!grid) return;
    grid.innerHTML = "";

    const data = currentState.data;
    const totalSize = data.length;
    const OCCUPIED_THRESHOLD = 1;

    const occupied = [];
    for (let i = 0; i < totalSize; i++) {
      const val = data[i];
      const isOccupied = (
        (typeof val === 'string' && val !== "DELETED" && val !== "") ||
        (Array.isArray(val) && val.length > 0)
      );
      if (isOccupied) occupied.push(i);
    }

    const appendCell = (index) => {
      const val = data[index];
      const cell = document.createElement("div");
      cell.className = "cell";
      cell.dataset.index = `Dir: ${index+1}`;
      cell.dataset.pos = index + 1;

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
    };

    if (occupied.length === 0) {
      const end = Math.min(5, totalSize) - 1;
      for (let i = 0; i <= end; i++) {
        appendCell(i);
      }
      return;
    }

    const firstOcc = occupied[0];
    const lastOcc = occupied[occupied.length - 1];

    const start = Math.max(0, firstOcc - 2);
    for (let i = start; i < firstOcc; i++) {
      appendCell(i);
    }

    for (let idx = 0; idx < occupied.length; idx++) {
      const i = occupied[idx];
      appendCell(i);

      if (idx < occupied.length - 1) {
        const next = occupied[idx + 1];
        if (next - i > OCCUPIED_THRESHOLD) {
          const dots = document.createElement("div");
          dots.className = "cell dots";
          dots.textContent = "...";
          grid.appendChild(dots);
        } else if (next - i > 1) {
          for (let j = i + 1; j < next; j++) {
            appendCell(j);
          }
        }
      }
    }

    const end = Math.min(totalSize - 1, lastOcc + 2);
    for (let i = lastOcc + 1; i <= end; i++) {
      appendCell(i);
    }
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

    // Elementos de truncamiento
    const hashTypeSelect = document.getElementById("hash-type");
    const truncationOptions = document.getElementById("truncation-options");
    const truncationMethod = document.getElementById("truncation-method");
    const truncationValue = document.getElementById("truncation-value");

    // Elementos de plegamiento
    const foldingOptions = document.getElementById("folding-options");
    const foldingOperation = document.getElementById("folding-operation");
    const foldingGroupSize = document.getElementById("folding-group-size");

    // Verificar que todos los elementos existan
    if (!hashTypeSelect || !truncationOptions || !truncationMethod || !truncationValue || 
        !foldingOptions || !foldingOperation || !foldingGroupSize) {
      console.error("Faltan elementos del DOM para los submenús.");
      return;
    }

    // Mostrar/ocultar opciones según el tipo seleccionado
    hashTypeSelect.addEventListener("change", () => {
      if (hashTypeSelect.value === "truncation") {
        truncationOptions.style.display = "block";
        foldingOptions.style.display = "none";
      } else if (hashTypeSelect.value === "folding") {
        truncationOptions.style.display = "none";
        foldingOptions.style.display = "block";
      } else {
        truncationOptions.style.display = "none";
        foldingOptions.style.display = "none";
      }
    });

    // Cambiar el placeholder según el método de truncamiento
    truncationMethod.addEventListener("change", () => {
      if (truncationMethod.value === "positions") {
        truncationValue.placeholder = "Ej: 1,3,5";
      } else {
        truncationValue.placeholder = "Ej: 2";
      }
    });

    if (valInp) {
      valInp.addEventListener("input", () => {
        const d = currentDigits || parseInt(document.getElementById("digits").value) || 0;
        enforceNumericDigits(valInp, d);
      });
    }

    // --- Inicializar ---
    createBtn.addEventListener("click", async () => {
      const hType = hashTypeSelect.value;
      const size = parseInt(document.getElementById("size").value);
      const digits = parseInt(document.getElementById("digits").value);

      if (isNaN(size) || size <= 0) return notifyError("Tamaño inválido.");
      if (isNaN(digits) || digits <= 0) return notifyError("Dígitos inválidos.");

      let setHashBody = { type: hType };

      // Truncamiento
      if (hType === "truncation") {
        const method = truncationMethod.value;
        const value = truncationValue.value.trim();
        if (!value) return notifyError("Especifica los parámetros de truncamiento.");

        let positions = [];
        if (method === "first") {
          const n = parseInt(value, 10);
          if (isNaN(n) || n <= 0 || n > digits) {
            return notifyError(`Ingresa un número válido de dígitos entre 1 y ${digits}.`);
          }
          for (let i = 1; i <= n; i++) positions.push(i);
        } else if (method === "last") {
          const n = parseInt(value, 10);
          if (isNaN(n) || n <= 0 || n > digits) {
            return notifyError(`Ingresa un número válido de dígitos entre 1 y ${digits}.`);
          }
          for (let i = digits - n + 1; i <= digits; i++) positions.push(i);
        } else if (method === "positions") {
          const parts = value.split(',').map(p => parseInt(p.trim(), 10));
          const invalid = parts.some(p => isNaN(p) || p <= 0 || p > digits);
          if (parts.length === 0 || invalid) {
            return notifyError(`Ingresa posiciones válidas entre 1 y ${digits} separadas por comas.`);
          }
          positions = parts;
        }
        setHashBody.positions = positions;
      }

      // Plegamiento
      if (hType === "folding") {
        const operation = foldingOperation.value;
        const groupSize = parseInt(foldingGroupSize.value, 10);
        if (isNaN(groupSize) || groupSize <= 0) {
          return notifyError("El tamaño del grupo debe ser un número positivo.");
        }
        setHashBody.operation = operation;
        setHashBody.group_size = groupSize;
      }

      try {
        currentDigits = digits;
        valInp.placeholder = `Ej: ${"1".padStart(digits, "0")}`;
        
        await fetch(`${API_BASE}/set-hash`, {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify(setHashBody)
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

        await loadState();
        
        collisionMenu.style.display = "none";
        document.getElementById("actions-section").style.display = "block";
        notifySuccess(`Estructura lista para ${digits} dígitos.`);
        clearInput();
      } catch (err) { notifyError(err.message); }
    });

    // --- Insertar (con verificación local de duplicados) ---
    insertBtn.addEventListener("click", async () => {
      const rawValue = valInp.value.trim();
      if (!rawValue) { notifyError("Ingresa una clave."); clearInput(); return; }
      const value = toDigits(rawValue, currentDigits);
      if (!validateKey(value)) return;

      // Verificar si el valor ya existe localmente
      if (valueAlreadyExists(value)) {
        notifyError(`La clave ${value} ya existe en la tabla.`);
        clearInput();
        return;
      }

      lastValueAttempt = rawValue;

      try {
        const res = await fetch(`${API_BASE}/insert`, {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({ value })
        });

        const data = await res.json();

        if (res.ok) {
          let positionsToHighlight = [];
          if (data.position && Array.isArray(data.position)) {
            positionsToHighlight = data.position;
          } else if (data.position && typeof data.position === 'number') {
            positionsToHighlight = [data.position];
          }

          if (positionsToHighlight.length > 0) {
            for (const pos of positionsToHighlight) {
              const index = pos - 1;
              if (index >= 0 && index < currentState.data.length) {
                const cell = currentState.data[index];
                if (Array.isArray(cell)) {
                  if (!cell.includes(value)) {
                    currentState.data[index] = [...cell, value];
                  }
                } else {
                  currentState.data[index] = value;
                }
              }
            }
            renderGrid();
            notifySuccess(`Clave ${value} insertada en Dir: ${positionsToHighlight.join(", ")}`);
            highlightCells(positionsToHighlight, 'highlight-insert');
          } else {
            await loadState();
            notifySuccess(`Clave ${value} insertada.`);
          }
          
          collisionMenu.style.display = "none";
          clearInput();
        } else {
          if (data.detail && data.detail.includes("Colisión")) {
            notifyError(data.detail);
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

    // --- Borrar ---
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
          const hasPosition = data.position && Array.isArray(data.position) && data.position.length > 0;
          
          if (hasPosition) {
            const dirs = data.position.join(", ");
            notifySuccess(`Clave ${value} eliminada de Dir: ${dirs}`);
            highlightCells(data.position, 'highlight-delete');

            for (const pos of data.position) {
              const index = pos - 1;
              if (index >= 0 && index < currentState.data.length) {
                const cell = currentState.data[index];
                if (Array.isArray(cell)) {
                  currentState.data[index] = cell.filter(item => String(item) !== value);
                } else {
                  currentState.data[index] = "DELETED";
                }
              }
            }
            renderGrid();
          } else {
            const errorMsg = data.message || data.detail || `La clave ${value} no existe.`;
            notifyError(errorMsg);
          }
        } else {
          notifyError(data.detail || `Error al eliminar (${res.status})`);
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