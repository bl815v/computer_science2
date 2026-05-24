(() => {
  "use strict";

  const API_BASE = "http://127.0.0.1:8000/search/index";

  function getEndpoint(type) {
    switch(type) {
      case 'primary': return `${API_BASE}/primary`;
      case 'secondary': return `${API_BASE}/secondary`;
      case 'multilevel-primary': return `${API_BASE}/multilevel-primary`;
      case 'multilevel-secondary': return `${API_BASE}/multilevel-secondary`;
      default: return `${API_BASE}/primary`;
    }
  }

  async function calculate() {
    const r = parseInt(document.getElementById('total-records').value);
    const block_size = parseInt(document.getElementById('block-size').value);
    const record_length = parseInt(document.getElementById('record-length').value);
    const index_record_length = parseInt(document.getElementById('index-record-length').value);
    const indexType = document.getElementById('index-type').value;

    if (isNaN(r) || isNaN(block_size) || isNaN(record_length) || isNaN(index_record_length)) {
      notifyError('Complete todos los campos numéricos');
      return;
    }

    const resultsDiv = document.getElementById('results-section');
    const vizDiv = document.getElementById('visualization');
    resultsDiv.style.display = 'block';
    vizDiv.innerHTML = '<div class="loading-overlay">Calculando estructura...</div>';

    try {
      const endpoint = getEndpoint(indexType);
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ r, block_size, record_length, index_record_length })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Error en el cálculo');
      }

      const data = await response.json(); // data tiene la estructura IndexResponse
      renderVisualization(data, indexType);
      notifySuccess('Estructura calculada correctamente');
    } catch (err) {
      notifyError(err.message);
      vizDiv.innerHTML = '<div class="error-message">No se pudo generar la visualización</div>';
    }
  }

  function renderVisualization(data, type) {
    const vizDiv = document.getElementById('visualization');
    if (!vizDiv) return;

    // data: { bfr, b, bfr_i, b_i, accesses, log_value, levels: [{level, blocks}] }
    const { bfr, b, bfr_i, b_i, accesses, log_value, levels } = data;

    let html = `<div class="stats-summary">
                  <div class="stat-item">📦 Datos: ${b} bloques (${bfr} reg/bloque)</div>
                  <div class="stat-item">📇 Índice: ${b_i} bloques (${bfr_i} entradas/bloque)</div>
                  <div class="stat-item">⚡ Accesos estimados: ${accesses}</div>
                  <div class="stat-item">📐 log₂: ${log_value.toFixed(2)}</div>
                </div>`;

    if (levels && levels.length > 0) {
      html += `<div class="multilevel-container">`;
      levels.forEach(lvl => {
        html += `<div class="level-card">
                  <div class="level-title">Nivel ${lvl.level}</div>
                  <div class="level-blocks">${lvl.blocks} bloques</div>
                </div>`;
        if (lvl.level !== levels[levels.length-1].level) {
          html += `<div class="arrow">⬇️</div>`;
        }
      });
      html += `</div>`;
    } else {
      // Índice simple: mostrar un solo nivel
      html += `<div class="level-card">
                <div class="level-title">Índice único</div>
                <div class="level-blocks">${b_i} bloques</div>
              </div>`;
    }

    // Representación visual de bloques (simplificada pero moderna)
    html += `<div class="blocks-representation">
              <div class="data-blocks">
                <h4>Bloques de datos (${b})</h4>
                <div class="block-grid">${'<div class="mini-block"></div>'.repeat(Math.min(b, 20))}${b>20 ? '<span class="more">+...</span>' : ''}</div>
              </div>
              <div class="index-blocks">
                <h4>Bloques de índice (${b_i})</h4>
                <div class="block-grid">${'<div class="mini-block index"></div>'.repeat(Math.min(b_i, 20))}${b_i>20 ? '<span class="more">+...</span>' : ''}</div>
              </div>
            </div>`;

    vizDiv.innerHTML = html;
  }

  document.getElementById('calculate-btn').addEventListener('click', calculate);
  window.initSimulator = () => {
    document.getElementById('results-section').style.display = 'none';
  };
})();