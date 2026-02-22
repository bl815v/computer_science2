(() => {
  "use strict";

  const API_BASE = "http://127.0.0.1:8000/binary-search";
  let isAlertActive = false; // Control para no saturar de notificaciones

  function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  function toDigits(v, digits) {
    return String(v).padStart(digits, "0");
  }

  /**
   * Valida la entrada numérica y dispara la notificación si excede los dígitos
   */
  function enforceNumeric(input, digits) {
    const originalValue = input.value;
    // Eliminar cualquier cosa que no sea número
    const numericValue = originalValue.replace(/\D+/g, "");

    if (digits > 0 && numericValue.length > digits) {
      // Recortamos el valor al máximo permitido
      input.value = numericValue.slice(0, digits);

      // Si no hay una alerta mostrándose, la lanzamos
      if (!isAlertActive) {
        isAlertActive = true;
        notifyError(`La clave solo puede tener ${digits} dígitos.`);
        
        // Desbloqueamos después de un breve tiempo para permitir futuras alertas
        setTimeout(() => {
          isAlertActive = false;
        }, 1500);
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

  async function binarySearchAnimation(targetValue, state) {
    const cells = document.querySelectorAll("#bin-visualization .cell");
    const validLength = state.data.filter((v) => v !== null).length;

    let left = 0;
    let right = validLength - 1;

    cells.forEach((c) =>
      c.classList.remove("active", "found", "discarded")
    );

    while (left <= right) {
      let mid = Math.floor((left + right) / 2);

      cells[mid].classList.add("active");
      await sleep(800);

      if (state.data[mid] === targetValue) {
        cells[mid].classList.add("found");
        notifySuccess(`Valor ${targetValue} encontrado.`);
        return true;
      }

      if (state.data[mid] < targetValue) {
        for (let i = left; i <= mid; i++)
          cells[i].classList.add("discarded");
        left = mid + 1;
      } else {
        for (let i = mid; i <= right; i++)
          cells[i].classList.add("discarded");
        right = mid - 1;
      }

      await sleep(500);
    }

    notifyError(`Valor ${targetValue} no encontrado.`);
    return false;
  }

  async function initBinaria() {
    const sizeEl = document.getElementById("bin-size");
    const digitsEl = document.getElementById("bin-digits");
    const valInput = document.getElementById("bin-value-input");

    const createBtn = document.getElementById("bin-create-btn");
    const insertBtn = document.getElementById("bin-insert-btn");
    const searchBtn = document.getElementById("bin-search-btn");

    if (!sizeEl || !digitsEl || !createBtn) {
      console.warn("[binaria] Faltan elementos del DOM.");
      return;
    }

    let currentState = { size: 0, digits: 0, data: [] };

    async function reload() {
      try {
        const res = await fetch(`${API_BASE}/state`);
        if (!res.ok) throw new Error("No se pudo obtener el estado");

        currentState = await res.json();
        renderGrid(currentState);

        if (valInput && currentState.digits > 0) {
          // Quitamos el maxLength nativo para que el evento 'input' detecte el exceso
          // y podamos disparar nuestra propia notificación.
          valInput.removeAttribute("maxlength"); 
          valInput.placeholder = `Máx: ${currentState.digits} dígitos`;
        }
      } catch (error) {
        notifyError(error.message);
        resetInput(valInput);
      }
    }

    createBtn.addEventListener("click", async () => {
      const size = parseInt(sizeEl.value);
      const digits = parseInt(digitsEl.value);

      if (!size || !digits) {
        notifyError("Debes ingresar tamaño y número de dígitos.");
        return;
      }

      try {
        const res = await fetch(`${API_BASE}/create`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ size, digits }),
        });

        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.detail || "Error creando estructura");
        }

        await reload();
        notifySuccess("Estructura creada correctamente.");
      } catch (error) {
        notifyError(error.message);
        resetInput(valInput);
      }
    });

    if (valInput) {
      valInput.addEventListener("input", () => {
        // Usamos la cantidad de dígitos definida en la estructura actual
        const limit = currentState.digits || parseInt(digitsEl.value) || 0;
        enforceNumeric(valInput, limit);
      });
    }

    insertBtn.addEventListener("click", async () => {
      if (!currentState.size) {
        notifyError("Primero crea la estructura.");
        return;
      }

      if (!valInput.value) {
        notifyError("Ingresa un valor.");
        return;
      }

      const val = toDigits(valInput.value, currentState.digits);

      try {
        const res = await fetch(`${API_BASE}/insert`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ value: val }),
        });

        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.detail || "No se pudo insertar");
        }

        await reload();
        notifySuccess(`Valor ${val} insertado.`);
        valInput.value = "";
      } catch (error) {
        notifyError(error.message);
        resetInput(valInput);
      }
    });

    searchBtn.addEventListener("click", async () => {
      if (!currentState.size) {
        notifyError("Primero crea la estructura.");
        return;
      }

      if (!valInput.value) {
        notifyError("Ingresa un valor.");
        return;
      }

      const val = toDigits(valInput.value, currentState.digits);
      await binarySearchAnimation(val, currentState);
    });

    await reload();
  }

  window.initSimulator = initBinaria;
})();