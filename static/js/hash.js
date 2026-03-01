/* eslint-disable no-console */
(() => {
  "use strict";
  const API_BASE = getApiUrl(API_CONFIG.ENDPOINTS.HASH);
  let lastValueAttempt = ""; 
  let currentDigits = 0;
  let isNotifying = false;

  function clearInput() {
    const inp = document.getElementById("value-input");
    if (inp) {
      inp.value = "";
      inp.focus();
    }
  }

  function toDigits(v, digits) {
    if (v === null || v === undefined || v === "") return "";
    if (!isNaN(v) && v !== "DELETED") {
        return String(v).padStart(digits, "0");
    }
    return v;
  }

  function enforceNumericDigits(input, digits) {
    if (!input || digits <= 0) return;
    
    const originalValue = input.value;
    const numericValue = originalValue.replace(/\D+/g, "");
    
    if (digits > 0 && numericValue.length > digits) {
      input.value = numericValue.slice(0, digits);
      if (!isNotifying) {
        isNotifying = true;
        window.notifyError(`La clave solo puede tener ${digits} dígitos.`, true);
        setTimeout(() => { isNotifying = false; }, 1500);
      }
    } else {
      input.value = numericValue;
    }
  }

  function validateKey(val) {
    if (!val) {
      window.notifyError("Ingresa una clave.", true);
      clearInput();
      return false;
    }
    if (val.length !== currentDigits) {
      window.notifyError(`La clave debe tener exactamente ${currentDigits} dígitos.`, true);
      clearInput();
      return false;
    }
    return true;
  }

  function renderGrid(currentState) {
    const grid = document.getElementById("visualization");
    if (!grid) return;
    grid.innerHTML = "";
    
    currentState.data.forEach((val, i) => {
      const cell = document.createElement("div");
      cell.className = "cell";
      cell.dataset.index = `Dir: ${i+1}`; 

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

    if (!createBtn || !insertBtn || !searchBtn || !deleteBtn) return;

    if (valInp) {
      valInp.addEventListener("input", () => {
        const d = currentDigits || parseInt(document.getElementById("digits")?.value) || 0;
        enforceNumericDigits(valInp, d);
      });
    }

    createBtn.addEventListener("click", async () => {
      const hType = document.getElementById("hash-type")?.value;
      const size = parseInt(document.getElementById("size")?.value);
      const digits = parseInt(document.getElementById("digits")?.value);

      if (isNaN(size) || size <= 0) {
        window.notifyError("Tamaño inválido.", true);
        return;
      }
      if (isNaN(digits) || digits <= 0) {
        window.notifyError("Dígitos inválidos.", true);
        return;
      }

      try {
        currentDigits = digits;
        if (valInp) {
          valInp.maxLength = digits;
          valInp.placeholder = `Ej: ${"1".padStart(digits, "0")}`;
        }
        
        await fetchWithTimeout(`${API_BASE}/set-hash`, {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({ type: hType, positions: [1, 2], group_size: 2 })
        });

        const res = await fetchWithTimeout(`${API_BASE}/create`, {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({ size, digits })
        });

        if (!res.ok) {
           const errData = await res.json();
           throw new Error(errData.detail || "Error al crear");
        }

        const stateRes = await fetchWithTimeout(`${API_BASE}/state`);
        renderGrid(await stateRes.json());
        
        if (collisionMenu) collisionMenu.style.display = "none";
        const actionsSection = document.getElementById("actions-section");
        if (actionsSection) actionsSection.style.display = "block";
        
        window.notifySuccess(`Estructura lista para ${digits} dígitos.`, true);
        clearInput();
      } catch (err) { 
        window.notifyError(err.message, true);
      }
    });

    if (insertBtn) {
      insertBtn.addEventListener("click", async () => {
        if (!valInp) return;
        
        const rawValue = valInp.value.trim();
        if (!rawValue) { 
          window.notifyError("Ingresa una clave.", true);
          clearInput(); 
          return; 
        }
        const value = toDigits(rawValue, currentDigits);
        if (!validateKey(value)) return;
        lastValueAttempt = rawValue;

        try {
          const res = await fetchWithTimeout(`${API_BASE}/insert`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ value })
          });

          const data = await res.json();

          if (res.ok) {
            const stateRes = await fetchWithTimeout(`${API_BASE}/state`);
            renderGrid(await stateRes.json());
            window.notifySuccess(`Clave ${value} insertada en Dir: ${data.position - 1}`, true);
            if (collisionMenu) collisionMenu.style.display = "none";
            clearInput();
          } else {
            if (data.detail && data.detail.includes("Colisión")) {
              window.notifyError(data.detail, true);
              if (collisionMenu) collisionMenu.style.display = "flex";
            } else {
              window.notifyError(data.detail || "Error al insertar", true);
            }
            clearInput();
          }
        } catch (e) { 
          window.notifyError("Error de conexión al insertar.", true);
          clearInput(); 
        }
      });
    }

    if (applyCollisionBtn) {
      applyCollisionBtn.addEventListener("click", async () => {
        const cType = document.getElementById("collision-type")?.value;
        const endpoint = cType === 'chaining' ? `${API_BASE}/set-chaining` : `${API_BASE}/set-collision`;
        
        try {
          const res = await fetchWithTimeout(endpoint, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ type: cType, second_hash_type: "mod" })
          });

          if (res.ok) {
            if (collisionMenu) collisionMenu.style.display = "none";
            window.notifySuccess(`Estrategia aplicada. Reintentando...`, true);
            if (valInp) {
              valInp.value = lastValueAttempt;
              insertBtn?.click();
            }
          } else {
             const data = await res.json();
             window.notifyError(data.detail || "No se pudo aplicar la estrategia.", true);
          }
        } catch (e) { 
          window.notifyError("Error al aplicar estrategia.", true);
          clearInput(); 
        }
      });
    }

    if (searchBtn) {
      searchBtn.addEventListener("click", async () => {
        if (!valInp) return;
        
        const rawValue = valInp.value.trim();
        if (!rawValue) { 
          window.notifyError("Ingresa una clave.", true);
          clearInput(); 
          return; 
        }
        const value = toDigits(rawValue, currentDigits);
        if (!validateKey(value)) return;

        try {
          const res = await fetchWithTimeout(`${API_BASE}/search/${value}`);
          const data = await res.json();
          
          if (res.ok) {
            if (data.found) {
              const dirs = data.positions ? data.positions.map(p => p - 1).join(", ") : "desconocida";
              window.notifySuccess(`Clave ${value} encontrada en Dir(s): ${dirs}`, true);
            } else {
              window.notifyError(`La clave ${value} no existe.`, true);
            }
          } else {
            window.notifyError(data.detail || "Error en la búsqueda.", true);
          }
        } catch (e) { 
          window.notifyError("Error de conexión al buscar.", true);
        }
        clearInput();
      });
    }

    if (deleteBtn) {
      deleteBtn.addEventListener("click", async () => {
        if (!valInp) return;
        
        const rawValue = valInp.value.trim();
        if (!rawValue) { 
          window.notifyError("Ingresa una clave.", true);
          clearInput(); 
          return; 
        }
        
        const value = toDigits(rawValue, currentDigits);
        if (!validateKey(value)) return;

        try {
          const res = await fetchWithTimeout(`${API_BASE}/delete/${value}`, { method: "DELETE" });
          const data = await res.json();

          if (res.ok) {
            const stateRes = await fetchWithTimeout(`${API_BASE}/state`);
            renderGrid(await stateRes.json());
            
            if (data && data.positions && Array.isArray(data.positions) && data.positions.length > 0) {
              const dirs = data.positions.map(p => p - 1).join(", ");
              window.notifySuccess(`Clave ${value} eliminada de Dir: ${dirs}`, true);
            } else {
              window.notifySuccess(`Clave ${value} eliminada.`, true);
            }
          } else {
            window.notifyError(data.detail || "Error al eliminar.", true);
          }
        } catch (e) { 
          console.error("Error en eliminación:", e);
          window.notifyError("Error al procesar la eliminación. Verifica la conexión.", true);
        }
        clearInput();
      });
    }
  }

  window.initSimulator = initHashing;
})();