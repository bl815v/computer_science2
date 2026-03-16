/* eslint-disable no-console */
(() => {
  "use strict";

  const API_BASE = "http://127.0.0.1:8000/external/binary";
  let isNotifying = false;
  let currentState = { size: 0, digits: 0, block_size: 0, blocks: [] };

  function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  function toDigits(v, digits) {
    if (v === null || v === undefined || v === "") return "";
    return String(v).padStart(digits, "0");
  }

  function clearInput() {
    const inp = document.getElementById("value-input");
    if (inp) {
      inp.value = "";
      inp.focus();
    }
  }

  function enforceNumericDigits(input, digits) {
    const originalValue = input.value;
    const numericValue = originalValue.replace(/\D+/g, "");
    if (digits > 0 && numericValue.length > digits) {
      input.value = numericValue.slice(0, digits);
      if (!isNotifying) {
        isNotifying = true;
        notifyError(`La clave solo puede tener ${digits} dígitos.`);
        setTimeout(() => { isNotifying = false; }, 1500);
      }
    } else {
      input.value = numericValue;
    }
  }

  function validateKey(val) {
    if (!val) {
      notifyError("Ingresa una clave.");
      clearInput();
      return false;
    }
    if (val.length !== currentState.digits) {
      notifyError(`La clave debe tener exactamente ${currentState.digits} dígitos.`);
      clearInput();
      return false;
    }
    return true;
  }

  function renderGrid() {
    const container = document.getElementById("visualization");
    if (!container) return;
    container.innerHTML = "";

    if (!currentState.blocks || currentState.blocks.length === 0) {
      const msg = document.createElement("p");
      msg.className = "empty-message";
      msg.textContent = "Crea una estructura para visualizar los bloques.";
      container.appendChild(msg);
      return;
    }

    currentState.blocks.forEach((block, bIdx) => {
      const blockDiv = document.createElement("div");
      blockDiv.className = "block";
      blockDiv.dataset.block = bIdx + 1;

      const blockHeader = document.createElement("div");
      blockHeader.className = "block-header";
      blockHeader.textContent = `Bloque ${bIdx + 1}`;
      blockDiv.appendChild(blockHeader);

      const cellsDiv = document.createElement("div");
      cellsDiv.className = "block-cells";

      block.forEach((val, pos) => {
        const cell = document.createElement("div");
        cell.className = "cell";
        cell.dataset.block = bIdx + 1;
        cell.dataset.pos = pos + 1;
        cell.dataset.index = `${bIdx + 1}.${pos + 1}`;

        if (val !== null && val !== undefined && val !== "") {
          cell.textContent = toDigits(val, currentState.digits);
        } else {
          cell.classList.add("empty");
          cell.textContent = "";
        }
        cellsDiv.appendChild(cell);
      });

      blockDiv.appendChild(cellsDiv);
      container.appendChild(blockDiv);
    });
  }

  function highlightCells(positions, className, duration = 1500) {
    if (!positions || positions.length === 0) return;
    const container = document.getElementById("visualization");
    positions.forEach(({ block, cell }) => {
      const cellElement = container.querySelector(`.cell[data-block="${block}"][data-pos="${cell}"]`);
      if (cellElement) {
        cellElement.classList.add(className);
        setTimeout(() => cellElement.classList.remove(className), duration);
      }
    });
  }

  // --- Animación de búsqueda externa binaria (dos niveles) ---
  // Retorna la posición encontrada { block, cell } o null si no se encuentra.
  // Opciones:
  //   autoClear (bool): si true, limpia los resaltados tras 2 segundos.
  //   resultClass (string): clase a aplicar a la celda encontrada (por defecto 'found').
  async function binaryExternalSearchAnimation(targetValue, options = { autoClear: true, resultClass: 'found' }) {
    const container = document.getElementById("visualization");
    if (!container) return null;

    // Limpiar clases previas
    const allCells = container.querySelectorAll(".cell");
    const allBlocks = container.querySelectorAll(".block");
    allCells.forEach(c => c.classList.remove("active", "found", "discarded", "highlight-delete"));
    allBlocks.forEach(b => b.classList.remove("block-active", "block-discarded", "block-candidate"));

    // Obtener los máximos de cada bloque (último valor no nulo)
    const blockMaxValues = [];
    for (let b = 0; b < currentState.blocks.length; b++) {
      const block = currentState.blocks[b];
      let maxVal = null;
      for (let i = block.length - 1; i >= 0; i--) {
        if (block[i] !== null && block[i] !== undefined && block[i] !== "") {
          maxVal = block[i];
          break;
        }
      }
      blockMaxValues.push(maxVal);
    }

    // 1. Búsqueda binaria sobre los bloques
    let leftBlock = 0;
    let rightBlock = currentState.blocks.length - 1;

    while (leftBlock < rightBlock) {
      let midBlock = Math.floor((leftBlock + rightBlock) / 2);

      // Resaltar el bloque actual
      const blockElement = container.querySelector(`.block[data-block="${midBlock + 1}"]`);
      if (blockElement) {
        blockElement.classList.add("block-active");
      }
      await sleep(600);

      const maxVal = blockMaxValues[midBlock];

      if (maxVal === null) {
        // Bloque vacío: todos a la derecha también vacíos
        for (let i = midBlock; i <= rightBlock; i++) {
          const bElem = container.querySelector(`.block[data-block="${i + 1}"]`);
          if (bElem) bElem.classList.add("block-discarded");
        }
        rightBlock = midBlock - 1;
      } else {
        if (targetValue <= maxVal) {
          // Descartar bloques a la derecha
          for (let i = midBlock + 1; i <= rightBlock; i++) {
            const bElem = container.querySelector(`.block[data-block="${i + 1}"]`);
            if (bElem) bElem.classList.add("block-discarded");
          }
          rightBlock = midBlock;
        } else {
          // Descartar este bloque y los de la izquierda
          for (let i = leftBlock; i <= midBlock; i++) {
            const bElem = container.querySelector(`.block[data-block="${i + 1}"]`);
            if (bElem) bElem.classList.add("block-discarded");
          }
          leftBlock = midBlock + 1;
        }
      }

      // Quitar resaltado del bloque actual
      if (blockElement) {
        blockElement.classList.remove("block-active");
      }
      await sleep(400);
    }

    // Después del bucle, leftBlock es el índice candidato
    if (leftBlock < 0 || leftBlock >= currentState.blocks.length) {
      if (options.autoClear) {
        // Limpiar todo (por si acaso)
        allBlocks.forEach(b => b.classList.remove("block-discarded", "block-candidate"));
      }
      notifyError(`Clave ${targetValue} no encontrada.`);
      return null;
    }
    const candidateBlock = leftBlock;

    // Verificar si el bloque candidato podría contener el valor
    const maxValCandidate = blockMaxValues[candidateBlock];
    if (maxValCandidate === null || targetValue > maxValCandidate) {
      if (options.autoClear) {
        allBlocks.forEach(b => b.classList.remove("block-discarded", "block-candidate"));
      }
      notifyError(`Clave ${targetValue} no encontrada.`);
      return null;
    }

    // Resaltar el bloque candidato
    const candidateBlockElem = container.querySelector(`.block[data-block="${candidateBlock + 1}"]`);
    if (candidateBlockElem) {
      candidateBlockElem.classList.add("block-candidate");
    }

    // 2. Búsqueda binaria dentro del bloque candidato
    const blockData = currentState.blocks[candidateBlock];
    const blockCells = container.querySelectorAll(`.block[data-block="${candidateBlock + 1}"] .cell`);

    let leftCell = 0;
    let rightCell = blockData.length - 1;
    let found = false;
    let foundPos = null;

    while (leftCell <= rightCell) {
      let midCell = Math.floor((leftCell + rightCell) / 2);
      let cell = blockCells[midCell];

      cell.classList.add("active");
      await sleep(600);

      const cellValue = blockData[midCell];

      if (cellValue !== null && cellValue !== undefined && cellValue !== "" && cellValue === targetValue) {
        cell.classList.remove("active");
        cell.classList.add(options.resultClass); // Usar la clase especificada
        found = true;
        foundPos = { block: candidateBlock + 1, cell: midCell + 1 };
        break;
      }

      cell.classList.remove("active");

      // Lógica corregida para celdas vacías: las vacías son mayores que cualquier valor
      if (cellValue === null || cellValue === "") {
        // Celda vacía → descartar derecha (los valores están a la izquierda)
        for (let i = midCell; i <= rightCell; i++) {
          blockCells[i].classList.add("discarded");
        }
        rightCell = midCell - 1;
      } else if (cellValue < targetValue) {
        // Descartar izquierda
        for (let i = leftCell; i <= midCell; i++) {
          blockCells[i].classList.add("discarded");
        }
        leftCell = midCell + 1;
      } else {
        // cellValue > targetValue
        for (let i = midCell; i <= rightCell; i++) {
          blockCells[i].classList.add("discarded");
        }
        rightCell = midCell - 1;
      }
      await sleep(400);
    }

    if (found) {
      if (options.autoClear) {
        await sleep(2000);
        allCells.forEach(c => c.classList.remove("active", "found", "discarded", "highlight-delete"));
        allBlocks.forEach(b => b.classList.remove("block-active", "block-discarded", "block-candidate"));
      }
      return foundPos;
    } else {
      // No encontrado: limpiar todo y notificar
      allCells.forEach(c => c.classList.remove("active", "found", "discarded", "highlight-delete"));
      allBlocks.forEach(b => b.classList.remove("block-active", "block-discarded", "block-candidate"));
      notifyError(`Clave ${targetValue} no encontrada.`);
      return null;
    }
  }

  async function loadState() {
    try {
      const res = await fetch(`${API_BASE}/state`);
      if (res.status === 404) {
        console.log("No hay estructura previa (404)");
        currentState = { size: 0, digits: 0, block_size: 0, blocks: [] };
        renderGrid();
        return;
      }
      if (!res.ok) throw new Error("Error al cargar estado");
      const data = await res.json();
      console.log("Estado cargado:", data);
      currentState = {
        size: data.size || 0,
        digits: data.digits || 0,
        block_size: data.block_size || data.blockSize || 0,
        blocks: data.blocks || []
      };
      const blockSizeSpan = document.getElementById("block-size-display");
      if (blockSizeSpan) blockSizeSpan.textContent = currentState.block_size || "-";
      renderGrid();
    } catch (err) {
      console.error("Error en loadState:", err);
      currentState = { size: 0, digits: 0, block_size: 0, blocks: [] };
      renderGrid();
    }
  }

  async function initSimulator() {
    const totalSizeInput = document.getElementById("total-size");
    const digitsInput = document.getElementById("digits");
    const createBtn = document.getElementById("create-structure");
    const actionsSection = document.getElementById("actions-section");
    const valueInput = document.getElementById("value-input");
    const insertBtn = document.getElementById("insert-btn");
    const searchBtn = document.getElementById("search-btn");
    const deleteBtn = document.getElementById("delete-btn");
    const blockSizeSpan = document.getElementById("block-size-display");

    if (!createBtn) return;

    actionsSection.style.display = "none";
    currentState = { size: 0, digits: 0, block_size: 0, blocks: [] };
    renderGrid();

    const updateBlockSizePreview = () => {
      const size = parseInt(totalSizeInput.value);
      if (!isNaN(size) && size > 0) {
        const bs = Math.floor(Math.sqrt(size));
        blockSizeSpan.textContent = bs;
      } else {
        blockSizeSpan.textContent = "-";
      }
    };
    totalSizeInput.addEventListener("input", updateBlockSizePreview);
    updateBlockSizePreview();

    createBtn.addEventListener("click", async () => {
      const size = parseInt(totalSizeInput.value);
      const digits = parseInt(digitsInput.value);

      if (isNaN(size) || size <= 0) return notifyError("Capacidad inválida.");
      if (isNaN(digits) || digits <= 0) return notifyError("Dígitos inválidos.");

      try {
        const res = await fetch(`${API_BASE}/create`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ size, digits })
        });
        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.detail || "Error al crear");
        }
        await loadState();
        actionsSection.style.display = "block";
        notifySuccess("Estructura creada correctamente.");
        valueInput.placeholder = `Máx: ${digits} dígitos`;
      } catch (err) {
        notifyError(err.message);
      }
    });

    if (valueInput) {
      valueInput.addEventListener("input", () => {
        const digits = currentState.digits || parseInt(digitsInput.value) || 0;
        enforceNumericDigits(valueInput, digits);
      });
    }

    // ---- INSERTAR ----
    insertBtn.addEventListener("click", async () => {
      const rawValue = valueInput.value.trim();
      if (!rawValue) { notifyError("Ingresa una clave."); clearInput(); return; }
      const value = toDigits(rawValue, currentState.digits);
      if (!validateKey(value)) return;

      try {
        const res = await fetch(`${API_BASE}/insert`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ value })
        });

        let data;
        const contentType = res.headers.get("content-type");
        if (contentType && contentType.includes("application/json")) {
          data = await res.json();
        } else {
          data = { detail: await res.text() };
        }
        console.log("Respuesta insert:", res.status, data);

        if (res.ok) {
          if (data.position && Array.isArray(data.position) && data.position.length > 0) {
            await loadState();
            const posInfo = data.position[0];
            if (posInfo.block_index !== undefined && posInfo.block_position !== undefined) {
              const block = posInfo.block_index;
              const cell = posInfo.block_position;
              notifySuccess(`Clave ${value} insertada en bloque ${block}, posición ${cell}`);
              highlightCells([{ block, cell }], 'highlight-insert');
            } else {
              notifySuccess(`Clave ${value} insertada.`);
            }
          } else {
            notifySuccess(`Clave ${value} insertada.`);
          }
          clearInput();
        } else {
          let errorMsg = data.detail || data.message || `Error ${res.status}: ${res.statusText}`;
          if (res.status === 500) {
            errorMsg = "Error interno del servidor. Es posible que la clave ya exista o haya un problema en el backend.";
          }
          notifyError(errorMsg);
          clearInput();
        }
      } catch (err) {
        console.error("Error en inserción (catch):", err);
        notifyError("Error de conexión al insertar.");
        clearInput();
      }
    });

    // ---- BUSCAR CON ANIMACIÓN (autoClear true, resultado en verde) ----
    searchBtn.addEventListener("click", async () => {
      const rawValue = valueInput.value.trim();
      if (!rawValue) { notifyError("Ingresa una clave."); clearInput(); return; }
      const value = toDigits(rawValue, currentState.digits);
      if (!validateKey(value)) return;

      const foundPos = await binaryExternalSearchAnimation(value, { autoClear: true, resultClass: 'found' });
      if (foundPos) {
        // La animación ya muestra el mensaje de encontrado? No, la animación no muestra éxito, solo retorna la posición.
        // Añadimos el mensaje aquí.
        notifySuccess(`Clave ${value} encontrada en bloque ${foundPos.block}, posición ${foundPos.cell}`);
      } else {
        // La animación ya mostró error
      }
      clearInput();
    });

    // ---- ELIMINAR CON ANIMACIÓN PREVIA (resultado en rojo) ----
    deleteBtn.addEventListener("click", async () => {
      const rawValue = valueInput.value.trim();
      if (!rawValue) { notifyError("Ingresa una clave."); clearInput(); return; }
      const value = toDigits(rawValue, currentState.digits);
      if (!validateKey(value)) return;

      // Primero realizar la animación de búsqueda sin autoClear y con resultado en rojo
      const foundPos = await binaryExternalSearchAnimation(value, { autoClear: false, resultClass: 'highlight-delete' });

      if (!foundPos) {
        // La animación ya mostró mensaje de no encontrado
        clearInput();
        return;
      }

      // Mensaje de encontrado (opcional, pero podemos mostrarlo brevemente antes de eliminar)
      // notifySuccess(`Clave ${value} encontrada, eliminando...`); // quizás no es necesario

      // Pequeña pausa para que el usuario vea la celda resaltada en rojo
      await sleep(500);

      try {
        // Realizar la eliminación
        const res = await fetch(`${API_BASE}/delete/${encodeURIComponent(value)}`, { method: "DELETE" });
        const data = await res.json();
        console.log("Respuesta delete:", data);

        // Extraer posiciones de la respuesta (para posible resaltado adicional)
        let positions = [];
        if (Array.isArray(data)) {
          positions = data;
        } else if (data.positions && Array.isArray(data.positions)) {
          positions = data.positions;
        } else if (data.position && Array.isArray(data.position)) {
          positions = data.position;
        }

        if (res.ok && positions.length > 0) {
          await loadState(); // Recargar estado (se borran los resaltados)
          notifySuccess(`Clave ${value} eliminada.`);
        } else {
          // Si no hay positions pero el status es ok, puede que se haya eliminado igual
          if (res.ok) {
            await loadState();
            notifySuccess(`Clave ${value} eliminada.`);
          } else {
            const errorMsg = data.detail || data.message || `No se pudo eliminar (código ${res.status})`;
            notifyError(errorMsg);
          }
        }
      } catch (err) {
        console.error("Error en eliminación:", err);
        notifyError("Error de conexión al eliminar.");
      }
      clearInput();
    });
  }

  window.initSimulator = initSimulator;
})();