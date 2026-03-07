/* eslint-disable no-console */
(() => {
  "use strict";

  const API_BASE = "http://127.0.0.1:8000/linear-search";
  let isNotifying = false;
  let currentState = { size: 0, digits: 0, data: [] }; // Estado local

  function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  function toDigits(v, digits) {
    if (v === null || v === undefined || v === "") return "";
    return String(v).padStart(digits, "0");
  }

  function resetInput(input) {
    input.value = "";
    input.focus();
  }

  async function fetchState() {
    try {
      const res = await fetch(`${API_BASE}/state`);
      if (!res.ok) return { size: 0, digits: 0, data: [] };
      return await res.json();
    } catch (error) {
      console.warn("No se pudo obtener el estado:", error);
      return { size: 0, digits: 0, data: [] };
    }
  }

  // --- Renderizado dinámico con puntos suspensivos ---
  function renderGrid() {
    const grid = document.getElementById("visualization");
    if (!grid) return;
    grid.innerHTML = "";

    const data = currentState.data;
    const totalSize = data.length;
    const OCCUPIED_THRESHOLD = 1; // Si hay más de 2 vacíos entre ocupados, ponemos "..."

    // Encontrar índices ocupados (que tienen un valor real, no vacío ni DELETED)
    const occupied = [];
    for (let i = 0; i < totalSize; i++) {
      const val = data[i];
      const isOccupied = (typeof val === 'string' && val !== "" && val !== null && val !== undefined);
      if (isOccupied) occupied.push(i);
    }

    // Función auxiliar para crear una celda en un índice dado
    const appendCell = (index) => {
      const val = data[index];
      const cell = document.createElement("div");
      cell.className = "cell";
      if (val == null || val === "") cell.classList.add("empty");
      cell.dataset.index = String(index + 1);
      cell.dataset.pos = index + 1; // Para búsquedas y animaciones
      cell.textContent = (val == null || val === "") ? "" : toDigits(val, currentState.digits);
      grid.appendChild(cell);
    };

    // Si no hay ocupados, mostrar un pequeño conjunto de celdas vacías (primeras 5)
    if (occupied.length === 0) {
      const end = Math.min(1, totalSize) - 1;
      for (let i = 0; i <= end; i++) {
        appendCell(i);
      }
      return;
    }

    const firstOcc = occupied[0];
    const lastOcc = occupied[occupied.length - 1];

    // Contexto inicial: desde max(0, firstOcc-2) hasta firstOcc-1
    const start = Math.max(0, firstOcc - 2);
    for (let i = start; i < firstOcc; i++) {
      appendCell(i);
    }

    // Mostrar ocupados y los espacios entre ellos
    for (let idx = 0; idx < occupied.length; idx++) {
      const i = occupied[idx];
      appendCell(i);

      if (idx < occupied.length - 1) {
        const next = occupied[idx + 1];
        if (next - i > OCCUPIED_THRESHOLD) {
          // Salto grande: poner "..."
          const dots = document.createElement("div");
          dots.className = "cell dots";
          dots.textContent = "...";
          grid.appendChild(dots);
        } else if (next - i > 1) {
          // Mostrar las celdas intermedias vacías (para mantener continuidad)
          for (let j = i + 1; j < next; j++) {
            appendCell(j);
          }
        }
      }
    }

    // Contexto final: desde lastOcc+1 hasta min(totalSize-1, lastOcc+2)
    const end = Math.min(totalSize - 1, lastOcc + 2);
    for (let i = lastOcc + 1; i <= end; i++) {
      appendCell(i);
    }
  }

  // --- ANIMACIÓN CON DETECCIÓN VISUAL Y PARADA TEMPRANA POR ORDEN ---
  async function scanAnimation(targetValue, state, stepMs = 450) {
    const grid = document.getElementById("visualization");
    if (!grid) return { found: false, position: -1 };

    // Seleccionar todas las celdas que no sean puntos suspensivos
    const cells = Array.from(grid.querySelectorAll(".cell:not(.dots)"));
    // Ordenar por data-pos (número real de la celda)
    cells.sort((a, b) => parseInt(a.dataset.pos) - parseInt(b.dataset.pos));

    let foundAny = false;
    let foundIndex = -1;
    const targetNum = Number(targetValue);

    // Limpiar clases previas
    cells.forEach(c => c.classList.remove("active", "found", "not-found", "visited"));

    for (let i = 0; i < cells.length; i++) {
      const cell = cells[i];
      cells.forEach(c => c.classList.remove("active"));
      cell.classList.add("active");

      const cellContent = cell.textContent.trim();
      const cellNum = cellContent ? Number(cellContent) : NaN;

      // Si la celda tiene un valor numérico y es mayor que el buscado, detener
      if (!isNaN(cellNum) && cellNum > targetNum) {
        break;
      }

      if (cellContent !== "" && cellContent === targetValue) {
        cell.classList.add("found");
        foundAny = true;
        foundIndex = parseInt(cell.dataset.pos); // posición real (1-based)
        break;
      } else {
        cell.classList.add("visited");
      }

      await sleep(stepMs);
    }

    if (!foundAny) {
      cells.forEach(c => {
        c.classList.remove("active");
        c.classList.add("not-found");
      });
      await sleep(1000);
      cells.forEach(c => c.classList.remove("not-found", "visited"));
    } else {
      cells.forEach(c => c.classList.remove("active"));
      await sleep(1000);
      cells.forEach(c => c.classList.remove("found", "visited"));
    }
    return { found: foundAny, position: foundIndex };
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

  async function initSecuencial() {
    const sizeEl = document.getElementById("size");
    const digitsEl = document.getElementById("digits");
    const createBtn = document.getElementById("create-structure");
    const actions = document.getElementById("actions-section");
    const valueEl = document.getElementById("value-input");
    const insertBtn = document.getElementById("insert-btn");
    const searchBtn = document.getElementById("search-btn");
    const deleteBtn = document.getElementById("delete-btn");

    if (!sizeEl || !digitsEl || !createBtn) return;

    // Asegurar que los botones de acción estén ocultos al inicio
    if (actions) actions.style.display = "none";
    // El contenedor de visualización se deja vacío (sin celdas)

    async function reload() {
      currentState = await fetchState();
      renderGrid();
      if (actions) {
        actions.style.display = currentState.size > 0 ? "block" : "none";
      }
      if (valueEl) {
        valueEl.removeAttribute("maxlength");
        valueEl.placeholder = currentState.digits > 0 ? `Máx: ${currentState.digits} dígitos` : "Clave";
      }
    }

    createBtn.addEventListener("click", async () => {
      const size = parseInt(sizeEl.value) || 5;
      const digits = parseInt(digitsEl.value) || 2;
      try {
        const response = await fetch(`${API_BASE}/create`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ size, digits }),
        });
        if (!response.ok) throw new Error("Error al crear estructura");
        await reload();
        notifySuccess("Estructura creada correctamente.");
      } catch (error) {
        notifyError(error.message);
      }
    });

    if (valueEl) {
      valueEl.addEventListener("input", () => {
        const d = currentState.digits || parseInt(digitsEl.value) || 0;
        enforceNumericDigits(valueEl, d);
      });
    }

    if (insertBtn && valueEl) {
      insertBtn.addEventListener("click", async () => {
        if (insertBtn.disabled) return;
        try {
          if (!currentState.size) throw new Error("Primero crea la estructura.");
          if (!valueEl.value) throw new Error("Ingresa una clave.");

          insertBtn.disabled = true;
          const value = toDigits(valueEl.value, currentState.digits);

          const res = await fetch(`${API_BASE}/insert`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ value }),
          });

          if (!res.ok) {
            const errorData = await res.json();
            throw new Error(errorData.detail || "No se pudo insertar");
          }

          await reload(); 
          const result = await scanAnimation(value, currentState, 300); 
          notifySuccess(`Clave ${value} insertada correctamente en la dirección ${result.position}.`);
          valueEl.value = "";
        } catch (error) {
          notifyError(error.message);
        } finally {
          insertBtn.disabled = false;
        }
      });
    }

    if (searchBtn && valueEl) {
      searchBtn.addEventListener("click", async () => {
        if (!currentState.size) return notifyError("Estructura no inicializada.");
        if (!valueEl.value) return notifyError("Ingresa una clave.");
        
        const value = toDigits(valueEl.value, currentState.digits);
        const result = await scanAnimation(value, currentState, 350);

        if (result.found) {
          notifySuccess(`Clave ${value} encontrada en la dirección ${result.position}.`);
        } else {
          notifyError(`Clave ${value} no encontrada.`);
        }
      });
    }

    if (deleteBtn && valueEl) {
      deleteBtn.addEventListener("click", async () => {
        if (!currentState.size) return;
        if (!valueEl.value) return;
        
        const value = toDigits(valueEl.value, currentState.digits);
        
        try {
          const result = await scanAnimation(value, currentState, 300);
          if (!result.found) {
            notifyError("No se encontró el valor para eliminar.");
            return;
          }

          const res = await fetch(`${API_BASE}/delete/${encodeURIComponent(value)}`, { 
            method: "DELETE" 
          });
          
          if (res.ok) {
            await reload();
            notifySuccess(`Clave ${value} eliminada de la dirección ${result.position}.`);
            valueEl.value = "";
          } else {
            notifyError("Error al procesar la eliminación.");
          }
        } catch (error) {
          notifyError("Error de conexión.");
        }
      });
    }

    // Cargar estado inicial (vacío)
    currentState = await fetchState();
    renderGrid();
  }

  window.initSimulator = initSecuencial;
})();