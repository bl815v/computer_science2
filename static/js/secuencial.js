/* eslint-disable no-console */
/**
 * Sequential (frontend)
 * - Supported by FastAPI backend (/linear-search)
 * - This file only handles UI and animations.
 */

(() => {
  "use strict";

  /** @const {string} */
  const API_BASE = "http://127.0.0.1:8000/linear-search";

  /**
   * Wait ms miliseconds.
   * @param {number} ms
   * @return {!Promise<void>}
   */
  function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  /**
   * Left pad with zeros up to `digits`.
   * @param {number|string} v
   * @param {number} digits
   * @return {string}
   */
  function toDigits(v, digits) {
    return String(v).padStart(digits, "0");
  }

  /**
   * Gets current state of the backend.
   * @return {!Promise<{size:number,digits:number,data:Array<number|null>}>}
   */
  async function fetchState() {
    try {
      const res = await fetch(`${API_BASE}/state`);
      if (!res.ok) {
        return { size: 0, digits: 0, data: [] };
      }
      return await res.json();
    } catch (error) {
      console.warn("No se pudo obtener el estado del backend:", error);
      return { size: 0, digits: 0, data: [] };
    }
  }

  /**
   * Shows temporary message below the simulator.
   * @param {string} text
   * @param {'success'|'error'|'info'} type
   */
  function showMessage(text, type) {
    let el = document.getElementById("message");
    if (!el) {
      el = document.createElement("div");
      el.id = "message";
      const container =
        document.querySelector(".secuencial-container") ||
        document.getElementById("visualization")?.parentElement ||
        document.body;
      container.appendChild(el);
    }
    el.textContent = text;
    el.className = `message ${type}`;
    el.style.display = "block";
    setTimeout(
      () => (el.style.display = "none"),
      type === "error" ? 2000 : 4000
    );
  }

  /**
   * Renders the grid with the given state.
   * @param {{size:number,digits:number,data:Array<number|null>}} state
   */
  function renderGrid(state) {
    const grid = document.getElementById("visualization");
    if (!grid) return;

    grid.innerHTML = "";
    grid.classList.add("grid");

    for (let i = 0; i < state.size; i++) {
      const val = state.data[i];
      const cell = document.createElement("div");
      cell.className = `cell ${val == null ? "empty" : ""}`;
      cell.dataset.index = String(i + 1); // 1-based
      cell.textContent = val == null ? "-" : toDigits(val, state.digits);
      grid.appendChild(cell);
    }
  }

  /**
   * Sequentially highlights all cells and marks as found
   * positions included in `positions1B` (1-based).
   * @param {number} size
   * @param {!Array<number>} positions1B
   * @param {number=} stepMs
   * @return {!Promise<void>}
   */
  async function scanAnimation(size, positions1B, stepMs = 450) {
    const grid = document.getElementById("visualization");
    if (!grid) return;

    const foundSet = new Set(positions1B.map((p) => p - 1)); // to 0-based
    const cells = /** @type {!NodeListOf<HTMLElement>} */ (
      grid.querySelectorAll(".cell")
    );

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

  /**
   * Validates the value entry according to digits.
   * @param {HTMLInputElement} input
   * @param {number} digits
   */
  function enforceNumericDigits(input, digits) {
    input.value = input.value.replace(/\D+/g, "");
    if (digits > 0 && input.value.length > digits) {
      input.value = input.value.slice(0, digits);
    }
  }

  /**
   * Initializes events and state. It must be called after injecting sequential.html.
   */
  async function initSecuencial() {
    const sizeEl = /** @type {HTMLInputElement} */ (
      document.getElementById("size")
    );
    const digitsEl = /** @type {HTMLInputElement} */ (
      document.getElementById("digits")
    );
    const createBtn = document.getElementById("create-structure");
    const actions = document.getElementById("actions-section");
    const valueEl = /** @type {HTMLInputElement} */ (
      document.getElementById("value-input")
    );
    const insertBtn = document.getElementById("insert-btn");
    const searchBtn = document.getElementById("search-btn");
    const deleteBtn = document.getElementById("delete-btn");

    if (!sizeEl || !digitsEl || !createBtn) {
      console.warn("[secuencial] Faltan elementos del DOM para iniciar.");
      return;
    }

    /** @type {{size:number,digits:number,data:Array<number|null>}|null} */
    let state = null;

    /**
     * Reload state from backend and re-render.
     */
    async function reload() {
      try {
        state = await fetchState();
        renderGrid(state);

        const infoMessage = document.querySelector('.message.info');
        if (infoMessage && state.size > 0) {
          infoMessage.style.display = 'none';
        }

        if (actions) actions.style.display = state.size > 0 ? "block" : "none";
        if (valueEl && state.digits > 0) {
          valueEl.maxLength = state.digits;
          valueEl.placeholder = `Ej: ${toDigits(1, state.digits)}`;
        }
      } catch (error) {
        console.error("Error al recargar el estado:", error);
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
          throw new Error(errorData.detail || "Error creando la estructura");
        }

        console.log("[secuencial] Estructura creada en backend");

        await reload();
        showMessage("Estructura creada correctamente.", "success");
      } catch (error) {
        console.error("[secuencial] No se pudo crear la estructura", error);
        showMessage(error.message, "error");
      }
    }

    createBtn.addEventListener("click", createStructure);

    if (valueEl) {
      valueEl.addEventListener("input", () => {
        const d = state?.digits || Math.max(1, parseInt(digitsEl.value, 10) || 0);
        enforceNumericDigits(valueEl, d);
      });
    }

    if (insertBtn && valueEl) {
      insertBtn.addEventListener("click", async () => {
        if (!state || state.size === 0) {
          showMessage("Primero crea la estructura.", "error");
          return;
        }

        enforceNumericDigits(valueEl, state.digits);
        if (!valueEl.value) {
          showMessage("Ingresa un valor.", "error");
          return;
        }

        let value = valueEl.value.padStart(state.digits, '0');
        console.log("Attempting to insert value:", value);

        try {
          const res = await fetch(`${API_BASE}/insert`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              value: value
            }),
          });

          if (!res.ok) {
            const errorData = await res.json();
            throw new Error(errorData.detail || "No se pudo insertar");
          }

          const body = await res.json();
          await reload();

          const positions = [];
          state.data.forEach((v, i) => {
            if (v === value) positions.push(i + 1);
          });

          await scanAnimation(state.size, positions, 300);
          showMessage(
            body.message || `Valor ${value} insertado.`,
            "success"
          );
          valueEl.value = "";
        } catch (error) {
          showMessage(error.message, "error");
        }
      });
    }

    if (searchBtn && valueEl) {
      searchBtn.addEventListener("click", async () => {
        if (!state || state.size === 0) {
          showMessage("Primero crea la estructura.", "error");
          return;
        }

        enforceNumericDigits(valueEl, state.digits);
        if (!valueEl.value) {
          showMessage("Ingresa un valor.", "error");
          return;
        }

        let value = valueEl.value.padStart(state.digits, '0');

        try {
          const res = await fetch(`${API_BASE}/search/${encodeURIComponent(value)}`);

          if (!res.ok) {
            const errorData = await res.json();
            throw new Error(errorData.detail || "Error en la búsqueda");
          }

          const body = await res.json();
          const positions = Array.isArray(body.positions) ? body.positions : [];

          await scanAnimation(state.size, positions, 350);

          if (positions.length) {
            showMessage(
              `Valor ${value} ` +
              `encontrado en posiciones: ${positions.join(", ")}`,
              "success"
            );
          } else {
            showMessage(
              `Valor ${value} no encontrado.`,
              "error"
            );
          }
        } catch (error) {
          showMessage(error.message, "error");
        }
      });
    }

    if (deleteBtn && valueEl) {
      deleteBtn.addEventListener("click", async () => {
        if (!state || state.size === 0) {
          showMessage("Primero crea la estructura.", "error");
          return;
        }

        enforceNumericDigits(valueEl, state.digits);
        if (!valueEl.value) {
          showMessage("Ingresa un valor.", "error");
          return;
        }

        let value = valueEl.value.padStart(state.digits, '0');

        try {
          const preview = [];
          state.data.forEach((v, i) => {
            if (v === value) preview.push(i + 1);
          });
          await scanAnimation(state.size, preview, 300);

          const res = await fetch(`${API_BASE}/delete/${encodeURIComponent(value)}`, {
            method: "DELETE",
          });

          if (!res.ok) {
            const errorData = await res.json();
            throw new Error(errorData.detail || "No se pudo eliminar");
          }

          const body = await res.json();
          await reload();

          showMessage(
            body.deleted_positions?.length
              ? `Eliminado en posiciones: ${body.deleted_positions.join(", ")}`
              : "No había ocurrencias para eliminar.",
            body.deleted_positions?.length ? "success" : "info"
          );
          valueEl.value = "";
        } catch (error) {
          showMessage(error.message, "error");
        }
      });
    }

    try {
      await reload();
    } catch (e) {
      console.info("[secuencial] Esperando creación de estructura…");
    }
  }

  window.initSimulator = initSecuencial;

  if (document.getElementById("create-structure")) {
    initSecuencial().catch((e) => console.error(e));
  }
})();
