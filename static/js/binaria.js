/* eslint-disable no-console */
/**
 * Búsqueda Binaria (frontend)
 * - Implementación completa en el frontend
 * - Incluye inserción, búsqueda y eliminación con animación
 */

(() => {
  "use strict";

  // Estado de la aplicación
  let state = {
    size: 0,
    digits: 0,
    data: [],
    animationSpeed: 800,
  };

  /**
   * Espera ms milisegundos.
   * @param {number} ms
   * @return {!Promise<void>}
   */
  function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  /**
   * Pad izquierda con ceros hasta `digits`.
   * @param {number|string} v
   * @param {number} digits
   * @return {string}
   */
  function toDigits(v, digits) {
    return String(v).padStart(digits, "0");
  }

  /**
   * Muestra mensaje temporal debajo del simulador.
   * @param {string} text
   * @param {'success'|'error'|'info'} type
   */
  function showMessage(text, type) {
    const el = document.getElementById("message");
    if (!el) return;

    el.textContent = text;
    el.className = `message ${type}`;
    el.style.display = "block";

    setTimeout(
      () => {
        if (el.textContent === text) {
          el.style.display = "none";
        }
      },
      type === "error" ? 3000 : 4000
    );
  }

  /**
   * Valida la entrada del valor según dígitos.
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
   * Renderiza la grilla con el estado actual.
   */
  function renderGrid() {
    const grid = document.getElementById("visualization");
    if (!grid) return;

    grid.innerHTML = "";

    for (let i = 0; i < state.size; i++) {
      const val = i < state.data.length ? state.data[i] : null;
      const cell = document.createElement("div");
      cell.className = `cell ${val === null ? "empty" : ""}`;

      const indexSpan = document.createElement("span");
      indexSpan.className = "cell-index";
      indexSpan.textContent = i + 1;

      const valueSpan = document.createElement("span");
      valueSpan.className = "cell-value";
      valueSpan.textContent = val === null ? "−" : toDigits(val, state.digits);

      cell.appendChild(indexSpan);
      cell.appendChild(valueSpan);
      grid.appendChild(cell);
    }
  }

  /**
   * Agrega un paso al contenedor de información del algoritmo.
   * @param {string} text
   * @param {boolean} isCurrent
   */
  function addAlgorithmStep(text, isCurrent = false) {
    const stepsContainer = document.getElementById("steps-container");
    if (!stepsContainer) return;

    const stepEl = document.createElement("div");
    stepEl.className = `step ${isCurrent ? "current-step" : ""}`;
    stepEl.textContent = text;
    stepsContainer.appendChild(stepEl);

    // Auto-scroll to the latest step
    stepsContainer.scrollTop = stepsContainer.scrollHeight;
  }

  /**
   * Realiza la búsqueda binaria con animación.
   * @param {number} target
   * @return {!Promise<number>} Índice del elemento encontrado o -1 si no se encuentra
   */
  async function binarySearchAnimation(target) {
    const grid = document.getElementById("visualization");
    if (!grid) return -1;

    const cells = grid.querySelectorAll(".cell");
    const stepsContainer = document.getElementById("steps-container");
    if (stepsContainer) stepsContainer.innerHTML = "";

    const algorithmInfo = document.getElementById("algorithm-info");
    if (algorithmInfo) algorithmInfo.style.display = "block";

    let low = 0;
    let high = state.data.length - 1;
    let step = 1;

    addAlgorithmStep(
      `Iniciando búsqueda binaria para el valor: ${toDigits(
        target,
        state.digits
      )}`,
      true
    );
    await sleep(state.animationSpeed);

    while (low <= high) {
      const mid = Math.floor((low + high) / 2);
      const midValue = state.data[mid];

      // Resaltar las celdas actuales
      cells.forEach((cell) => {
        cell.classList.remove("low", "mid", "high", "found");
      });

      if (low < cells.length) cells[low].classList.add("low");
      if (mid < cells.length) cells[mid].classList.add("mid");
      if (high < cells.length) cells[high].classList.add("high");

      addAlgorithmStep(
        `Paso ${step}: low=${low + 1}, mid=${mid + 1}, high=${high + 1}`,
        true
      );
      addAlgorithmStep(
        `Comparando ${toDigits(midValue, state.digits)} con ${toDigits(
          target,
          state.digits
        )}`
      );
      step++;

      await sleep(state.animationSpeed);

      if (midValue === target) {
        cells[mid].classList.remove("low", "mid", "high");
        cells[mid].classList.add("found");

        addAlgorithmStep(`¡Valor encontrado en la posición ${mid + 1}!`, true);
        return mid;
      } else if (midValue < target) {
        addAlgorithmStep(
          `${toDigits(midValue, state.digits)} < ${toDigits(
            target,
            state.digits
          )} → buscar en la mitad superior`
        );
        low = mid + 1;
      } else {
        addAlgorithmStep(
          `${toDigits(midValue, state.digits)} > ${toDigits(
            target,
            state.digits
          )} → buscar en la mitad inferior`
        );
        high = mid - 1;
      }

      await sleep(state.animationSpeed);
    }

    // No encontrado
    addAlgorithmStep(
      `Valor ${toDigits(target, state.digits)} no encontrado en el arreglo`,
      true
    );

    // Animación de no encontrado
    for (let i = 0; i < cells.length; i++) {
      cells[i].classList.add("not-found");
      await sleep(100);
    }

    await sleep(800);

    for (let i = 0; i < cells.length; i++) {
      cells[i].classList.remove("not-found");
    }

    return -1;
  }

  /**
   * Inicializa eventos y estado.
   */
  function initBinaria() {
    // Elementos del DOM
    const sizeEl = document.getElementById("size");
    const digitsEl = document.getElementById("digits");
    const createBtn = document.getElementById("create-structure");
    const actions = document.getElementById("actions-section");
    const valueEl = document.getElementById("value-input");
    const insertBtn = document.getElementById("insert-btn");
    const searchBtn = document.getElementById("search-btn");
    const deleteBtn = document.getElementById("delete-btn");
    const slowSpeedBtn = document.getElementById("slow-speed");
    const normalSpeedBtn = document.getElementById("normal-speed");
    const fastSpeedBtn = document.getElementById("fast-speed");

    if (!sizeEl || !digitsEl || !createBtn) {
      console.warn("[binaria] Faltan elementos del DOM para iniciar.");
      return;
    }

    /**
     * Actualiza la UI con el estado actual.
     */
    function updateUI() {
      renderGrid();

      // Ocultar mensaje informativo si hay estructura
      const infoMessage = document.getElementById("message");
      if (infoMessage && state.size > 0) {
        infoMessage.style.display = "none";
      }

      if (actions) actions.style.display = state.size > 0 ? "flex" : "none";
      if (valueEl && state.digits > 0) {
        valueEl.maxLength = state.digits;
        valueEl.placeholder = `Máx. ${state.digits} dígitos`;
      }
    }

    /**
     * Crea la estructura con el tamaño y dígitos especificados.
     */
    function createStructure() {
      const size = parseInt(sizeEl.value) || 10;
      const digits = parseInt(digitsEl.value) || 2;

      if (size <= 0 || digits <= 0) {
        showMessage("El tamaño y los dígitos deben ser mayores a 0", "error");
        return;
      }

      state.size = size;
      state.digits = digits;
      state.data = [];

      updateUI();
      showMessage(
        "Estructura creada. Ahora puedes insertar valores.",
        "success"
      );
    }

    /**
     * Inserta un valor manteniendo el orden.
     */
    function insertValue(value) {
      if (state.data.length >= state.size) {
        showMessage(
          "La estructura está llena. No se pueden insertar más valores.",
          "error"
        );
        return false;
      }

      // Convertir a número y validar
      const numValue = parseInt(value);
      if (isNaN(numValue)) {
        showMessage("El valor debe ser numérico", "error");
        return false;
      }

      // Validar longitud de dígitos
      if (value.length !== state.digits) {
        showMessage(
          `El valor debe tener exactamente ${state.digits} dígitos`,
          "error"
        );
        return false;
      }

      // Evitar duplicados
      if (state.data.includes(numValue)) {
        showMessage("El valor ya existe en la estructura", "error");
        return false;
      }

      // Insertar manteniendo el orden
      state.data.push(numValue);
      state.data.sort((a, b) => a - b);

      updateUI();
      showMessage(
        `Valor ${toDigits(numValue, state.digits)} insertado correctamente`,
        "success"
      );
      return true;
    }

    /**
     * Elimina un valor de la estructura.
     */
    function deleteValue(value) {
      const numValue = parseInt(value);
      if (isNaN(numValue)) {
        showMessage("El valor debe ser numérico", "error");
        return false;
      }

      const index = state.data.indexOf(numValue);
      if (index === -1) {
        showMessage("El valor no existe en la estructura", "error");
        return false;
      }

      state.data.splice(index, 1);
      updateUI();
      showMessage(
        `Valor ${toDigits(numValue, state.digits)} eliminado correctamente`,
        "success"
      );
      return true;
    }

    // Configurar eventos
    createBtn.addEventListener("click", createStructure);

    if (valueEl) {
      valueEl.addEventListener("input", () => {
        enforceNumericDigits(
          valueEl,
          state.digits || parseInt(digitsEl.value, 10) || 0
        );
      });
    }

    if (insertBtn && valueEl) {
      insertBtn.addEventListener("click", () => {
        if (state.size === 0) {
          showMessage("Primero crea la estructura", "error");
          return;
        }

        if (!valueEl.value) {
          showMessage("Ingresa un valor", "error");
          return;
        }

        insertValue(valueEl.value);
        valueEl.value = "";
      });
    }

    if (searchBtn && valueEl) {
      searchBtn.addEventListener("click", async () => {
        if (state.size === 0) {
          showMessage("Primero crea la estructura", "error");
          return;
        }

        if (state.data.length === 0) {
          showMessage("No hay valores en la estructura para buscar", "error");
          return;
        }

        if (!valueEl.value) {
          showMessage("Ingresa un valor", "error");
          return;
        }

        const numValue = parseInt(valueEl.value);
        if (isNaN(numValue)) {
          showMessage("El valor debe ser numérico", "error");
          return;
        }

        const foundIndex = await binarySearchAnimation(numValue);

        if (foundIndex !== -1) {
          showMessage(
            `Valor ${toDigits(
              numValue,
              state.digits
            )} encontrado en la posición ${foundIndex + 1}`,
            "success"
          );
        } else {
          showMessage(
            `Valor ${toDigits(numValue, state.digits)} no encontrado`,
            "error"
          );
        }
      });
    }

    if (deleteBtn && valueEl) {
      deleteBtn.addEventListener("click", () => {
        if (state.size === 0) {
          showMessage("Primero crea la estructura", "error");
          return;
        }

        if (!valueEl.value) {
          showMessage("Ingresa un valor", "error");
          return;
        }

        deleteValue(valueEl.value);
        valueEl.value = "";
      });
    }

    // Controles de velocidad
    if (slowSpeedBtn) {
      slowSpeedBtn.addEventListener("click", () => {
        state.animationSpeed = 1200;
        showMessage("Velocidad lenta activada", "info");
      });
    }

    if (normalSpeedBtn) {
      normalSpeedBtn.addEventListener("click", () => {
        state.animationSpeed = 800;
        showMessage("Velocidad normal activada", "info");
      });
    }

    if (fastSpeedBtn) {
      fastSpeedBtn.addEventListener("click", () => {
        state.animationSpeed = 400;
        showMessage("Velocidad rápida activada", "info");
      });
    }

    // Crear una estructura inicial al cargar
    setTimeout(createStructure, 500);
  }

  // Inicializar cuando el DOM esté listo
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initBinaria);
  } else {
    initBinaria();
  }
})();
