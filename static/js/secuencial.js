/* eslint-disable no-console */
(() => {
  "use strict";

  const API_BASE = getApiUrl(API_CONFIG.ENDPOINTS.LINEAR_SEARCH);
  let isNotifying = false;

  function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  function toDigits(v, digits) {
    if (v === null || v === undefined || v === "") return "";
    return String(v).padStart(digits, "0");
  }

  function resetInput(input) {
    if (input) {
      input.value = "";
      input.focus();
    }
  }

  async function fetchState() {
    try {
      const res = await fetchWithTimeout(`${API_BASE}/state`);
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

  async function scanAnimation(targetValue, state, stepMs = API_CONFIG.ANIMATION_SPEED.NORMAL) {
    const grid = document.getElementById("visualization");
    if (!grid) return { found: false, position: -1 };
    
    const cells = grid.querySelectorAll(".cell");
    let foundAny = false;
    let foundIndex = -1;
    
    cells.forEach(c => {
      c.classList.remove("active", "found", "not-found", "visited");
    });

    for (let i = 0; i < Math.min(state.size, cells.length); i++) {
      cells.forEach(c => c.classList.remove("active"));
      cells[i].classList.add("active");

      const cellContent = cells[i].textContent.trim();
      const normalizedTarget = String(targetValue).trim();

      if (cellContent !== "" && cellContent === normalizedTarget) {
        cells[i].classList.remove("active");
        cells[i].classList.add("found");
        foundAny = true;
        foundIndex = i + 1;
        break;
      } else if (cellContent !== "") {
        cells[i].classList.add("visited");
      }

      await sleep(stepMs);
    }

    if (!foundAny) {
      cells.forEach(c => {
        c.classList.remove("active");
        if (c.textContent.trim() !== "") {
          c.classList.add("not-found");
        }
      });
      await sleep(1500);
      cells.forEach(c => c.classList.remove("not-found", "visited"));
    } else {
      await sleep(1500);
      cells.forEach(c => c.classList.remove("found", "visited", "active"));
    }
    
    return { found: foundAny, position: foundIndex };
  }

  function enforceNumericDigits(input, digits) {
    if (!input || digits <= 0) return;
    
    const originalValue = input.value;
    const numericValue = originalValue.replace(/\D+/g, "");
    
    if (numericValue.length > digits) {
      input.value = numericValue.slice(0, digits);
      if (!isNotifying) {
        isNotifying = true;
        window.notifyError(`La clave solo puede tener ${digits} dígitos.`, true);
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
    const actionsSection = document.getElementById("actions-section");
    const valueEl = document.getElementById("value-input");
    const insertBtn = document.getElementById("insert-btn");
    const searchBtn = document.getElementById("search-btn");
    const deleteBtn = document.getElementById("delete-btn");

    if (!sizeEl || !digitsEl || !createBtn) return;

    let state = { size: 0, digits: 0, data: [] };

    async function reload() {
      state = await fetchState();
      renderGrid(state);
      if (valueEl) {
        valueEl.placeholder = state.digits > 0 ? `Máx: ${state.digits} dígitos` : "Clave";
      }
    }

    createBtn.addEventListener("click", async () => {
      const size = parseInt(sizeEl.value) || 5;
      const digits = parseInt(digitsEl.value) || 2;
      try {
        const response = await fetchWithTimeout(`${API_BASE}/create`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ size, digits }),
        });
        if (!response.ok) throw new Error("Error al crear estructura");
        await reload();
        
        // Mostrar acciones después de crear la estructura
        if (actionsSection) {
          actionsSection.style.display = "block";
        }
        
        window.notifySuccess("Estructura creada correctamente.", true);
      } catch (error) {
        window.notifyError(error.message, true);
      }
    });

    if (valueEl) {
      valueEl.addEventListener("input", () => {
        const d = state.digits || parseInt(digitsEl?.value) || 0;
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

          const res = await fetchWithTimeout(`${API_BASE}/insert`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ value }),
          });

          if (!res.ok) {
            const errorData = await res.json();
            throw new Error(errorData.detail || "No se pudo insertar");
          }

          await reload();
          const result = await scanAnimation(value, state, API_CONFIG.ANIMATION_SPEED.FAST);
          window.notifySuccess(`Clave ${value} insertada correctamente en la dirección ${result.position}.`, true);
          valueEl.value = "";
        } catch (error) {
          window.notifyError(error.message, true);
        } finally {
          insertBtn.disabled = false;
        }
      });
    }

    if (searchBtn && valueEl) {
      searchBtn.addEventListener("click", async () => {
        if (!state.size) {
          window.notifyError("Estructura no inicializada.", true);
          return;
        }
        if (!valueEl.value) {
          window.notifyError("Ingresa una clave.", true);
          return;
        }
        
        const value = toDigits(valueEl.value, state.digits);
        const result = await scanAnimation(value, state, API_CONFIG.ANIMATION_SPEED.NORMAL);

        if (result.found) {
          window.notifySuccess(`Clave ${value} encontrada en la dirección ${result.position}.`, true);
        } else {
          window.notifyError(`Clave ${value} no encontrada.`, true);
        }
      });
    }

    if (deleteBtn && valueEl) {
      deleteBtn.addEventListener("click", async () => {
        if (!state.size) {
          window.notifyError("Estructura no inicializada.", true);
          return;
        }
        if (!valueEl.value) {
          window.notifyError("Ingresa una clave.", true);
          return;
        }
        
        const value = toDigits(valueEl.value, state.digits);
        
        try {
          const result = await scanAnimation(value, state, API_CONFIG.ANIMATION_SPEED.FAST);
          if (!result.found) {
            window.notifyError("No se encontró el valor para eliminar.", true);
            return;
          }

          const res = await fetchWithTimeout(`${API_BASE}/delete/${encodeURIComponent(value)}`, { 
            method: "DELETE" 
          });
          
          if (res.ok) {
            await reload();
            window.notifySuccess(`Clave ${value} eliminada de la dirección ${result.position}.`, true);
            valueEl.value = "";
          } else {
            window.notifyError("Error al procesar la eliminación.", true);
          }
        } catch (error) {
          window.notifyError("Error de conexión.", true);
        }
      });
    }

    await reload();
  }

  window.initSimulator = initSecuencial;
})();