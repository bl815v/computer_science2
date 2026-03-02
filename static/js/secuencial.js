/* eslint-disable no-console */
(() => {
  "use strict";

  const API_BASE = "http://127.0.0.1:8000/linear-search";
  let isNotifying = false;

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

  function renderGrid(state) {
    const grid = document.getElementById("visualization");
    if (!grid) return;
    grid.innerHTML = "";
    for (let i = 0; i < state.size; i++) {
      const val = state.data[i];
      const cell = document.createElement("div");
      cell.className = "cell";
      if (val == null || val === "") cell.classList.add("empty");
      cell.dataset.index = String(i + 1);
      cell.textContent = (val == null || val === "") ? "" : toDigits(val, state.digits);
      grid.appendChild(cell);
    }
  }

  // (La función renderEmptyGrid se puede eliminar o dejar, pero ya no se usa)
  function renderEmptyGrid(size, digits) {
    const grid = document.getElementById("visualization");
    if (!grid) return;
    grid.innerHTML = "";
    for (let i = 0; i < size; i++) {
      const cell = document.createElement("div");
      cell.className = "cell empty";
      cell.dataset.index = String(i + 1);
      cell.textContent = "";
      grid.appendChild(cell);
    }
  }

  async function scanAnimation(targetValue, state, stepMs = 450) {
    const grid = document.getElementById("visualization");
    if (!grid) return { found: false, position: -1 };
    const cells = grid.querySelectorAll(".cell");
    let foundAny = false;
    let foundIndex = -1;

    cells.forEach((c) => c.classList.remove("active", "found", "not-found", "visited"));

    for (let i = 0; i < state.size; i++) {
      cells.forEach((c) => c.classList.remove("active"));
      cells[i].classList.add("active");

      const cellContent = cells[i].textContent.trim();
      const normalizedTarget = String(targetValue).trim();

      if (cellContent !== "" && cellContent === normalizedTarget) {
        cells[i].classList.add("found");
        foundAny = true;
        foundIndex = i + 1;
        break;
      } else {
        cells[i].classList.add("visited");
      }

      await sleep(stepMs);
    }

    if (!foundAny) {
      cells.forEach((c) => {
        c.classList.remove("active");
        c.classList.add("not-found");
      });
      await sleep(1000);
      cells.forEach((c) => c.classList.remove("not-found", "visited"));
    } else {
      cells.forEach((c) => c.classList.remove("active"));
      await sleep(1000); 
      cells.forEach((c) => c.classList.remove("found", "visited"));
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

    let state = { size: 0, digits: 0, data: [] };

    // Asegurar que los botones de acción estén ocultos al inicio
    if (actions) actions.style.display = "none";
    // El contenedor de visualización se deja vacío (sin celdas)

    async function reload() {
      state = await fetchState();
      renderGrid(state);
      if (actions) {
        actions.style.display = state.size > 0 ? "block" : "none";
      }
      if (valueEl) {
        valueEl.removeAttribute("maxlength");
        valueEl.placeholder = state.digits > 0 ? `Máx: ${state.digits} dígitos` : "Clave";
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
        const d = state.digits || parseInt(digitsEl.value) || 0;
        enforceNumericDigits(valueEl, d);
      });
    }

    if (insertBtn && valueEl) {
      insertBtn.addEventListener("click", async () => {
        if (insertBtn.disabled) return;
        try {
          if (!state.size) throw new Error("Primero crea la estructura.");
          if (!valueEl.value) throw new Error("Ingresa una clave.");

          insertBtn.disabled = true;
          const value = toDigits(valueEl.value, state.digits);

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
          const result = await scanAnimation(value, state, 300); 
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
        if (!state.size) return notifyError("Estructura no inicializada.");
        if (!valueEl.value) return notifyError("Ingresa una clave.");
        
        const value = toDigits(valueEl.value, state.digits);
        const result = await scanAnimation(value, state, 350);

        if (result.found) {
          notifySuccess(`Clave ${value} encontrada en la dirección ${result.position}.`);
        } else {
          notifyError(`Clave ${value} no encontrada.`);
        }
      });
    }

    if (deleteBtn && valueEl) {
      deleteBtn.addEventListener("click", async () => {
        if (!state.size) return;
        if (!valueEl.value) return;
        
        const value = toDigits(valueEl.value, state.digits);
        
        try {
          const result = await scanAnimation(value, state, 300);
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
  }

  window.initSimulator = initSecuencial;
})();