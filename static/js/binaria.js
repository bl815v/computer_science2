(() => {
  "use strict";

  const API_BASE = getApiUrl(API_CONFIG.ENDPOINTS.BINARY_SEARCH);
  let isAlertActive = false;

  function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  function toDigits(v, digits) {
    return String(v).padStart(digits, "0");
  }

  function enforceNumeric(input, digits) {
    if (!input || digits <= 0) return;
    
    const originalValue = input.value;
    const numericValue = originalValue.replace(/\D+/g, "");
    if (digits > 0 && numericValue.length > digits) {
      input.value = numericValue.slice(0, digits);
      if (!isAlertActive) {
        isAlertActive = true;
        window.notifyError(`La clave solo puede tener ${digits} dígitos.`, true);
        setTimeout(() => { isAlertActive = false; }, 1500);
      }
    } else {
      input.value = numericValue;
    }
  }

  function renderGrid(state) {
    const grid = document.getElementById("bin-visualization");
    if (!grid) return;
    grid.innerHTML = "";
    for (let i = 0; i < state.size; i++) {
      const val = state.data[i];
      const cell = document.createElement("div");
      cell.className = "cell";
      
      if (val == null || val === "") {
        cell.classList.add("empty");
        cell.textContent = ""; 
      } else {
        cell.dataset.index = i + 1;
        cell.textContent = val;
      }
      grid.appendChild(cell);
    }
  }

  async function binarySearchAnimation(targetValue, state) {
    const cells = document.querySelectorAll("#bin-visualization .cell");
    const validData = state.data.filter((v) => v !== null && v !== "");
    const validLength = validData.length;

    let left = 0;
    let right = validLength - 1;
    let found = false;
    let foundIndex = -1;

    cells.forEach((c) => c.classList.remove("active", "found", "discarded"));

    while (left <= right) {
      let mid = Math.floor((left + right) / 2);
      
      cells[mid].classList.add("active");
      await sleep(API_CONFIG.ANIMATION_SPEED.SLOW);

      const midValue = String(state.data[mid]).trim();
      const searchValue = String(targetValue).trim();

      if (midValue === searchValue) {
        cells[mid].classList.remove("active");
        cells[mid].classList.add("found");
        found = true;
        foundIndex = mid + 1;
        break; 
      }

      cells[mid].classList.remove("active");

      if (midValue < searchValue) {
        for (let i = left; i <= mid; i++) {
          if (state.data[i] !== null && state.data[i] !== "") {
            cells[i].classList.add("discarded");
          }
        }
        left = mid + 1;
      } else {
        for (let i = mid; i <= right; i++) {
          if (state.data[i] !== null && state.data[i] !== "") {
            cells[i].classList.add("discarded");
          }
        }
        right = mid - 1;
      }
      await sleep(API_CONFIG.ANIMATION_SPEED.NORMAL);
    }

    if (!found) {
      window.notifyError(`Valor ${targetValue} no encontrado.`, true);
    } else {
      window.notifySuccess(`Valor ${targetValue} encontrado en dirección ${foundIndex}.`, true);
    }

    await sleep(2000);
    cells.forEach((c) => {
      c.classList.remove("active", "found", "discarded");
    });

    return found;
  }

  async function initBinaria() {
    const sizeEl = document.getElementById("bin-size");
    const digitsEl = document.getElementById("bin-digits");
    const valInput = document.getElementById("bin-value-input");
    const createBtn = document.getElementById("bin-create-btn");
    const actionsSection = document.getElementById("actions-section");
    const insertBtn = document.getElementById("bin-insert-btn");
    const searchBtn = document.getElementById("bin-search-btn");
    const deleteBtn = document.getElementById("bin-delete-btn");

    if (!sizeEl || !digitsEl || !createBtn) return;

    let currentState = { size: 0, digits: 0, data: [] };

    async function reload() {
      try {
        const res = await fetchWithTimeout(`${API_BASE}/state`);
        if (!res.ok) throw new Error("No se pudo obtener el estado");
        currentState = await res.json();
        renderGrid(currentState);
        if (valInput && currentState.digits > 0) {
          valInput.placeholder = `Máx: ${currentState.digits} dígitos`;
        }
      } catch (error) {
        console.error(error);
        window.notifyError("Error al cargar el estado", true);
      }
    }

    createBtn.addEventListener("click", async () => {
      const size = parseInt(sizeEl.value);
      const digits = parseInt(digitsEl.value);
      if (!size || !digits) {
        window.notifyError("Datos incompletos.", true);
        return;
      }
      try {
        await fetchWithTimeout(`${API_BASE}/create`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ size, digits }),
        });
        await reload();
        
        // Mostrar acciones después de crear la estructura
        if (actionsSection) {
          actionsSection.style.display = "block";
        }
        
        window.notifySuccess("Estructura creada.", true);
      } catch (error) {
        window.notifyError(error.message, true);
      }
    });

    if (valInput) {
      valInput.addEventListener("input", () => {
        const limit = currentState.digits || parseInt(digitsEl.value) || 0;
        enforceNumeric(valInput, limit);
      });
    }

    if (insertBtn) {
      insertBtn.addEventListener("click", async () => {
        if (!currentState.size) {
          window.notifyError("Crea la estructura primero.", true);
          return;
        }
        if (!valInput?.value) {
          window.notifyError("Ingresa un valor.", true);
          return;
        }
        
        const val = toDigits(valInput.value, currentState.digits);

        try {
          const res = await fetchWithTimeout(`${API_BASE}/insert`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ value: val }),
          });

          if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Error en la inserción");
          }

          await reload();
          window.notifySuccess(`Valor ${val} insertado.`, true);
          valInput.value = "";
        } catch (error) {
          window.notifyError(error.message, true);
        }
      });
    }

    if (searchBtn) {
      searchBtn.addEventListener("click", async () => {
        if (!currentState.size) {
          window.notifyError("Crea la estructura.", true);
          return;
        }
        if (!valInput?.value) {
          window.notifyError("Ingresa valor.", true);
          return;
        }
        const val = toDigits(valInput.value, currentState.digits);
        await binarySearchAnimation(val, currentState);
      });
    }

    if (deleteBtn) {
      deleteBtn.addEventListener("click", async () => {
        if (!currentState.size) {
          window.notifyError("Crea la estructura.", true);
          return;
        }
        if (!valInput?.value) {
          window.notifyError("Ingresa el valor a eliminar.", true);
          return;
        }

        const val = toDigits(valInput.value, currentState.digits);

        try {
          const found = await binarySearchAnimation(val, currentState);

          if (found) {
            const res = await fetchWithTimeout(`${API_BASE}/delete/${encodeURIComponent(val)}`, {
              method: "DELETE",
            });

            if (!res.ok) {
              const err = await res.json();
              throw new Error(err.detail || "Error al eliminar");
            }

            await reload();
            window.notifySuccess(`Valor ${val} eliminado.`, true);
            valInput.value = "";
          }
        } catch (error) {
          window.notifyError(error.message, true);
        }
      });
    }

    await reload();
  }

  window.initSimulator = initBinaria;
})();