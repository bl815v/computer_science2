/* eslint-disable no-console */
(() => {
  "use strict";

  const API_BASE = "http://127.0.0.1:8000/hash-external";
  let isNotifying = false;
  let currentState = { size: 0, digits: 0, block_size: 0, blocks: [], overflow: [] };

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

  // Convierte posición global (1-based) a bloque y celda (considerando overflow)
  function globalPosToBlockCell(globalPos) {
    if (!currentState.blocks || currentState.blocks.length === 0) return null;
    let acc = 0;
    for (let b = 0; b < currentState.blocks.length; b++) {
      const blockLen = currentState.blocks[b].length;
      if (globalPos <= acc + blockLen) {
        return {
          block: b + 1,
          cell: globalPos - acc,
          location: 'block'
        };
      }
      acc += blockLen;
    }
    const totalPrincipal = acc;
    let overflowAcc = 0;
    for (let b = 0; b < currentState.overflow.length; b++) {
      const overflowLen = currentState.overflow[b].length;
      if (globalPos <= totalPrincipal + overflowAcc + overflowLen) {
        return {
          block: b + 1,
          cell: globalPos - totalPrincipal - overflowAcc,
          location: 'overflow'
        };
      }
      overflowAcc += overflowLen;
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
        cell.dataset.location = "block";

        if (val !== null && val !== undefined && val !== "") {
          cell.textContent = toDigits(val, currentState.digits);
        } else {
          cell.classList.add("empty");
          cell.textContent = "";
        }
        cellsDiv.appendChild(cell);
      });

      blockDiv.appendChild(cellsDiv);

      // Agregar overflow si existe
      const overflowList = currentState.overflow[bIdx] || [];
      if (overflowList.length > 0) {
        const overflowDiv = document.createElement("div");
        overflowDiv.className = "block-overflow";

        const title = document.createElement("div");
        title.className = "block-overflow-title";
        title.textContent = "Overflow:";
        overflowDiv.appendChild(title);

        const overflowCellsDiv = document.createElement("div");
        overflowCellsDiv.className = "overflow-cells";

        overflowList.forEach((val, idx) => {
          const cell = document.createElement("div");
          cell.className = "overflow-cell";
          cell.dataset.block = bIdx + 1;
          cell.dataset.pos = idx + 1;
          cell.dataset.location = "overflow";
          cell.textContent = toDigits(val, currentState.digits);
          overflowCellsDiv.appendChild(cell);
        });

        overflowDiv.appendChild(overflowCellsDiv);
        blockDiv.appendChild(overflowDiv);
      }

      container.appendChild(blockDiv);
    });
  }

  function highlightCells(positions, className, duration = 1500) {
    if (!positions || positions.length === 0) return;
    const container = document.getElementById("visualization");
    positions.forEach(({ block, cell, location }) => {
      let selector;
      if (location === 'overflow') {
        selector = `.overflow-cell[data-block="${block}"][data-pos="${cell}"]`;
      } else {
        selector = `.cell[data-block="${block}"][data-pos="${cell}"]`;
      }
      const element = container.querySelector(selector);
      if (element) {
        console.log(`Resaltando ${location} bloque ${block} celda ${cell} con clase ${className}`);
        element.classList.add(className);
        setTimeout(() => {
          element.classList.remove(className);
          console.log(`Quitando resaltado de ${location} bloque ${block} celda ${cell}`);
        }, duration);
      } else {
        console.warn(`No se encontró elemento con selector: ${selector}`);
      }
    });
  }

  // --- Animación de búsqueda en hash externo ---
  async function animateSearch(value) {
    const container = document.getElementById("visualization");
    if (!container) return null;

    const allCells = container.querySelectorAll(".cell, .overflow-cell");
    allCells.forEach(c => c.classList.remove("active", "found", "highlight-search", "highlight-delete", "candidate"));

    try {
      const res = await fetch(`${API_BASE}/search/${encodeURIComponent(value)}`);
      const data = await res.json();
      if (!res.ok || !Array.isArray(data) || data.length === 0) {
        return null;
      }

      for (let i = 0; i < data.length; i++) {
        const item = data[i];
        const bc = globalPosToBlockCell(item.global_position);
        if (!bc) continue;
        let selector;
        if (bc.location === 'overflow') {
          selector = `.overflow-cell[data-block="${bc.block}"][data-pos="${bc.cell}"]`;
        } else {
          selector = `.cell[data-block="${bc.block}"][data-pos="${bc.cell}"]`;
        }
        const element = container.querySelector(selector);
        if (element) {
          element.classList.add("active");
          await sleep(600);
          if (i === data.length - 1) {
            element.classList.remove("active");
            element.classList.add("found");
            // Programar la eliminación de la clase found después de 1.5s
            setTimeout(() => {
              element.classList.remove("found");
            }, 1500);
          } else {
            element.classList.remove("active");
            element.classList.add("visited");
          }
        }
      }
      return globalPosToBlockCell(data[0].global_position);
    } catch (err) {
      console.error("Error en animateSearch:", err);
      return null;
    }
  }

  // --- Animación de eliminación (similar pero con rojo) ---
  async function animateDelete(value) {
    const container = document.getElementById("visualization");
    if (!container) return null;

    const allCells = container.querySelectorAll(".cell, .overflow-cell");
    allCells.forEach(c => c.classList.remove("active", "found", "highlight-search", "highlight-delete", "candidate"));

    try {
      const res = await fetch(`${API_BASE}/search/${encodeURIComponent(value)}`);
      const data = await res.json();
      if (!res.ok || !Array.isArray(data) || data.length === 0) {
        return null;
      }

      for (let i = 0; i < data.length; i++) {
        const item = data[i];
        const bc = globalPosToBlockCell(item.global_position);
        if (!bc) continue;
        let selector;
        if (bc.location === 'overflow') {
          selector = `.overflow-cell[data-block="${bc.block}"][data-pos="${bc.cell}"]`;
        } else {
          selector = `.cell[data-block="${bc.block}"][data-pos="${bc.cell}"]`;
        }
        const element = container.querySelector(selector);
        if (element) {
          element.classList.add("active");
          await sleep(600);
          if (i === data.length - 1) {
            element.classList.remove("active");
            element.classList.add("highlight-delete");
            // Programar la eliminación de la clase highlight-delete después de 1.5s
            setTimeout(() => {
              element.classList.remove("highlight-delete");
            }, 1500);
          } else {
            element.classList.remove("active");
            element.classList.add("visited");
          }
        }
      }
      return globalPosToBlockCell(data[0].global_position);
    } catch (err) {
      console.error("Error en animateDelete:", err);
      return null;
    }
  }

  async function loadState() {
    try {
      const res = await fetch(`${API_BASE}/state`);
      if (res.status === 404) {
        console.log("No hay estructura previa (404)");
        currentState = { size: 0, digits: 0, block_size: 0, blocks: [], overflow: [] };
        renderGrid();
        return;
      }
      if (!res.ok) throw new Error("Error al cargar estado");
      const data = await res.json();
      console.log("Estado cargado:", data);
      currentState = {
        size: data.size || 0,
        digits: data.digits || 0,
        block_size: data.block_size || 0,
        blocks: data.blocks || [],
        overflow: data.overflow || []
      };
      const blockSizeSpan = document.getElementById("block-size-display");
      if (blockSizeSpan) blockSizeSpan.textContent = currentState.block_size || "-";
      renderGrid();
    } catch (err) {
      console.error("Error en loadState:", err);
      currentState = { size: 0, digits: 0, block_size: 0, blocks: [], overflow: [] };
      renderGrid();
    }
  }

  // Construye el body para set-hash según los parámetros seleccionados
  function buildHashBody() {
    const type = document.getElementById("hash-type").value;
    let body = { type };
    if (type === "truncation") {
      const positionsInput = document.getElementById("hash-positions");
      if (!positionsInput) return null;
      const positions = positionsInput.value.split(',').map(p => parseInt(p.trim())).filter(p => !isNaN(p));
      if (positions.length === 0) return null;
      body.positions = positions;
    } else if (type === "folding") {
      const groupSize = parseInt(document.getElementById("hash-group-size")?.value);
      if (isNaN(groupSize) || groupSize <= 0) return null;
      const operation = document.getElementById("hash-operation")?.value || "sum";
      body.group_size = groupSize;
      body.operation = operation;
    } else if (type === "base_conversion") {
      const base = parseInt(document.getElementById("hash-base")?.value);
      if (isNaN(base) || base < 2) return null;
      body.base = base;
    }
    return body;
  }

  async function initSimulator() {
    const hashTypeSelect = document.getElementById("hash-type");
    const hashParamsDiv = document.getElementById("hash-params");
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

    // Ocultar acciones inicialmente
    actionsSection.style.display = "none";
    renderGrid();

    // Actualizar vista previa del tamaño de bloque
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

    // ---- Manejo dinámico de parámetros de hash ----
    function updateHashParams() {
      const type = hashTypeSelect.value;
      hashParamsDiv.innerHTML = "";
      if (type === "truncation") {
        hashParamsDiv.innerHTML = `
          <div class="row">
            <label>Posiciones (ej: 1,3,5):</label>
            <input type="text" id="hash-positions" value="1,2,3" placeholder="1,3,5" />
          </div>
        `;
      } else if (type === "folding") {
        hashParamsDiv.innerHTML = `
          <div class="row">
            <label>Tamaño de grupo:</label>
            <input type="number" id="hash-group-size" value="2" min="1" />
          </div>
          <div class="row">
            <label>Operación:</label>
            <select id="hash-operation">
              <option value="sum">Suma</option>
              <option value="mul">Multiplicación</option>
            </select>
          </div>
        `;
      } else if (type === "base_conversion") {
        hashParamsDiv.innerHTML = `
          <div class="row">
            <label>Base:</label>
            <input type="number" id="hash-base" value="7" min="2" />
          </div>
        `;
      } else {
        hashParamsDiv.innerHTML = "";
      }
    }
    hashTypeSelect.addEventListener("change", updateHashParams);
    updateHashParams();

    // Crear estructura: primero configurar hash, luego crear
    createBtn.addEventListener("click", async () => {
      const hashBody = buildHashBody();
      if (!hashBody) {
        return notifyError("Complete correctamente los parámetros de la función hash.");
      }

      const size = parseInt(totalSizeInput.value);
      const digits = parseInt(digitsInput.value);
      if (isNaN(size) || size <= 0) return notifyError("Capacidad inválida.");
      if (isNaN(digits) || digits <= 0) return notifyError("Dígitos inválidos.");

      try {
        const hashRes = await fetch(`${API_BASE}/set-hash`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(hashBody)
        });
        if (!hashRes.ok) {
          const err = await hashRes.json();
          throw new Error(err.detail || "Error al configurar hash");
        }

        const createRes = await fetch(`${API_BASE}/create`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ size, digits })
        });
        if (!createRes.ok) {
          const err = await createRes.json();
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

    // ---- INSERTAR CON ANIMACIÓN (resaltado después de ordenar) ----
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
          await loadState(); // Recarga la estructura (ya ordenada)

          // Buscar la clave para obtener su posición actual después de ordenar
          const searchRes = await fetch(`${API_BASE}/search/${encodeURIComponent(value)}`);
          if (searchRes.ok) {
            const searchData = await searchRes.json();
            if (searchData.length > 0) {
              const posActual = searchData[0].global_position;
              const bc = globalPosToBlockCell(posActual);
              if (bc) {
                highlightCells([bc], 'highlight-insert', 2000); // 2 segundos para que se note
                notifySuccess(`Clave ${value} insertada en bloque ${bc.block}, ${bc.location === 'overflow' ? 'overflow' : 'posición'} ${bc.cell}`);
              } else {
                notifySuccess(`Clave ${value} insertada.`);
              }
            } else {
              notifySuccess(`Clave ${value} insertada.`);
            }
          } else {
            notifySuccess(`Clave ${value} insertada.`);
          }
          clearInput();
        } else {
          const errorMsg = data.detail || data.message || "Error al insertar";
          notifyError(errorMsg);
          clearInput();
        }
      } catch (err) {
        console.error("Error en inserción:", err);
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

      const foundPos = await animateSearch(value);
      if (foundPos) {
        notifySuccess(`Clave ${value} encontrada en bloque ${foundPos.block}, ${foundPos.location === 'overflow' ? 'overflow' : 'posición'} ${foundPos.cell}`);
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

      const foundPos = await animateDelete(value);
      if (!foundPos) {
        notifyError(`Clave ${value} no encontrada.`);
        clearInput();
        return;
      }

      // Pequeña pausa para que el usuario vea el resaltado rojo
      await sleep(800);

      try {
        const res = await fetch(`${API_BASE}/delete/${encodeURIComponent(value)}`, { method: "DELETE" });
        const data = await res.json();
        console.log("Respuesta delete:", data);
        if (res.ok) {
          await loadState();
          if (data.deleted_positions && data.deleted_positions.length > 0) {
            notifySuccess(`Clave ${value} eliminada.`);
          } else {
            notifyError(`Clave ${value} no encontrada.`);
          }
        } else {
          const errorMsg = data.detail || data.message || "Error al eliminar";
          notifyError(errorMsg);
        }
        clearInput();
      } catch (err) {
        console.error("Error en eliminación:", err);
        notifyError("Error de conexión al eliminar.");
        clearInput();
      }
    });
  }

  window.initSimulator = initSimulator;
})();