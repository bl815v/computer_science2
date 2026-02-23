/* eslint-disable no-console */
(() => {
  "use strict";
  const API_BASE = "http://127.0.0.1:8000/hash";
  let lastValueAttempt = ""; 
  let currentDigits = 0;
  let isNotifying = false;

  // --- Utilidades ---
  function clearInput() {
    const inp = document.getElementById("value-input");
    if (inp) {
      inp.value = "";
      inp.focus();
    }
  }

  function toDigits(v, digits) {
    if (v === null || v === undefined || v === "") return "";
    // Si el valor es numérico o string numérico, rellenar con ceros
    if (!isNaN(v) && v !== "DELETED") {
        return String(v).padStart(digits, "0");
    }
    return v;
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
    if (val.length !== currentDigits) {
      notifyError(`La clave debe tener exactamente ${currentDigits} dígitos.`);
      clearInput();
      return false;
    }
    return true;
  }

  // --- Renderizado ---
  function renderGrid(currentState) {
    const grid = document.getElementById("visualization");
    if (!grid) return;
    grid.innerHTML = "";
    
    currentState.data.forEach((val, i) => {
      const cell = document.createElement("div");
      cell.className = "cell";
      cell.dataset.index = `Dir: ${i}`; 

      if (Array.isArray(val)) {
        cell.innerHTML = val.length > 0 
          ? val.map(v => `<span class="hash-item">${toDigits(v, currentDigits)}</span>`).join("") 
          : "";
      } else {
        cell.textContent = (val === null || val === undefined) 
          ? "" 
          : (val === "DELETED" ? "🗑️" : toDigits(val, currentDigits));
      }
      
      if (!cell.textContent && (!Array.isArray(val) || val.length === 0)) {
        cell.classList.add("empty");
      }
      grid.appendChild(cell);
    });
  }

  async function initHashing() {
    const createBtn = document.getElementById("create-structure");
    const insertBtn = document.getElementById("insert-btn");
    const searchBtn = document.getElementById("search-btn");
    const deleteBtn = document.getElementById("delete-btn");
    const collisionMenu = document.getElementById("collision-menu");
    const applyCollisionBtn = document.getElementById("apply-collision");
    const valInp = document.getElementById("value-input");

    if (valInp) {
      valInp.addEventListener("input", () => {
        const d = currentDigits || parseInt(document.getElementById("digits").value) || 0;
        enforceNumericDigits(valInp, d);
      });
    }

    // --- Inicializar ---
    createBtn.addEventListener("click", async () => {
      const hType = document.getElementById("hash-type").value;
      const size = parseInt(document.getElementById("size").value);
      const digits = parseInt(document.getElementById("digits").value);

      if (isNaN(size) || size <= 0) return notifyError("Tamaño inválido.");
      if (isNaN(digits) || digits <= 0) return notifyError("Dígitos inválidos.");

      try {
        currentDigits = digits;
        valInp.placeholder = `Ej: ${"1".padStart(digits, "0")}`;
        
        await fetch(`${API_BASE}/set-hash`, {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({ type: hType, positions: [1, 2], group_size: 2 })
        });

        const res = await fetch(`${API_BASE}/create`, {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({ size, digits })
        });

        if (!res.ok) {
           const errData = await res.json();
           throw new Error(errData.detail || "Error al crear");
        }

        const stateRes = await fetch(`${API_BASE}/state`);
        renderGrid(await stateRes.json());
        
        collisionMenu.style.display = "none";
        document.getElementById("actions-section").style.display = "block";
        notifySuccess(`Estructura lista para ${digits} dígitos.`);
        clearInput();
      } catch (err) { notifyError(err.message); }
    });

    // --- Insertar ---
    insertBtn.addEventListener("click", async () => {
      const rawValue = valInp.value.trim();
      if (!rawValue) { notifyError("Ingresa una clave."); clearInput(); return; }
      const value = toDigits(rawValue, currentDigits);
      if (!validateKey(value)) return;
      lastValueAttempt = rawValue;

      try {
        const res = await fetch(`${API_BASE}/insert`, {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({ value })
        });

        const data = await res.json();

        if (res.ok) {
          const stateRes = await fetch(`${API_BASE}/state`);
          renderGrid(await stateRes.json());
          notifySuccess(`Clave ${value} insertada en Dir: ${data.position - 1}`);
          collisionMenu.style.display = "none";
          clearInput();
        } else {
          if (data.detail && data.detail.includes("Colisión")) {
            notifyError(data.detail);
            collisionMenu.style.display = "flex";
          } else {
            notifyError(data.detail || "Error al insertar");
          }
          clearInput();
        }
      } catch (e) { notifyError("Error de conexión al insertar."); clearInput(); }
    });

    // --- Aplicar Colisión ---
    applyCollisionBtn.addEventListener("click", async () => {
      const cType = document.getElementById("collision-type").value;
      const endpoint = cType === 'chaining' ? `${API_BASE}/set-chaining` : `${API_BASE}/set-collision`;
      
      try {
        const res = await fetch(endpoint, {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({ type: cType, second_hash_type: "mod" })
        });

        if (res.ok) {
          collisionMenu.style.display = "none";
          notifySuccess(`Estrategia aplicada. Reintentando...`);
          valInp.value = lastValueAttempt;
          insertBtn.click();
        } else {
           const data = await res.json();
           notifyError(data.detail || "No se pudo aplicar la estrategia.");
        }
      } catch (e) { notifyError("Error al aplicar estrategia."); clearInput(); }
    });

    // --- Buscar ---
    searchBtn.addEventListener("click", async () => {
      const rawValue = valInp.value.trim();
      if (!rawValue) { notifyError("Ingresa una clave."); clearInput(); return; }
      const value = toDigits(rawValue, currentDigits);
      if (!validateKey(value)) return;

      try {
        const res = await fetch(`${API_BASE}/search/${value}`);
        const data = await res.json();
        
        if (res.ok) {
          if (data.found) {
            const dirs = data.positions.map(p => p - 1).join(", ");
            notifySuccess(`Clave ${value} encontrada en Dir(s): ${dirs}`);
          } else {
            notifyError(`La clave ${value} no existe.`);
          }
        } else {
          notifyError(data.detail || "Error en la búsqueda.");
        }
      } catch (e) { notifyError("Error de conexión al buscar."); }
      clearInput();
    });

    // --- Borrar (CORREGIDO) ---
    deleteBtn.addEventListener("click", async () => {
      const rawValue = valInp.value.trim();
      if (!rawValue) { notifyError("Ingresa una clave."); clearInput(); return; }
      const value = toDigits(rawValue, currentDigits);
      if (!validateKey(value)) return;

      try {
        const res = await fetch(`${API_BASE}/delete/${value}`, { method: "DELETE" });
        const data = await res.json();

        if (res.ok) {
          // Refrescar tabla
          const stateRes = await fetch(`${API_BASE}/state`);
          renderGrid(await stateRes.json());
          
          // Verificación segura de data.positions para evitar el crash
          if (data && data.positions && Array.isArray(data.positions) && data.positions.length > 0) {
            const dirs = data.positions.map(p => p - 1).join(", ");
            notifySuccess(`Clave ${value} eliminada de Dir: ${dirs}`);
          } else {
            notifySuccess(`Clave ${value} eliminada.`);
          }
        } else {
          notifyError(data.detail || "Error al eliminar.");
        }
      } catch (e) { 
        console.error("Error Delete:", e);
        notifyError("Error al procesar la eliminación."); 
      }
      clearInput();
    });
  }

  window.initSimulator = initHashing;
})();