/* eslint-disable no-console */
(() => {
  "use strict";

  const API_BASE = "http://127.0.0.1:8000/external/linear";
  let isNotifying = false;
  let currentState = { num_blocks: 0, block_size: 0, digits: 0, data: [] };

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

    const numBlocks = currentState.num_blocks;
    const blockSize = currentState.block_size;
    const data = currentState.data;

    for (let b = 0; b < numBlocks; b++) {
      const blockDiv = document.createElement("div");
      blockDiv.className = "block";
      blockDiv.dataset.block = b + 1;

      const blockHeader = document.createElement("div");
      blockHeader.className = "block-header";
      blockHeader.textContent = `Bloque ${b + 1}`;
      blockDiv.appendChild(blockHeader);

      const cellsDiv = document.createElement("div");
      cellsDiv.className = "block-cells";

      const blockData = data[b] || [];
      for (let i = 0; i < blockSize; i++) {
        const val = blockData[i];
        const cell = document.createElement("div");
        cell.className = "cell";
        cell.dataset.block = b + 1;
        cell.dataset.pos = i + 1;
        cell.dataset.index = `${b + 1}.${i + 1}`;

        if (val !== undefined && val !== null && val !== "") {
          cell.textContent = toDigits(val, currentState.digits);
        } else {
          cell.classList.add("empty");
          cell.textContent = "";
        }
        cellsDiv.appendChild(cell);
      }
      blockDiv.appendChild(cellsDiv);
      container.appendChild(blockDiv);
    }
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
        // No hay estructura creada aún, es normal
        console.log("No hay estructura previa (404)");
        currentState = { num_blocks: 0, block_size: 0, digits: 0, data: [] };
        renderGrid();
        return;
      }
      if (!res.ok) throw new Error("Error al cargar estado");
      currentState = await res.json();
      renderGrid();
    } catch (err) {
      console.error("Error en loadState:", err);
      // En caso de cualquier error, mostramos una estructura vacía
      currentState = { num_blocks: 0, block_size: 0, digits: 0, data: [] };
      renderGrid();
    }
  }

  async function initSimulator() {
    const numBlocksInput = document.getElementById("num-blocks");
    const blockSizeInput = document.getElementById("block-size");
    const digitsInput = document.getElementById("digits");
    const createBtn = document.getElementById("create-structure");
    const actionsSection = document.getElementById("actions-section");
    const valueInput = document.getElementById("value-input");
    const insertBtn = document.getElementById("insert-btn");
    const searchBtn = document.getElementById("search-btn");
    const deleteBtn = document.getElementById("delete-btn");

    if (!createBtn) return;

    actionsSection.style.display = "none";

    createBtn.addEventListener("click", async () => {
      const numBlocks = parseInt(numBlocksInput.value);
      const blockSize = parseInt(blockSizeInput.value);
      const digits = parseInt(digitsInput.value);

      if (isNaN(numBlocks) || numBlocks <= 0) return notifyError("Número de bloques inválido.");
      if (isNaN(blockSize) || blockSize <= 0) return notifyError("Tamaño de bloque inválido.");
      if (isNaN(digits) || digits <= 0) return notifyError("Dígitos inválidos.");

      try {
        const res = await fetch(`${API_BASE}/create`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ size: numBlocks, digits, block_size: blockSize })
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
        if (res.ok) {
          await loadState();
          notifySuccess(`Clave ${value} insertada en bloque ${data.block}, posición ${data.position}`);
          highlightCells([{ block: data.block, cell: data.position }], 'highlight-insert');
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
        const data = await res.json();
        if (res.ok) {
          if (data.found) {
            notifySuccess(`Clave ${value} encontrada en bloque ${data.block}, posición ${data.position}`);
            highlightCells([{ block: data.block, cell: data.position }], 'highlight-search');
          } else {
            notifyError(`Clave ${value} no encontrada.`);
          }
        } else {
          notifyError(data.detail || "Error en la búsqueda.");
        }
      } catch (err) {
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
        const res = await fetch(`${API_BASE}/delete/${encodeURIComponent(value)}`, { method: "DELETE" });
        const data = await res.json();
        if (res.ok) {
          await loadState();
          notifySuccess(`Clave ${value} eliminada.`);
          clearInput();
        } else {
          notifyError(data.detail || "Error al eliminar");
        }
      } catch (err) {
        notifyError("Error de conexión al eliminar.");
      }
    });

    // Cargar estado inicial (si existe) sin mostrar error al usuario
    await loadState();
    if (currentState.num_blocks > 0) {
      actionsSection.style.display = "block";
    }
  }

  window.initSimulator = initSimulator;
})();