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
      if (val == null) cell.classList.add("empty");
      cell.dataset.index = i + 1;
      cell.textContent = val == null ? "" : val;
      grid.appendChild(cell);
    }
  }

  // --- ANIMACIÓN ACTUALIZADA CON RESET FINAL ---
  async function binarySearchAnimation(targetValue, state) {
    const cells = document.querySelectorAll("#bin-visualization .cell");
    const validData = state.data.filter((v) => v !== null);
    const validLength = validData.length;

    let left = 0;
    let right = validLength - 1;
    let found = false;

    // Limpieza previa antes de empezar una nueva búsqueda
    cells.forEach((c) => c.classList.remove("active", "found", "discarded"));

    while (left <= right) {
      let mid = Math.floor((left + right) / 2);
      
      cells[mid].classList.add("active");
      await sleep(800);

      // Usamos trim() y String() para asegurar que la comparación sea exacta
      const midValue = String(state.data[mid]).trim();
      const searchValue = String(targetValue).trim();

      if (midValue === searchValue) {
        cells[mid].classList.remove("active");
        cells[mid].classList.add("found");
        notifySuccess(`Valor ${targetValue} encontrado en posición ${mid + 1}.`);
        found = true;
        break; // Salimos del bucle si lo encontramos
      }

      cells[mid].classList.remove("active");

      if (midValue < searchValue) {
        // Descartar lado izquierdo
        for (let i = left; i <= mid; i++) {
          cells[i].classList.add("discarded");
        }
        left = mid + 1;
      } else {
        // Descartar lado derecho
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

    // --- BLOQUE DE RESET FINAL ---
    // Esperamos 2 segundos para que el cliente vea el resultado final
    await sleep(2000);

    // Removemos todas las clases para que la tabla vuelva a la normalidad
    cells.forEach((c) => {
      c.classList.remove("active", "found", "discarded");
    });
  }

  async function initBinaria() {
    const sizeEl = document.getElementById("bin-size");
    const digitsEl = document.getElementById("bin-digits");
    const valInput = document.getElementById("bin-value-input");
    const createBtn = document.getElementById("bin-create-btn");
    const insertBtn = document.getElementById("bin-insert-btn");
    const searchBtn = document.getElementById("bin-search-btn");

    if (!sizeEl || !digitsEl || !createBtn) return;

    let currentState = { size: 0, digits: 0, data: [] };

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
      } catch (error) {
        console.error(error);
      }
    }

    createBtn.addEventListener("click", async () => {
      const size = parseInt(sizeEl.value);
      const digits = parseInt(digitsEl.value);
      if (!size || !digits) return notifyError("Datos incompletos.");
      try {
        const res = await fetch(`${API_BASE}/create`, {
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
        await fetch(`${API_BASE}/insert`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ value: val }),
        });
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
      // Llamamos a la animación que ahora tiene reset incluido
      await binarySearchAnimation(val, currentState);
    });

    await reload();
  }

  window.initSimulator = initBinaria;
})();