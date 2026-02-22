/* eslint-disable no-console */
/**
 * Sequential (frontend)
 * - Supported by FastAPI backend (/linear-search)
 * - UI + animations only
 * - Uses global notification system (notifications.js)
 */

(() => {
  "use strict";

  const API_BASE = "http://127.0.0.1:8000/linear-search";

  function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  function toDigits(v, digits) {
    return String(v).padStart(digits, "0");
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
    grid.className = "";

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

    const foundSet = new Set(positions1B.map((p) => p - 1));
    const cells = grid.querySelectorAll(".cell");

    cells.forEach((c) => c.classList.remove("active", "found", "not-found"));

    for (let i = 0; i < size; i++) {
      cells.forEach((c) => c.classList.remove("active"));
      cells[i].classList.add("active");

      if (foundSet.has(i)) cells[i].classList.add("found");

      await sleep(stepMs);
    }

    if (foundSet.size === 0) {
      cells.forEach((c) => {
        c.classList.remove("active");
        c.classList.add("not-found");
      });
      await sleep(800);
      cells.forEach((c) => c.classList.remove("not-found"));
    } else {
      await sleep(600);
      cells.forEach((c) => c.classList.remove("active", "found"));
    }
  }

  function enforceNumericDigits(input, digits) {
    input.value = input.value.replace(/\D+/g, "");
    if (digits > 0 && input.value.length > digits) {
      input.value = input.value.slice(0, digits);
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

    if (!sizeEl || !digitsEl || !createBtn) {
      console.warn("[secuencial] Faltan elementos del DOM.");
      return;
    }

    let state = null;

    async function reload() {
      state = await fetchState();
      renderGrid(state);

      if (actions) actions.style.display = state.size > 0 ? "block" : "none";

      if (valueEl && state.digits > 0) {
        valueEl.maxLength = state.digits;
        valueEl.placeholder = `Ej: ${toDigits(1, state.digits)}`;
      }
    }

    async function createStructure() {
      const size = parseInt(sizeEl.value) || 5;
      const digits = parseInt(digitsEl.value) || 2;

      try {
        const response = await fetch(`${API_BASE}/create`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ size, digits }),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || "Error creando estructura");
        }

        await reload();
        notifySuccess("Estructura creada correctamente.");
      } catch (error) {
        notifyError(error.message);
      }
    }

    createBtn.addEventListener("click", createStructure);

    if (valueEl) {
      valueEl.addEventListener("input", () => {
        const d = state?.digits || parseInt(digitsEl.value) || 0;
        enforceNumericDigits(valueEl, d);
      });
    }

    if (insertBtn && valueEl) {
      insertBtn.addEventListener("click", async () => {
        if (!state || state.size === 0) {
          notifyError("Primero crea la estructura.");
          return;
        }

        enforceNumericDigits(valueEl, state.digits);

        if (!valueEl.value) {
          notifyError("Ingresa una clave.");
          return;
        }

        const value = valueEl.value.padStart(state.digits, "0");

        try {
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

          const positions = [];
          state.data.forEach((v, i) => {
            if (v === value) positions.push(i + 1);
          });

          await scanAnimation(state.size, positions, 300);

          notifySuccess(`Clave ${value} insertada en la dirección ${positions[0]}`);
          valueEl.value = "";
        } catch (error) {
          notifyError(error.message);
        }
      });
    }

    if (searchBtn && valueEl) {
      searchBtn.addEventListener("click", async () => {
        if (!state || state.size === 0) {
          notifyError("Primero crea la estructura.");
          return;
        }

        enforceNumericDigits(valueEl, state.digits);

        if (!valueEl.value) {
          notifyError("Ingresa una clave.");
          return;
        }

        const value = valueEl.value.padStart(state.digits, "0");

        try {
          const res = await fetch(
            `${API_BASE}/search/${encodeURIComponent(value)}`
          );

          if (!res.ok) {
            const errorData = await res.json();
            throw new Error(errorData.detail || "Error en la búsqueda");
          }

          const body = await res.json();
          const positions = Array.isArray(body.positions)
            ? body.positions
            : [];

          await scanAnimation(state.size, positions, 350);

          if (positions.length) {
            notifySuccess(
              `Clave ${value} encontrada en posiciones: ${positions.join(", ")}`
            );
          } else {
            notifyError(`Clave ${value} no encontrada.`);
          }
        } catch (error) {
          notifyError(error.message);
        }
      });
    }

    if (deleteBtn && valueEl) {
      deleteBtn.addEventListener("click", async () => {
        if (!state || state.size === 0) {
          notifyError("Primero crea la estructura.");
          return;
        }

        enforceNumericDigits(valueEl, state.digits);

        if (!valueEl.value) {
          notifyError("Ingresa una clave.");
          return;
        }

        const value = valueEl.value.padStart(state.digits, "0");

        try {
          const preview = [];
          state.data.forEach((v, i) => {
            if (v === value) preview.push(i + 1);
          });

          await scanAnimation(state.size, preview, 300);

          const res = await fetch(
            `${API_BASE}/delete/${encodeURIComponent(value)}`,
            { method: "DELETE" }
          );

          if (!res.ok) {
            const errorData = await res.json();
            throw new Error(errorData.detail || "No se pudo eliminar");
          }

          const body = await res.json();
          await reload();

          if (body.deleted_positions?.length) {
            notifySuccess(
              `Eliminado en posiciones: ${body.deleted_positions.join(", ")}`
            );
          } else {
            notifyInfo("No había ocurrencias para eliminar.");
          }

          valueEl.value = "";
        } catch (error) {
          notifyError(error.message);
        }
      });
    }

    try {
      await reload();
    } catch {
      console.info("[secuencial] Esperando creación de estructura…");
    }
  }

  window.initSimulator = initSecuencial;

  if (document.getElementById("create-structure")) {
    initSecuencial().catch(console.error);
  }
})();