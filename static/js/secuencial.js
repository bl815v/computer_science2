/* eslint-disable no-console */
(() => {
  "use strict";

  const API_BASE = "http://127.0.0.1:8000/linear-search";
  let isNotifying = false;

  function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  function toDigits(v, digits) {
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
      if (val == null) cell.classList.add("empty");
      cell.dataset.index = String(i + 1);
      cell.textContent = val == null ? "" : toDigits(val, state.digits);
      grid.appendChild(cell);
    }
  }

  async function scanAnimation(size, positions1B, stepMs = 450) {
    const grid = document.getElementById("visualization");
    if (!grid) return;

    // CORRECCIÓN: Convertimos a números explícitamente y restamos 1 para el índice 0
    const foundSet = new Set(positions1B.map((p) => Number(p) - 1));
    const cells = grid.querySelectorAll(".cell");

    // Limpieza inicial
    cells.forEach((c) => c.classList.remove("active", "found", "not-found", "visited"));

    for (let i = 0; i < size; i++) {
      cells.forEach((c) => c.classList.remove("active"));
      cells[i].classList.add("active");

      // Verificamos si el índice actual está en el Set de encontrados
      if (foundSet.has(i)) {
        cells[i].classList.add("found");
      } else {
        cells[i].classList.add("visited");
      }

      await sleep(stepMs);
    }

    // Al terminar el recorrido
    if (foundSet.size === 0) {
      cells.forEach((c) => {
        c.classList.remove("active");
        c.classList.add("not-found");
      });
      await sleep(1000);
      cells.forEach((c) => c.classList.remove("not-found", "visited"));
    } else {
      // Si encontró algo, quitamos el foco activo pero dejamos el éxito visible un momento
      cells.forEach((c) => c.classList.remove("active"));
      await sleep(1500); 
      cells.forEach((c) => c.classList.remove("found", "visited"));
    }
  }

  function enforceNumericDigits(input, digits) {
    const originalValue = input.value;
    input.value = input.value.replace(/\D+/g, "");
    if (digits > 0 && originalValue.length > digits) {
      input.value = originalValue.slice(0, digits);
      if (!isNotifying) {
        isNotifying = true;
        notifyError(`La clave solo puede tener ${digits} dígitos.`);
        setTimeout(() => { isNotifying = false; }, 500);
      }
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

    let state = null;

    async function reload() {
      state = await fetchState();
      renderGrid(state);
      if (actions) actions.style.display = state.size > 0 ? "block" : "none";
      if (valueEl && state.digits > 0) {
        valueEl.maxLength = state.digits + 1;
        valueEl.placeholder = `Ej: ${toDigits(1, state.digits)}`;
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
        if (!response.ok) throw new Error("Error creando estructura");
        await reload();
        notifySuccess("Estructura creada correctamente.");
      } catch (error) {
        notifyError(error.message);
      }
    });

    if (valueEl) {
      valueEl.addEventListener("input", () => {
        const d = state?.digits || parseInt(digitsEl.value) || 0;
        enforceNumericDigits(valueEl, d);
      });
    }

    if (insertBtn && valueEl) {
      insertBtn.addEventListener("click", async () => {
        if (insertBtn.dataset.loading === "true") return;
        try {
          if (!state || state.size === 0) throw new Error("Primero crea la estructura.");
          if (!valueEl.value) throw new Error("Ingresa una clave.");

          insertBtn.dataset.loading = "true";
          insertBtn.disabled = true;

          const value = valueEl.value.padStart(state.digits, "0");
          const res = await fetch(`${API_BASE}/insert`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ value }),
          });

          if (!res.ok) {
            const errorData = await res.json();
            throw new Error(errorData.detail || "No se pudo insertar");
          }

          // Obtenemos el nuevo estado ANTES de la animación para ver el valor puesto
          state = await fetchState();
          renderGrid(state);

          const positions = [];
          state.data.forEach((v, i) => {
            if (v === value) positions.push(i + 1);
          });

          await scanAnimation(state.size, positions, 300);
          notifySuccess(`Clave ${value} insertada correctamente.`);
          valueEl.value = "";
        } catch (error) {
          notifyError(error.message);
        } finally {
          insertBtn.disabled = false;
          insertBtn.dataset.loading = "false";
        }
      });
    }

    if (searchBtn && valueEl) {
      searchBtn.addEventListener("click", async () => {
        if (!state || state.size === 0) return notifyError("Primero crea la estructura.");
        if (!valueEl.value) return notifyError("Ingresa una clave.");
        const value = valueEl.value.padStart(state.digits, "0");
        try {
          const res = await fetch(`${API_BASE}/search/${encodeURIComponent(value)}`);
          const body = await res.json();
          const positions = Array.isArray(body.positions) ? body.positions : [];

          await scanAnimation(state.size, positions, 350);

          if (positions.length) {
            notifySuccess(`Clave ${value} encontrada.`);
          } else {
            notifyError(`Clave ${value} no encontrada.`);
          }
        } catch (error) {
          notifyError("Error en la búsqueda");
        }
      });
    }

    if (deleteBtn && valueEl) {
      deleteBtn.addEventListener("click", async () => {
        if (!state || state.size === 0) return;
        if (!valueEl.value) return;
        const value = valueEl.value.padStart(state.digits, "0");
        try {
          const preview = [];
          state.data.forEach((v, i) => { if (v === value) preview.push(i + 1); });
          await scanAnimation(state.size, preview, 300);

          const res = await fetch(`${API_BASE}/delete/${encodeURIComponent(value)}`, { method: "DELETE" });
          const body = await res.json();
          await reload();
          if (body.deleted_positions?.length) notifySuccess("Eliminado correctamente.");
          else notifyError("No se encontró el valor.");
          valueEl.value = "";
        } catch (error) {
          notifyError("Error al borrar");
        }
      });
    }

    await reload();
  }

  window.initSimulator = initSecuencial;
})();