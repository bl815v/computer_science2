(() => {
  "use strict";

  const API_BASE = "http://127.0.0.1:8000/binary-search";
  let isAlertActive = false;

  function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  function toDigits(v, digits) {
    return String(v).padStart(digits, "0");
  }

  function enforceNumeric(input, digits) {
    const originalValue = input.value;
    const numericValue = originalValue.replace(/\D+/g, "");
    if (digits > 0 && numericValue.length > digits) {
      input.value = numericValue.slice(0, digits);
      if (!isAlertActive) {
        isAlertActive = true;
        notifyError(`La clave solo puede tener ${digits} dígitos.`);
        setTimeout(() => { isAlertActive = false; }, 1500);
      }
    } else {
      input.value = numericValue;
    }
  }

  function resetInput(input) {
    input.value = "";
    input.focus();
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

  // (La función renderEmptyGrid se puede eliminar o dejar, pero ya no se usa)
  function renderEmptyGrid(size) {
    const grid = document.getElementById("bin-visualization");
    if (!grid) return;
    grid.innerHTML = "";
    for (let i = 0; i < size; i++) {
      const cell = document.createElement("div");
      cell.className = "cell empty";
      cell.dataset.index = i + 1;
      cell.textContent = "";
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

    cells.forEach((c) => c.classList.remove("active", "found", "discarded"));

    while (left <= right) {
      let mid = Math.floor((left + right) / 2);
      
      cells[mid].classList.add("active");
      await sleep(800);

      const midValue = String(state.data[mid]).trim();
      const searchValue = String(targetValue).trim();

      if (midValue === searchValue) {
        cells[mid].classList.remove("active");
        cells[mid].classList.add("found");
        notifySuccess(`Valor ${targetValue} encontrado en dirección ${mid + 1}.`);
        found = true;
        break; 
      }

      cells[mid].classList.remove("active");

      if (midValue < searchValue) {
        for (let i = left; i <= mid; i++) {
          cells[i].classList.add("discarded");
        }
        left = mid + 1;
      } else {
        for (let i = mid; i <= right; i++) {
          cells[i].classList.add("discarded");
        }
        right = mid - 1;
      }
      await sleep(500);
    }

    if (!found) {
      notifyError(`Valor ${targetValue} no encontrado.`);
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
    const insertBtn = document.getElementById("bin-insert-btn");
    const searchBtn = document.getElementById("bin-search-btn");
    const deleteBtn = document.getElementById("bin-delete-btn");
    const actionsSection = document.getElementById("actions-section");

    if (!sizeEl || !digitsEl || !createBtn) return;

    let currentState = { size: 0, digits: 0, data: [] };

    // Asegurar que los botones de acción estén ocultos al inicio
    if (actionsSection) actionsSection.style.display = "none";
    // El contenedor de visualización se deja vacío (sin celdas)

    async function reload() {
      try {
        const res = await fetch(`${API_BASE}/state`);
        if (!res.ok) throw new Error("No se pudo obtener el estado");
        currentState = await res.json();
        renderGrid(currentState);
        if (valInput && currentState.digits > 0) {
          valInput.removeAttribute("maxlength"); 
          valInput.placeholder = `Máx: ${currentState.digits} dígitos`;
        }
        if (actionsSection) {
          actionsSection.style.display = currentState.size > 0 ? "block" : "none";
        }
      } catch (error) {
        console.error(error);
      }
    }

    createBtn.addEventListener("click", async () => {
      const size = parseInt(sizeEl.value);
      const digits = parseInt(digitsEl.value);
      if (!size || !digits) return notifyError("Datos incompletos.");
      try {
        await fetch(`${API_BASE}/create`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ size, digits }),
        });
        await reload();
        notifySuccess("Estructura creada.");
      } catch (error) {
        notifyError(error.message);
      }
    });

    if (valInput) {
      valInput.addEventListener("input", () => {
        const limit = currentState.digits || parseInt(digitsEl.value) || 0;
        enforceNumeric(valInput, limit);
      });
    }

    insertBtn.addEventListener("click", async () => {
      if (!currentState.size) return notifyError("Crea la estructura primero.");
      if (!valInput.value) return notifyError("Ingresa un valor.");
      
      const val = toDigits(valInput.value, currentState.digits);

      try {
        const res = await fetch(`${API_BASE}/insert`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ value: val }),
        });

        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.detail || "Error en la inserción");
        }

        await reload();
        notifySuccess(`Valor ${val} insertado.`);
        valInput.value = "";
      } catch (error) {
        notifyError(error.message);
      }
    });

    searchBtn.addEventListener("click", async () => {
      if (!currentState.size) return notifyError("Crea la estructura.");
      if (!valInput.value) return notifyError("Ingresa valor.");
      const val = toDigits(valInput.value, currentState.digits);
      await binarySearchAnimation(val, currentState);
    });

    if (deleteBtn) {
      deleteBtn.addEventListener("click", async () => {
        if (!currentState.size) return notifyError("Crea la estructura.");
        if (!valInput.value) return notifyError("Ingresa el valor a eliminar.");

        const val = toDigits(valInput.value, currentState.digits);

        try {
          const found = await binarySearchAnimation(val, currentState);

          if (found) {
            const res = await fetch(`${API_BASE}/delete/${encodeURIComponent(val)}`, {
              method: "DELETE",
            });

            if (!res.ok) {
              const err = await res.json();
              throw new Error(err.detail || "Error al eliminar");
            }

            await reload();
            notifySuccess(`Valor ${val} eliminado.`);
            valInput.value = "";
          }
        } catch (error) {
          notifyError(error.message);
        }
      });
    }
  }

  window.initSimulator = initBinaria;
})();