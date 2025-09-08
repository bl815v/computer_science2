(() => {
  "use strict";

  // Estado de la aplicación
  let state = {
    size: 0,
    digits: 0,
    table: [],
    animationSpeed: 800,
    hashFunction: "mod",
    rangeOption: "user",
    collisionResolution: "lineal",
    isPrimeSize: false,
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
   * Comprueba si un número es primo
   * @param {number} num
   * @return {boolean}
   */
  function isPrime(num) {
    if (num <= 1) return false;
    if (num <= 3) return true;

    if (num % 2 === 0 || num % 3 === 0) return false;

    for (let i = 5; i * i <= num; i += 6) {
      if (num % i === 0 || num % (i + 2) === 0) return false;
    }

    return true;
  }

  /**
   * Encuentra el número primo mayor más cercano
   * @param {number} num
   * @return {number}
   */
  function findLargerPrime(num) {
    let candidate = num;
    while (true) {
      if (isPrime(candidate)) return candidate;
      candidate++;
    }
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
   * Renderiza la tabla hash con el estado actual.
   */
  function renderTable() {
    const grid = document.getElementById("visualization");
    if (!grid) return;

    grid.innerHTML = "";

    for (let i = 0; i < state.size; i++) {
      const cell = document.createElement("div");
      cell.className = "cell";

      const indexSpan = document.createElement("span");
      indexSpan.className = "cell-index";
      indexSpan.textContent = i + 1;

      const valueContainer = document.createElement("div");
      valueContainer.className = "cell-value";

      // Para encadenamiento, mostramos una lista
      if (state.collisionResolution === "encadenamiento") {
        if (!state.table[i] || state.table[i].length === 0) {
          valueContainer.textContent = "−";
          cell.classList.add("empty");
        } else {
          state.table[i].forEach((value) => {
            const valueSpan = document.createElement("span");
            valueSpan.className = "chain-item";
            valueSpan.textContent = toDigits(value, state.digits);
            valueContainer.appendChild(valueSpan);
          });
        }
      }
      // Para arreglos anidados
      else if (state.collisionResolution === "anidados") {
        if (!state.table[i] || state.table[i].length === 0) {
          valueContainer.textContent = "−";
          cell.classList.add("empty");
        } else {
          // Mostrar todos los valores del slot anidado
          state.table[i].forEach((value, idx) => {
            if (value !== null) {
              const valueSpan = document.createElement("span");
              valueSpan.className = "chain-item";
              valueSpan.textContent = toDigits(value, state.digits);
              valueContainer.appendChild(valueSpan);
            }
          });
        }
      }
      // Para otros métodos
      else {
        if (state.table[i] === null || state.table[i] === undefined) {
          valueContainer.textContent = "−";
          cell.classList.add("empty");
        } else {
          valueContainer.textContent = toDigits(state.table[i], state.digits);
        }
      }

      cell.appendChild(indexSpan);
      cell.appendChild(valueContainer);
      grid.appendChild(cell);
    }
  }

  /**
   * Aplica la función hash seleccionada a un valor
   * @param {number} value
   * @return {number}
   */
  function applyHashFunction(value) {
    const tableSize = state.size;

    switch (state.hashFunction) {
      case "mod":
        return value % tableSize;

      case "cuadrado":
        const squared = value * value;
        // Tomar los dígitos del medio
        const squaredStr = squared.toString();
        const mid = Math.floor(squaredStr.length / 2) - 1;
        const digits = squaredStr.substring(mid, mid + 2);
        return parseInt(digits) % tableSize;

      case "truncamiento":
        // Truncar a dos dígitos y aplicar módulo
        const truncated = parseInt(value.toString().substring(0, 2));
        return truncated % tableSize;

      case "plegamiento":
        // Dividir en partes y sumarlas
        const valueStr = value.toString().padStart(state.digits, "0");
        let sum = 0;
        for (let i = 0; i < valueStr.length; i += 2) {
          const part = valueStr.substring(i, i + 2);
          sum += parseInt(part);
        }
        return sum % tableSize;

      default:
        return value % tableSize;
    }
  }

  /**
   * Resuelve colisiones según el método seleccionado
   * @param {number} index
   * @param {number} value
   * @param {string} operation - 'insert' o 'search'
   * @return {number}
   */
  function resolveCollision(index, value, operation = "insert") {
    const tableSize = state.size;

    switch (state.collisionResolution) {
      case "lineal":
        let linearIndex = index;
        for (let i = 1; i < tableSize; i++) {
          linearIndex = (index + i) % tableSize;

          if (
            operation === "insert" &&
            (state.table[linearIndex] === null ||
              state.table[linearIndex] === undefined)
          ) {
            return linearIndex;
          }

          if (operation === "search" && state.table[linearIndex] === value) {
            return linearIndex;
          }

          if (
            operation === "search" &&
            (state.table[linearIndex] === null ||
              state.table[linearIndex] === undefined)
          ) {
            return -1; // No encontrado
          }
        }
        return -1; // Tabla llena o no encontrado

      case "cuadratica":
        let quadraticIndex = index;
        for (let i = 1; i < tableSize; i++) {
          quadraticIndex = (index + i * i) % tableSize;

          if (
            operation === "insert" &&
            (state.table[quadraticIndex] === null ||
              state.table[quadraticIndex] === undefined)
          ) {
            return quadraticIndex;
          }

          if (operation === "search" && state.table[quadraticIndex] === value) {
            return quadraticIndex;
          }

          if (
            operation === "search" &&
            (state.table[quadraticIndex] === null ||
              state.table[quadraticIndex] === undefined)
          ) {
            return -1;
          }
        }
        return -1;

      case "doble":
        // Segunda función hash
        const secondHash = (value % (tableSize - 1)) + 1;
        let doubleIndex = index;
        for (let i = 1; i < tableSize; i++) {
          doubleIndex = (index + i * secondHash) % tableSize;

          if (
            operation === "insert" &&
            (state.table[doubleIndex] === null ||
              state.table[doubleIndex] === undefined)
          ) {
            return doubleIndex;
          }

          if (operation === "search" && state.table[doubleIndex] === value) {
            return doubleIndex;
          }

          if (
            operation === "search" &&
            (state.table[doubleIndex] === null ||
              state.table[doubleIndex] === undefined)
          ) {
            return -1;
          }
        }
        return -1;

      case "anidados":
        // Para arreglos anidados, siempre devolvemos el índice original
        // La gestión se hace en las operaciones de inserción/búsqueda
        return index;

      case "encadenamiento":
        // Para encadenamiento, siempre devolvemos el índice original
        return index;

      default:
        return index;
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
   * Realiza la inserción con animación.
   * @param {number} value
   * @return {!Promise<boolean>} True si se insertó correctamente
   */
  async function insertValueAnimation(value) {
    const grid = document.getElementById("visualization");
    if (!grid) return false;

    const cells = grid.querySelectorAll(".cell");
    const stepsContainer = document.getElementById("steps-container");
    if (stepsContainer) stepsContainer.innerHTML = "";

    const algorithmInfo = document.getElementById("algorithm-info");
    if (algorithmInfo) algorithmInfo.style.display = "block";

    addAlgorithmStep(
      `Iniciando inserción del valor: ${toDigits(value, state.digits)}`,
      true
    );
    await sleep(state.animationSpeed);

    // Calcular hash inicial
    let index = applyHashFunction(value);
    addAlgorithmStep(
      `Aplicando función hash (${state.hashFunction}): índice calculado = ${
        index + 1
      }`,
      true
    );

    // Resaltar la celda del índice calculado
    if (index < cells.length) {
      cells[index].classList.add("searched");
    }
    await sleep(state.animationSpeed);

    // Para encadenamiento o arreglos anidados
    if (
      state.collisionResolution === "encadenamiento" ||
      state.collisionResolution === "anidados"
    ) {
      if (state.table[index] === null || state.table[index] === undefined) {
        // Inicializar la lista si es necesario
        if (state.collisionResolution === "encadenamiento") {
          state.table[index] = [];
        } else {
          // Para arreglos anidados, creamos un array de tamaño fijo (3)
          state.table[index] = Array(3).fill(null);
        }
      }

      if (state.collisionResolution === "encadenamiento") {
        // Verificar si el valor ya existe
        if (state.table[index].includes(value)) {
          addAlgorithmStep(
            `El valor ${toDigits(
              value,
              state.digits
            )} ya existe en la lista de colisiones.`,
            true
          );
          if (index < cells.length) {
            cells[index].classList.remove("searched");
            cells[index].classList.add("collision");
            await sleep(state.animationSpeed);
            cells[index].classList.remove("collision");
          }
          return false;
        }

        state.table[index].push(value);
        renderTable(); // Renderizar inmediatamente

        addAlgorithmStep(
          `Insertando en la lista de colisiones en índice ${index + 1}.`,
          true
        );

        // Obtener referencia a las celdas actualizadas
        const currentCells = document
          .getElementById("visualization")
          .querySelectorAll(".cell");
        if (index < currentCells.length) {
          currentCells[index].classList.add("collision");
          await sleep(state.animationSpeed);
          currentCells[index].classList.remove("collision");
        }

        return true;
      } else {
        // Arreglos anidados - buscar un hueco
        for (let i = 0; i < state.table[index].length; i++) {
          if (state.table[index][i] === null) {
            state.table[index][i] = value;
            addAlgorithmStep(
              `Insertando en sub-índice ${i + 1} del arreglo anidado en índice ${index + 1}.`,
              true
            );

            if (index < cells.length) {
              cells[index].classList.remove("searched");
              cells[index].classList.add("collision");
              await sleep(state.animationSpeed);
            }

            renderTable();
            return true;
          }
        }

        addAlgorithmStep(
          `El arreglo anidado en índice ${index} está lleno. No se puede insertar.`,
          true
        );
        if (index < cells.length) {
          cells[index].classList.remove("searched");
          cells[index].classList.add("collision");
          await sleep(state.animationSpeed);
          cells[index].classList.remove("collision");
        }
        return false;
      }
    }

    // Para otros métodos de resolución de colisiones
    if (state.table[index] === null || state.table[index] === undefined) {
      state.table[index] = value;
      renderTable(); // Renderizar inmediatamente después de cambiar el estado

      addAlgorithmStep(`Insertando en índice ${index + 1}.`, true);

      // Obtener referencia a las celdas actualizadas
      const currentCells = document
        .getElementById("visualization")
        .querySelectorAll(".cell");
      if (index < currentCells.length) {
        currentCells[index].classList.add("found");
        await sleep(state.animationSpeed);
        currentCells[index].classList.remove("found");
      }

      return true;
    } else {
      addAlgorithmStep(
        `Colisión en índice ${index+1}. Aplicando resolución ${state.collisionResolution}.`,
        true
      );

      if (index < cells.length) {
        cells[index].classList.remove("searched");
        cells[index].classList.add("collision");
        await sleep(state.animationSpeed);
      }

      const newIndex = resolveCollision(index, value, "insert");

      if (newIndex === -1) {
        addAlgorithmStep(
          `No se encontró espacio disponible en la tabla.`,
          true
        );
        return false;
      }

      state.table[newIndex] = value;
      renderTable(); // Renderizar inmediatamente después de cambiar el estado

      addAlgorithmStep(`Nuevo índice calculado: ${newIndex + 1}.`, true);

      // Obtener referencia a las celdas actualizadas
      const currentCells = document
        .getElementById("visualization")
        .querySelectorAll(".cell");
      if (newIndex < currentCells.length) {
        currentCells[newIndex].classList.add("found");
        await sleep(state.animationSpeed);
        currentCells[newIndex].classList.remove("found");
      }

      return true;
    }
  }

  /**
   * Realiza la búsqueda con animación.
   * @param {number} value
   * @return {!Promise<number>} Índice del elemento encontrado o -1 si no se encuentra
   */
  async function searchValueAnimation(value) {
    const grid = document.getElementById("visualization");
    if (!grid) return -1;

    const cells = grid.querySelectorAll(".cell");
    const stepsContainer = document.getElementById("steps-container");
    if (stepsContainer) stepsContainer.innerHTML = "";

    const algorithmInfo = document.getElementById("algorithm-info");
    if (algorithmInfo) algorithmInfo.style.display = "block";

    addAlgorithmStep(
      `Iniciando búsqueda del valor: ${toDigits(value, state.digits)}`,
      true
    );
    await sleep(state.animationSpeed);

    // Calcular hash inicial
    let index = applyHashFunction(value);
    addAlgorithmStep(
      `Aplicando función hash (${state.hashFunction}): índice calculado = ${index + 1}`,
      true
    );

    // Resaltar la celda del índice calculado
    if (index < cells.length) {
      cells[index].classList.add("searched");
    }
    await sleep(state.animationSpeed);

    // Para encadenamiento
    if (state.collisionResolution === "encadenamiento") {
      if (state.table[index] && state.table[index].includes(value)) {
        addAlgorithmStep(
          `Valor encontrado en la lista de colisiones del índice ${index + 1}.`,
          true
        );

        if (index < cells.length) {
          cells[index].classList.remove("searched");
          cells[index].classList.add("found");
          await sleep(state.animationSpeed);
        }

        return index;
      } else {
        addAlgorithmStep(
          `Valor no encontrado en la lista de colisiones del índice ${index}.`,
          true
        );

        if (index < cells.length) {
          cells[index].classList.remove("searched");
          await sleep(state.animationSpeed);
        }

        return -1;
      }
    }

    // Para arreglos anidados
    if (state.collisionResolution === "anidados") {
      if (state.table[index]) {
        for (let i = 0; i < state.table[index].length; i++) {
          if (state.table[index][i] === value) {
            addAlgorithmStep(
              `Valor encontrado en sub-índice ${i + 1} del arreglo anidado en índice ${index + 1}.`,
              true
            );

            if (index < cells.length) {
              cells[index].classList.remove("searched");
              cells[index].classList.add("found");
              await sleep(state.animationSpeed);
            }

            return index;
          }
        }
      }

      addAlgorithmStep(
        `Valor no encontrado en el arreglo anidado del índice ${index}.`,
        true
      );

      if (index < cells.length) {
        cells[index].classList.remove("searched");
        await sleep(state.animationSpeed);
      }

      return -1;
    }

    // Para otros métodos de resolución de colisiones
    if (state.table[index] === value) {
      addAlgorithmStep(`Valor encontrado en índice ${index + 1}.`, true);

      if (index < cells.length) {
        cells[index].classList.remove("searched");
        cells[index].classList.add("found");
        await sleep(state.animationSpeed);
      }

      return index;
    } else if (
      state.table[index] === null ||
      state.table[index] === undefined
    ) {
      addAlgorithmStep(
        `Celda vacía en índice ${index}. Valor no encontrado.`,
        true
      );

      if (index < cells.length) {
        cells[index].classList.remove("searched");
        await sleep(state.animationSpeed);
      }

      return -1;
    } else {
      addAlgorithmStep(
        `Valor diferente en índice ${index}. Aplicando resolución ${state.collisionResolution}.`,
        true
      );

      if (index < cells.length) {
        cells[index].classList.remove("searched");
        cells[index].classList.add("collision");
        await sleep(state.animationSpeed);
      }

      const newIndex = resolveCollision(index, value, "search");

      if (newIndex === -1) {
        addAlgorithmStep(`Valor no encontrado en la tabla.`, true);
        return -1;
      }

      addAlgorithmStep(`Valor encontrado en índice ${newIndex + 1}.`, true);

      if (newIndex < cells.length) {
        cells[newIndex].classList.add("found");
        await sleep(state.animationSpeed);
      }

      return newIndex;
    }
  }

  /**
   * Realiza la eliminación con animación.
   * @param {number} value
   * @return {!Promise<boolean>} True si se eliminó correctamente
   */
  async function deleteValueAnimation(value) {
    const index = await searchValueAnimation(value);

    if (index === -1) {
      addAlgorithmStep(`No se puede eliminar: valor no encontrado.`, true);
      return false;
    }

    // Para encadenamiento
    if (state.collisionResolution === "encadenamiento") {
      const valueIndex = state.table[index].indexOf(value);
      if (valueIndex !== -1) {
        state.table[index].splice(valueIndex, 1);
        addAlgorithmStep(
          `Valor eliminado de la lista de colisiones en índice ${index + 1}.`,
          true
        );
        renderTable();
        return true;
      }
      return false;
    }

    // Para arreglos anidados
    if (state.collisionResolution === "anidados") {
      for (let i = 0; i < state.table[index].length; i++) {
        if (state.table[index][i] === value) {
          state.table[index][i] = null;
          addAlgorithmStep(
            `Valor eliminado del sub-índice ${i + 1} en índice ${index + 1}.`,
            true
          );
          renderTable();
          return true;
        }
      }
      return false;
    }

    // Para otros métodos
    state.table[index] = null;
    addAlgorithmStep(`Valor eliminado del índice ${index + 1}.`, true);
    renderTable();
    return true;
  }

  /**
   * Inicializa eventos y estado.
   */
  function initHashing() {
    // Elementos del DOM
    const sizeEl = document.getElementById("size");
    const digitsEl = document.getElementById("digits");
    const createBtn = document.getElementById("create-structure");
    const hashFunctionEl = document.getElementById("hash-function");
    const rangeOptionEl = document.getElementById("range-option");
    const collisionResolutionEl = document.getElementById(
      "collision-resolution"
    );
    const actions = document.getElementById("actions-section");
    const valueEl = document.getElementById("value-input");
    const insertBtn = document.getElementById("insert-btn");
    const searchBtn = document.getElementById("search-btn");
    const deleteBtn = document.getElementById("delete-btn");
    const slowSpeedBtn = document.getElementById("slow-speed");
    const normalSpeedBtn = document.getElementById("normal-speed");
    const fastSpeedBtn = document.getElementById("fast-speed");

    if (!sizeEl || !digitsEl || !createBtn) {
      console.warn("[hashing] Faltan elementos del DOM para iniciar.");
      return;
    }

    /**
     * Actualiza la UI con el estado actual.
     */
    function updateUI() {
      renderTable();

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
     * Crea la tabla hash con el tamaño y dígitos especificados.
     */
    function createHashTable() {
      let size = parseInt(sizeEl.value) || 10;
      const digits = parseInt(digitsEl.value) || 2;

      if (size <= 0 || digits <= 0) {
        showMessage("El tamaño y los dígitos deben ser mayores a 0", "error");
        return;
      }

      // Aplicar opción de rango (primo mayor si está seleccionado)
      if (state.rangeOption === "prime") {
        size = findLargerPrime(size);
        sizeEl.value = size;
        state.isPrimeSize = true;
      } else {
        state.isPrimeSize = false;
      }

      state.size = size;
      state.digits = digits;
      state.table = Array(size).fill(null);

      // Actualizar métodos de hashing y colisión
      state.hashFunction = hashFunctionEl.value;
      state.rangeOption = rangeOptionEl.value;
      state.collisionResolution = collisionResolutionEl.value;

      updateUI();
      showMessage(
        `Tabla hash de tamaño ${size} creada. Ahora puedes insertar valores.`,
        "success"
      );
    }

    // Configurar eventos
    createBtn.addEventListener("click", createHashTable);

    hashFunctionEl.addEventListener("change", () => {
      state.hashFunction = hashFunctionEl.value;
    });

    rangeOptionEl.addEventListener("change", () => {
      state.rangeOption = rangeOptionEl.value;
    });

    collisionResolutionEl.addEventListener("change", () => {
      state.collisionResolution = collisionResolutionEl.value;
      if (state.size > 0) {
        // Reinicializar la tabla con el nuevo método
        state.table = Array(state.size).fill(null);
        updateUI();
      }
    });

    if (valueEl) {
      valueEl.addEventListener("input", () => {
        enforceNumericDigits(
          valueEl,
          state.digits || parseInt(digitsEl.value, 10) || 0
        );
      });
    }

    if (insertBtn && valueEl) {
      insertBtn.addEventListener("click", async () => {
        if (state.size === 0) {
          showMessage("Primero crea la tabla hash", "error");
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

        if (valueEl.value.length !== state.digits) {
          showMessage(
            `El valor debe tener exactamente ${state.digits} dígitos`,
            "error"
          );
          return;
        }

        const success = await insertValueAnimation(numValue);

        if (success) {
          showMessage(
            `Valor ${toDigits(numValue, state.digits)} insertado correctamente`,
            "success"
          );
        } else {
          showMessage(
            `No se pudo insertar el valor ${toDigits(numValue, state.digits)}`,
            "error"
          );
        }
      });
    }

    if (searchBtn && valueEl) {
      searchBtn.addEventListener("click", async () => {
        if (state.size === 0) {
          showMessage("Primero crea la tabla hash", "error");
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

        const foundIndex = await searchValueAnimation(numValue);

        if (foundIndex !== -1) {
          showMessage(
            `Valor ${toDigits(
              numValue,
              state.digits
            )} encontrado en la posición ${foundIndex}`,
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
      deleteBtn.addEventListener("click", async () => {
        if (state.size === 0) {
          showMessage("Primero crea la tabla hash", "error");
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

        const success = await deleteValueAnimation(numValue);

        if (success) {
          showMessage(
            `Valor ${toDigits(numValue, state.digits)} eliminado correctamente`,
            "success"
          );
        } else {
          showMessage(
            `No se pudo eliminar el valor ${toDigits(numValue, state.digits)}`,
            "error"
          );
        }
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
  }

  // Inicializar cuando el DOM esté listo
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initHashing);
  } else {
    initHashing();
  }
})();
