/* eslint-disable no-console */
(() => {
  "use strict";

  const API_BASE = "http://127.0.0.1:8000/external/linear";
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

  function globalPosToBlockCell(globalPos) {
    if (!currentState.blocks || currentState.blocks.length === 0) return null;
    let accumulated = 0;
    for (let b = 0; b < currentState.blocks.length; b++) {
      const blockLength = currentState.blocks[b].length;
      if (globalPos <= accumulated + blockLength) {
        return {
          block: b + 1,
          cell: globalPos - accumulated
        };
      }
      accumulated += blockLength;
    }
    return null;
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

  // --- Animación de búsqueda lineal externa con resaltado de bloques ---
  async function linearExternalSearchAnimation(targetValue, options = { autoClear: true, resultClass: 'found' }) {
    const container = document.getElementById("visualization");
    if (!container) return null;

    // Limpiar clases previas
    const allCells = container.querySelectorAll(".cell");
    const allBlocks = container.querySelectorAll(".block");
    allCells.forEach(c => c.classList.remove("active", "found", "visited", "not-found", "highlight-delete", "discarded", "highlight-insert"));
    allBlocks.forEach(b => b.classList.remove("block-active", "block-discarded", "block-candidate"));

    // Obtener el máximo de cada bloque (último valor no nulo)
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

    let found = false;
    let foundPos = null;

    // Recorrer bloques secuencialmente
    for (let b = 0; b < currentState.blocks.length; b++) {
      const blockElem = container.querySelector(`.block[data-block="${b + 1}"]`);
      const maxVal = blockMaxValues[b];

      // Resaltar el bloque actual
      if (blockElem) {
        blockElem.classList.add("block-active");
      }
      await sleep(600);

      if (maxVal === null) {
        // Bloque vacío: descartar
        if (blockElem) {
          blockElem.classList.remove("block-active");
          blockElem.classList.add("block-discarded");
        }
        await sleep(300);
        continue;
      }

      if (targetValue <= maxVal) {
        // Buscar dentro del bloque
        const blockCells = container.querySelectorAll(`.block[data-block="${b + 1}"] .cell`);
        for (let c = 0; c < blockCells.length; c++) {
          const cell = blockCells[c];
          cell.classList.add("active");
          await sleep(300);

          const cellContent = cell.textContent.trim();
          if (cellContent === targetValue) {
            cell.classList.remove("active");
            cell.classList.add(options.resultClass);
            found = true;
            foundPos = { block: b + 1, cell: c + 1 };
            break;
          } else {
            cell.classList.remove("active");
            cell.classList.add("visited");
          }

          const cellNum = cellContent ? Number(cellContent) : NaN;
          if (!isNaN(cellNum) && cellNum > targetValue) {
            break; // Nos pasamos, ya no puede estar
          }
        }

        if (blockElem) blockElem.classList.remove("block-active");
        if (found) break;

        // No encontrado en este bloque candidato, terminar
        if (blockElem) blockElem.classList.add("block-discarded");
        break;
      } else {
        // target > maxVal, descartar bloque
        if (blockElem) {
          blockElem.classList.remove("block-active");
          blockElem.classList.add("block-discarded");
        }
        await sleep(300);
      }
    }

    if (!found) {
      allCells.forEach(c => c.classList.add("not-found"));
      await sleep(1000);
      allCells.forEach(c => c.classList.remove("not-found", "visited", "active"));
      allBlocks.forEach(b => b.classList.remove("block-active", "block-discarded", "block-candidate"));
      return null;
    } else {
      if (options.autoClear) {
        await sleep(1500);
        allCells.forEach(c => c.classList.remove("active", "found", "visited", "discarded", options.resultClass));
        allBlocks.forEach(b => b.classList.remove("block-active", "block-discarded", "block-candidate"));
      }
      return foundPos;
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

    // ---- INSERTAR CON ANIMACIÓN ----
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
          await loadState(); // Recargar para tener el estado actualizado

          // Mostrar animación de búsqueda para resaltar dónde quedó la clave insertada
          const foundPos = await linearExternalSearchAnimation(value, { autoClear: true, resultClass: 'highlight-insert' });
          if (foundPos) {
            notifySuccess(`Clave ${value} insertada en bloque ${foundPos.block}, posición ${foundPos.cell}`);
          } else {
            // Si no se encuentra (raro), igual notificamos éxito
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

    // ---- BUSCAR CON ANIMACIÓN ----
    searchBtn.addEventListener("click", async () => {
      const rawValue = valueInput.value.trim();
      if (!rawValue) { notifyError("Ingresa una clave."); clearInput(); return; }
      const value = toDigits(rawValue, currentState.digits);
      if (!validateKey(value)) return;

      const foundPos = await linearExternalSearchAnimation(value, { autoClear: true, resultClass: 'found' });
      if (foundPos) {
        notifySuccess(`Clave ${value} encontrada en bloque ${foundPos.block}, posición ${foundPos.cell}`);
      } else {
        notifyError(`Clave ${value} no encontrada.`);
      }
      clearInput();
    });

    // ---- ELIMINAR CON ANIMACIÓN PREVIA ----
    deleteBtn.addEventListener("click", async () => {
      const rawValue = valueInput.value.trim();
      if (!rawValue) { notifyError("Ingresa una clave."); clearInput(); return; }
      const value = toDigits(rawValue, currentState.digits);
      if (!validateKey(value)) return;

      const foundPos = await linearExternalSearchAnimation(value, { autoClear: false, resultClass: 'highlight-delete' });

      if (!foundPos) {
        notifyError(`Clave ${value} no encontrada.`);
        clearInput();
        return;
      }

      await sleep(500);

      try {
        const res = await fetch(`${API_BASE}/delete/${encodeURIComponent(value)}`, { method: "DELETE" });
        const data = await res.json();
        console.log("Respuesta delete:", data);

        let positions = [];
        if (Array.isArray(data)) {
          positions = data;
        } else if (data.positions && Array.isArray(data.positions)) {
          positions = data.positions;
        } else if (data.position && Array.isArray(data.position)) {
          positions = data.position;
        }

        if (res.ok && positions.length > 0) {
          await loadState();
          notifySuccess(`Clave ${value} eliminada.`);
        } else {
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