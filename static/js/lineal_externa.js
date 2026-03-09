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

  // Convierte una posición global (1-based) a bloque y celda
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

    // Inicialmente ocultar acciones y mostrar mensaje
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
        const data = await res.json();
        console.log("Respuesta insert:", data);
        if (res.ok) {
          await loadState();
          if (data.position && Array.isArray(data.position) && data.position.length > 0) {
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
          notifyError(data.detail || "Error al insertar");
        }
      } catch (err) {
        notifyError("Error de conexión al insertar.");
      }
    });

    searchBtn.addEventListener("click", async () => {
      const rawValue = valueInput.value.trim();
      if (!rawValue) { notifyError("Ingresa una clave."); clearInput(); return; }
      const value = toDigits(rawValue, currentState.digits);
      if (!validateKey(value)) return;

      try {
        const res = await fetch(`${API_BASE}/search/${encodeURIComponent(value)}`);
        let data;
        try {
          data = await res.json();
        } catch (e) {
          data = null;
        }
        console.log("Respuesta search:", data);

        if (res.ok) {
          // El backend puede devolver un array vacío si no encuentra
          if (data && Array.isArray(data) && data.length > 0) {
            const info = data[0];
            notifySuccess(`Clave ${value} encontrada en bloque ${info.block_index}, posición ${info.block_position}`);
            highlightCells([{ block: info.block_index, cell: info.block_position }], 'highlight-search');
          } else {
            notifyError(`Clave ${value} no encontrada.`);
          }
        } else if (res.status === 404) {
          // Si el backend devuelve 404, mostrar no encontrado
          notifyError(`Clave ${value} no encontrada.`);
        } else {
          const errorMsg = data?.detail || `Error en la búsqueda (${res.status})`;
          notifyError(errorMsg);
        }
      } catch (err) {
        console.error("Error en búsqueda:", err);
        notifyError("Error de conexión al buscar.");
      }
      clearInput();
    });

    deleteBtn.addEventListener("click", async () => {
      const rawValue = valueInput.value.trim();
      if (!rawValue) { notifyError("Ingresa una clave."); clearInput(); return; }
      const value = toDigits(rawValue, currentState.digits);
      if (!validateKey(value)) return;

      try {
        // Primero buscar para obtener la posición y resaltar antes de eliminar
        let positionsToHighlight = [];
        const searchRes = await fetch(`${API_BASE}/search/${encodeURIComponent(value)}`);
        if (searchRes.ok) {
          const searchData = await searchRes.json();
          if (Array.isArray(searchData) && searchData.length > 0) {
            const info = searchData[0];
            positionsToHighlight = [{ block: info.block_index, cell: info.block_position }];
          }
        }

        // Si se encontró, resaltar antes de eliminar
        if (positionsToHighlight.length > 0) {
          highlightCells(positionsToHighlight, 'highlight-delete', 1000);
          await sleep(1000); // Esperar a que se vea el resaltado
        }

        // Realizar la eliminación
        const res = await fetch(`${API_BASE}/delete/${encodeURIComponent(value)}`, { method: "DELETE" });
        const data = await res.json();
        console.log("Respuesta delete:", data);

        if (res.ok) {
          await loadState();
          notifySuccess(`Clave ${value} eliminada.`);
          clearInput();
        } else {
          notifyError(data.detail || "Error al eliminar");
        }
      } catch (err) {
        console.error("Error en eliminación:", err);
        notifyError("Error de conexión al eliminar.");
      }
    });
  }

  window.initSimulator = initSimulator;
})();