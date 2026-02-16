(() => {
    "use strict";

    const API_BASE = "http://127.0.0.1:8000/binary-search";

    async function sleep(ms) { return new Promise(resolve => setTimeout(resolve, ms)); }

    function toDigits(v, digits) { return String(v).padStart(digits, "0"); }

    // Renderiza las celdas en la columna central
    function renderGrid(state) {
        const grid = document.getElementById("bin-visualization");
        if (!grid) return;
        grid.innerHTML = "";
        
        for (let i = 0; i < state.size; i++) {
            const val = state.data[i];
            const cell = document.createElement("div");
            cell.className = "cell";
            if (val == null) cell.classList.add("empty");
            
            cell.dataset.index = i + 1;
            cell.textContent = val == null ? "" : val;
            grid.appendChild(cell);
        }
    }

    // Animación visual de búsqueda binaria
    async function binarySearchAnimation(targetValue, state) {
        const cells = document.querySelectorAll("#bin-visualization .cell");
        // Solo buscamos en los datos que no son None (tu service.py hace valid_data)
        const validLength = state.data.filter(v => v !== null).length;
        
        let left = 0;
        let right = validLength - 1;

        cells.forEach(c => c.classList.remove("active", "found", "discarded"));

        while (left <= right) {
            let mid = Math.floor((left + right) / 2);
            
            // Resaltar punto medio
            cells[mid].classList.add("active");
            await sleep(800);

            if (state.data[mid] === targetValue) {
                cells[mid].classList.add("found");
                return;
            }

            if (state.data[mid] < targetValue) {
                // Descartar mitad izquierda
                for (let i = left; i <= mid; i++) cells[i].classList.add("discarded");
                left = mid + 1;
            } else {
                // Descartar mitad derecha
                for (let i = mid; i <= right; i++) cells[i].classList.add("discarded");
                right = mid - 1;
            }
            await sleep(500);
        }
    }

    async function initBinaria() {
        const sizeEl = document.getElementById("bin-size");
        const digitsEl = document.getElementById("bin-digits");
        const valInput = document.getElementById("bin-value-input");
        let currentState = { size: 0, data: [] };

        const reload = async () => {
            const res = await fetch(`${API_BASE}/state`);
            currentState = await res.json();
            renderGrid(currentState);
        };

        // Evento Crear
        document.getElementById("bin-create-btn").addEventListener("click", async () => {
            await fetch(`${API_BASE}/create`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ size: parseInt(sizeEl.value), digits: parseInt(digitsEl.value) })
            });
            await reload();
        });

        // Evento Insertar (Recuerda que tu Python ordena automáticamente)
        document.getElementById("bin-insert-btn").addEventListener("click", async () => {
            const val = toDigits(valInput.value, currentState.digits);
            await fetch(`${API_BASE}/insert`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ value: val })
            });
            await reload();
            valInput.value = "";
        });

        // Evento Buscar con Animación
        document.getElementById("bin-search-btn").addEventListener("click", async () => {
            const val = toDigits(valInput.value, currentState.digits);
            await binarySearchAnimation(val, currentState);
        });

        await reload();
    }

    window.initSimulator = initBinaria;
})();