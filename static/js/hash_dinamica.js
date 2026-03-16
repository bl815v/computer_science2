/* eslint-disable no-console */
(() => {
  "use strict";

  const API_BASE = "http://127.0.0.1:8000/dynamic-hash";
  let isNotifying = false;
  let currentState = {
    digits: 0,
    bucket_size: 0,
    num_buckets: 0,
    blocks: [],
    overflow: [],
    count: 0,
    load_factor: 0,
  };
  let currentHashType = "mod";

  // -------------------- Utilidades --------------------
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
        window.notifyError?.(`La clave solo puede tener ${digits} dígitos.`);
        setTimeout(() => { isNotifying = false; }, 1500);
      }
    } else {
      input.value = numericValue;
    }
  }

  function validateKey(val, digits) {
    if (!val) {
      window.notifyError?.("Ingresa una clave.");
      clearInput();
      return false;
    }
    if (val.length !== digits) {
      window.notifyError?.(`La clave debe tener exactamente ${digits} dígitos.`);
      clearInput();
      return false;
    }
    return true;
  }

  // -------------------- Obtener fila real (0‑based) de un valor dentro de una cubeta --------------------
  function getRowIndexForValueInBucket(value, blockIdx) {
    const block = currentState.blocks[blockIdx];
    // Aseguramos que el valor tenga el padding correcto para comparar
    const paddedValue = toDigits(value, currentState.digits);
    for (let i = 0; i < block.length; i++) {
      if (block[i] === paddedValue) return i; // fila principal
    }
    const overflow = currentState.overflow[blockIdx] || [];
    for (let i = 0; i < overflow.length; i++) {
      if (overflow[i] === paddedValue) return currentState.bucket_size + i; // fila overflow
    }
    return -1; // no encontrado
  }

  // -------------------- Renderizado como matriz (cubetas como columnas) --------------------
  function renderGrid() {
    const container = document.getElementById("visualization");
    if (!container) return;
    container.innerHTML = "";

    if (!currentState.blocks || currentState.blocks.length === 0) {
      const msg = document.createElement("p");
      msg.className = "empty-message";
      msg.textContent = "Crea una estructura para visualizar las cubetas.";
      container.appendChild(msg);
      return;
    }

    const numBuckets = currentState.blocks.length;
    const bucketSize = currentState.bucket_size;

    // Determinar el número máximo de filas necesario (incluyendo overflow)
    let maxRows = bucketSize;
    currentState.overflow.forEach(ov => {
      if (ov.length > maxRows - bucketSize) {
        maxRows = bucketSize + ov.length;
      }
    });

    // Crear tabla
    const table = document.createElement("table");
    table.className = "hash-table";

    // Cabecera: primera celda con "Pos" + números de cubeta
    const thead = document.createElement("thead");
    const headerRow = document.createElement("tr");
    const thCorner = document.createElement("th");
    thCorner.textContent = "Pos";
    headerRow.appendChild(thCorner);
    for (let b = 0; b < numBuckets; b++) {
      const th = document.createElement("th");
      th.textContent = b;
      th.dataset.block = b;
      headerRow.appendChild(th);
    }
    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Cuerpo: filas para cada posición (desde 0 hasta maxRows-1)
    const tbody = document.createElement("tbody");
    for (let r = 0; r < maxRows; r++) {
      const tr = document.createElement("tr");
      tr.dataset.row = r; // posición (0‑based)

      // Primera celda: número de posición (1‑based para el usuario)
      const tdPos = document.createElement("td");
      tdPos.textContent = r + 1;
      tr.appendChild(tdPos);

      // Para cada cubeta, añadir celda
      for (let b = 0; b < numBuckets; b++) {
        const td = document.createElement("td");
        td.dataset.block = b;
        td.dataset.row = r;

        let val = null;
        let type = "main";
        if (r < bucketSize) {
          // Posición dentro del bloque principal
          val = currentState.blocks[b][r];
        } else {
          // Posición de overflow
          const overflowIdx = r - bucketSize;
          const overflow = currentState.overflow[b] || [];
          if (overflowIdx < overflow.length) {
            val = overflow[overflowIdx];
            type = "overflow";
          } else {
            val = null;
          }
        }

        if (val !== null && val !== undefined && val !== "") {
          td.textContent = toDigits(val, currentState.digits);
        } else {
          td.classList.add("empty");
        }
        if (type === "overflow") {
          td.classList.add("overflow");
        }
        tr.appendChild(td);
      }
      tbody.appendChild(tr);
    }
    table.appendChild(tbody);
    container.appendChild(table);
  }

  // -------------------- Animación de búsqueda (recorre la columna) --------------------
  async function animateSearch(targetValue, blockIdx, resultClass = "found", autoClear = true) {
    console.log(`animateSearch: valor=${targetValue}, blockIdx=${blockIdx}`);
    const container = document.getElementById("visualization");
    const table = container?.querySelector(".hash-table");
    if (!table) return false;

    // Validar blockIdx
    if (blockIdx < 0 || blockIdx >= currentState.num_buckets) {
      console.error(`Índice de cubeta inválido: ${blockIdx}`);
      window.notifyError?.(`Índice de cubeta inválido: ${blockIdx + 1}`);
      return false;
    }

    // Limpiar clases previas
    table.querySelectorAll("td").forEach(c => c.classList.remove("active", "found", "discarded", "highlight-insert", "highlight-delete", "active-col"));
    table.querySelectorAll("col").forEach(c => c.classList.remove("active-col"));

    // Obtener la fila real donde se encuentra el valor
    const rowIdx = getRowIndexForValueInBucket(targetValue, blockIdx);
    console.log(`rowIdx encontrado: ${rowIdx}`);
    if (rowIdx === -1) {
      console.error("Valor no encontrado en la estructura");
      window.notifyError?.("Error de animación: valor no encontrado en la estructura.");
      return false;
    }

    // Resaltar la columna (cubeta)
    const cellsInColumn = table.querySelectorAll(`td[data-block="${blockIdx}"]`);
    if (cellsInColumn.length === 0) {
      window.notifyError?.(`Error de animación: cubeta ${blockIdx + 1} no encontrada.`);
      return false;
    }
    cellsInColumn.forEach(cell => cell.classList.add("active-col"));
    await sleep(600);

    // Buscar la celda específica
    let targetCell = null;
    for (let cell of cellsInColumn) {
      if (cell.dataset.row == rowIdx) {
        targetCell = cell;
        break;
      }
    }

    if (!targetCell) {
      window.notifyError?.("Error de animación: celda no encontrada en el DOM.");
      cellsInColumn.forEach(cell => cell.classList.remove("active-col"));
      return false;
    }

    // Simular búsqueda secuencial dentro de la columna (recorrer celdas en orden de fila)
    const allCellsInColumn = Array.from(cellsInColumn).sort((a, b) => {
      return parseInt(a.dataset.row) - parseInt(b.dataset.row);
    });

    let found = false;
    for (let cell of allCellsInColumn) {
      cell.classList.add("active");
      await sleep(400);

      if (cell === targetCell) {
        cell.classList.remove("active");
        cell.classList.add(resultClass);
        found = true;
        break;
      } else {
        cell.classList.remove("active");
        cell.classList.add("discarded");
      }
      await sleep(200);
    }

    if (found) {
      if (autoClear) {
        await sleep(2000);
        table.querySelectorAll("td").forEach(c => c.classList.remove("active", "found", "discarded", "highlight-insert", "highlight-delete", "active-col"));
      }
      return true;
    } else {
      window.notifyError?.(`Error de animación: no se encontró la celda destino.`);
      return false;
    }
  }

  // -------------------- Cargar estado desde backend --------------------
  async function loadState() {
    try {
      const res = await fetch(`${API_BASE}/state`);
      if (res.status === 404) {
        console.log("No hay estructura previa");
        currentState = { digits: 0, bucket_size: 0, num_buckets: 0, blocks: [], overflow: [], count: 0, load_factor: 0 };
        renderGrid();
        return;
      }
      if (!res.ok) throw new Error("Error al cargar estado");
      const data = await res.json();
      currentState = {
        digits: data.digits || 0,
        bucket_size: data.bucket_size || 0,
        num_buckets: data.num_buckets || 0,
        blocks: data.blocks || [],
        overflow: data.overflow || [],
        count: data.count || 0,
        load_factor: data.load_factor || 0,
      };
      renderGrid();

      // Mostrar/ocultar sección de acciones
      const actions = document.getElementById("actions-section");
      if (actions) {
        actions.style.display = currentState.num_buckets > 0 ? "block" : "none";
      }
    } catch (err) {
      console.error("Error en loadState:", err);
      currentState = { digits: 0, bucket_size: 0, num_buckets: 0, blocks: [], overflow: [], count: 0, load_factor: 0 };
      renderGrid();
    }
  }

  // -------------------- Inicialización --------------------
  async function initSimulator() {
    // Elementos del DOM
    const hashTypeSelect = document.getElementById("hash-type");
    const truncParams = document.getElementById("truncation-params");
    const foldingParams = document.getElementById("folding-params");
    const createBtn = document.getElementById("create-structure-btn");
    const digitsInput = document.getElementById("digits");
    const initialBucketsInput = document.getElementById("initial-buckets");
    const bucketSizeInput = document.getElementById("bucket-size");
    const expansionPolicy = document.getElementById("expansion-policy");
    const valueInput = document.getElementById("value-input");
    const insertBtn = document.getElementById("insert-btn");
    const searchBtn = document.getElementById("search-btn");
    const deleteBtn = document.getElementById("delete-btn");

    // Mostrar/ocultar parámetros según tipo de hash
    function updateHashParams() {
      const type = hashTypeSelect.value;
      currentHashType = type;
      truncParams.style.display = type === "truncation" ? "flex" : "none";
      foldingParams.style.display = type === "folding" ? "flex" : "none";
    }
    hashTypeSelect.addEventListener("change", updateHashParams);
    updateHashParams();

    // Crear estructura (configura hash y luego crea)
    createBtn.addEventListener("click", async () => {
      const digits = parseInt(digitsInput.value);
      const initialBuckets = parseInt(initialBucketsInput.value);
      const bucketSize = parseInt(bucketSizeInput.value);
      const policy = expansionPolicy.value; // "total" o "partial"

      if (isNaN(digits) || digits <= 0) return window.notifyError?.("Dígitos inválidos.");
      if (isNaN(initialBuckets) || initialBuckets <= 0) return window.notifyError?.("Número de cubetas inicial inválido.");
      if (isNaN(bucketSize) || bucketSize <= 0) return window.notifyError?.("Tamaño de cubeta inválido.");

      // 1. Configurar función hash
      const type = hashTypeSelect.value;
      let hashBody = { type };

      if (type === "truncation") {
        const positionsStr = document.getElementById("trunc-positions").value;
        if (!positionsStr) {
          window.notifyError?.("Debes ingresar las posiciones (ej. 1,3)");
          return;
        }
        const positions = positionsStr.split(",").map(s => parseInt(s.trim())).filter(n => !isNaN(n));
        if (positions.length === 0) {
          window.notifyError?.("Posiciones inválidas");
          return;
        }
        hashBody.positions = positions;
      } else if (type === "folding") {
        const groupSize = parseInt(document.getElementById("folding-group").value);
        const operation = document.getElementById("folding-op").value;
        if (isNaN(groupSize) || groupSize < 1) {
          window.notifyError?.("Tamaño de grupo inválido");
          return;
        }
        hashBody.group_size = groupSize;
        hashBody.operation = operation;
      }

      try {
        // Primero set-hash
        const hashRes = await fetch(`${API_BASE}/set-hash`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(hashBody)
        });
        if (!hashRes.ok) {
          const err = await hashRes.json();
          throw new Error(err.detail || "Error al configurar hash");
        }

        // Luego crear estructura con umbrales fijos
        const createBody = {
          digits,
          initial_num_buckets: initialBuckets,
          bucket_size: bucketSize,
          expansion_policy: policy,
          expansion_threshold: 0.75,
          reduction_threshold: 0.5
        };

        const createRes = await fetch(`${API_BASE}/create`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(createBody)
        });
        if (!createRes.ok) {
          const err = await createRes.json();
          throw new Error(err.detail || "Error al crear estructura");
        }

        await loadState();
        window.notifySuccess?.("Estructura creada correctamente.");
        if (valueInput) valueInput.placeholder = `Máx: ${digits} dígitos`;
      } catch (err) {
        window.notifyError?.(err.message);
      }
    });

    // Restricción de dígitos en el input
    if (valueInput) {
      valueInput.addEventListener("input", () => {
        const digits = currentState.digits || parseInt(digitsInput.value) || 0;
        enforceNumericDigits(valueInput, digits);
      });
    }

    // Insertar
    insertBtn.addEventListener("click", async () => {
      const rawValue = valueInput.value.trim();
      if (!rawValue) { window.notifyError?.("Ingresa una clave."); clearInput(); return; }
      const digits = currentState.digits;
      if (digits === 0) { window.notifyError?.("Primero crea la estructura."); return; }
      const value = toDigits(rawValue, digits);
      if (!validateKey(value, digits)) return;

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

        if (res.ok) {
          await loadState();
          if (data.position && Array.isArray(data.position) && data.position.length > 0) {
            const pos = data.position[0]; // { global_position, block_index, block_position }
            window.notifySuccess?.(`Clave ${value} insertada en cubeta ${pos.block_index}, posición ${pos.block_position}`);
            // Resaltar la celda insertada usando el valor
            const table = document.querySelector(".hash-table");
            const rowIdx = getRowIndexForValueInBucket(value, pos.block_index - 1);
            if (rowIdx !== -1) {
              const cell = table?.querySelector(`td[data-block="${pos.block_index-1}"][data-row="${rowIdx}"]`);
              if (cell) {
                cell.classList.add("highlight-insert");
                setTimeout(() => cell.classList.remove("highlight-insert"), 2000);
              }
            }
          } else {
            window.notifySuccess?.(`Clave ${value} insertada.`);
          }
          clearInput();
        } else {
          let errorMsg = data.detail || data.message || `Error ${res.status}`;
          window.notifyError?.(errorMsg);
          clearInput();
        }
      } catch (err) {
        console.error("Error en inserción:", err);
        window.notifyError?.("Error de conexión al insertar.");
        clearInput();
      }
    });

    // Buscar
    searchBtn.addEventListener("click", async () => {
      const rawValue = valueInput.value.trim();
      if (!rawValue) { window.notifyError?.("Ingresa una clave."); clearInput(); return; }
      const digits = currentState.digits;
      if (digits === 0) { window.notifyError?.("Primero crea la estructura."); return; }
      const value = toDigits(rawValue, digits);
      if (!validateKey(value, digits)) return;

      console.log(`Buscando valor: ${value}`);
      try {
        const res = await fetch(`${API_BASE}/search/${encodeURIComponent(value)}`);
        console.log(`Respuesta status: ${res.status}`);
        if (res.status === 404) {
          window.notifyError?.(`Clave ${value} no encontrada.`);
          clearInput();
          return;
        }
        if (!res.ok) throw new Error("Error en búsqueda");
        
        const responseData = await res.json();
        console.log("Respuesta completa:", responseData);
        
        // Extraer el array de posiciones
        let positions = [];
        if (Array.isArray(responseData)) {
          positions = responseData;
        } else if (responseData.position && Array.isArray(responseData.position)) {
          positions = responseData.position;
        } else if (responseData.positions && Array.isArray(responseData.positions)) {
          positions = responseData.positions;
        }
        
        if (positions.length === 0) {
          window.notifyError?.(`Clave ${value} no encontrada.`);
          clearInput();
          return;
        }
        
        const pos = positions[0];
        if (!pos || typeof pos.block_index !== 'number') {
          console.error("Posición inválida:", pos);
          window.notifyError?.("Respuesta de búsqueda inválida.");
          clearInput();
          return;
        }
        
        const blockIdx = pos.block_index - 1;
        const animOk = await animateSearch(value, blockIdx, "found", true);
        if (animOk) {
          window.notifySuccess?.(`Clave ${value} encontrada en cubeta ${pos.block_index}, posición ${pos.block_position}`);
        } else {
          // Aún así, la clave fue encontrada, mostramos éxito
          window.notifySuccess?.(`Clave ${value} encontrada en cubeta ${pos.block_index}, posición ${pos.block_position} (sin animación)`);
        }
        clearInput();
      } catch (err) {
        console.error("Error en búsqueda:", err);
        window.notifyError?.("Error de conexión al buscar.");
        clearInput();
      }
    });

    // Eliminar
    deleteBtn.addEventListener("click", async () => {
      const rawValue = valueInput.value.trim();
      if (!rawValue) { window.notifyError?.("Ingresa una clave."); clearInput(); return; }
      const digits = currentState.digits;
      if (digits === 0) { window.notifyError?.("Primero crea la estructura."); return; }
      const value = toDigits(rawValue, digits);
      if (!validateKey(value, digits)) return;

      console.log(`Eliminando valor: ${value}`);
      try {
        const searchRes = await fetch(`${API_BASE}/search/${encodeURIComponent(value)}`);
        console.log(`Respuesta búsqueda status: ${searchRes.status}`);
        if (searchRes.status === 404) {
          window.notifyError?.(`Clave ${value} no encontrada.`);
          clearInput();
          return;
        }
        if (!searchRes.ok) throw new Error("Error en búsqueda previa");
        
        const responseData = await searchRes.json();
        console.log("Respuesta para eliminar:", responseData);
        
        // Extraer el array de posiciones
        let positions = [];
        if (Array.isArray(responseData)) {
          positions = responseData;
        } else if (responseData.position && Array.isArray(responseData.position)) {
          positions = responseData.position;
        } else if (responseData.positions && Array.isArray(responseData.positions)) {
          positions = responseData.positions;
        }
        
        if (positions.length === 0) {
          window.notifyError?.(`Clave ${value} no encontrada.`);
          clearInput();
          return;
        }
        
        const pos = positions[0];
        if (!pos || typeof pos.block_index !== 'number') {
          window.notifyError?.("Respuesta de búsqueda inválida.");
          clearInput();
          return;
        }
        
        const blockIdx = pos.block_index - 1;

        const animOk = await animateSearch(value, blockIdx, "highlight-delete", false);
        if (!animOk) {
          console.warn("Animación falló, pero se procede a eliminar");
        }

        await sleep(500);

        const deleteRes = await fetch(`${API_BASE}/delete/${encodeURIComponent(value)}`, {
          method: "DELETE"
        });
        console.log(`Respuesta delete status: ${deleteRes.status}`);
        if (!deleteRes.ok) {
          const errData = await deleteRes.json();
          throw new Error(errData.detail || "Error al eliminar");
        }
        await loadState();
        window.notifySuccess?.(`Clave ${value} eliminada.`);
        clearInput();
      } catch (err) {
        console.error("Error en eliminación:", err);
        window.notifyError?.(err.message);
        clearInput();
      }
    });

    // Cargar estado inicial
    await loadState();
  }

  window.initSimulator = initSimulator;
})();