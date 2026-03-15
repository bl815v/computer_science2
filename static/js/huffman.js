/* eslint-disable no-console */
(() => {
  "use strict";

  const API_BASE = "http://127.0.0.1:8000/huffman";

  // Elementos del DOM
  const messageInput = document.getElementById('message-input');
  const createBtn = document.getElementById('create-tree-btn');
  const resultsSection = document.getElementById('results-section');
  
  // Nuevos elementos para la tabla principal
  const mainTableBody = document.getElementById('huffman-table-body');
  const mainTableFoot = document.getElementById('huffman-table-foot');
  
  const searchLetterInput = document.getElementById('search-letter');
  const searchBtn = document.getElementById('search-btn');
  const searchResult = document.getElementById('search-result');
  const treeImage = document.getElementById('tree-image');
  const imageSizeSlider = document.getElementById('image-size-slider');
  const imageSizeValue = document.getElementById('image-size-value');
  const showStepsBtn = document.getElementById('show-steps-btn');
  const stepsSection = document.getElementById('steps-section');
  const stepsContent = document.getElementById('steps-content');

  // Estado
  let currentText = '';
  let steps = [];

  // --- Utilidades ---
  function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // Configurar slider de tamaño de imagen
  function setupImageSizeSlider() {
    if (!imageSizeSlider || !imageSizeValue || !treeImage) return;

    const initialSize = imageSizeSlider.value;
    treeImage.style.width = initialSize + 'px';
    imageSizeValue.textContent = initialSize + 'px';

    imageSizeSlider.addEventListener('input', function() {
      const size = this.value + 'px';
      treeImage.style.width = size;
      imageSizeValue.textContent = size;
    });
  }

  // Cargar imagen con timestamp para evitar caché
  function loadImage(url) {
    const separator = url.includes('?') ? '&' : '?';
    treeImage.src = `${url}${separator}t=${Date.now()}`;
  }

  // Mostrar notificaciones
  function notifySuccess(msg) {
    if (window.notifySuccess) window.notifySuccess(msg);
    else alert(msg);
  }

  function notifyError(msg) {
    if (window.notifyError) window.notifyError(msg);
    else alert(msg);
  }

  function notifyInfo(msg) {
    if (window.notifyInfo) window.notifyInfo(msg);
    else alert(msg);
  }

  // --- Renderizar tabla principal con datos de /table ---
  function renderMainTable(data) {
    if (!mainTableBody || !mainTableFoot) return;
    mainTableBody.innerHTML = '';
    mainTableFoot.innerHTML = '';

    if (!data || !data.table || data.table.length === 0) {
      mainTableBody.innerHTML = '<tr><td colspan="5">No hay datos</td></tr>';
      return;
    }

    // Filas
    data.table.forEach(row => {
      const tr = document.createElement('tr');
      tr.setAttribute('data-char', row.char);
      tr.innerHTML = `
        <td>${row.char === ' ' ? '␣' : row.char}</td>
        <td>${row.freq}</td>
        <td><code>${row.binary}</code></td>
        <td>${row.li}</td>
        <td>${row.L}</td>
      `;
      mainTableBody.appendChild(tr);
    });

    // Pie con totales
    const totalRow = document.createElement('tr');
    totalRow.innerHTML = `
      <td colspan="4" style="text-align: right;"><strong>Promedio</strong></td>
      <td>${data.average_L.toFixed(2)}</td>
    `;
    mainTableFoot.appendChild(totalRow);
  }

  // --- Renderizar pasos en formato tabla vertical ---
  function renderStepsTable(stepsArray) {
    if (!stepsContent) return;
    if (!stepsArray || stepsArray.length === 0) {
      stepsContent.innerHTML = '<p>No hay pasos disponibles.</p>';
      return;
    }

    let html = '';
    stepsArray.forEach((step, idx) => {
      const stepNum = idx + 1;
      const items = step.items || [];
      html += `<div style="margin-bottom: 20px; border-bottom: 1px solid var(--ms-border); padding-bottom: 10px;">`;
      html += `<h4 style="margin: 5px 0;">Paso ${stepNum}</h4>`;
      if (items.length > 0) {
        html += `<table style="width: 100%; border-collapse: collapse; font-family: monospace;">`;
        html += `<thead><tr><th style="text-align: left; border-bottom: 1px solid #ccc;">Elemento</th><th style="text-align: left; border-bottom: 1px solid #ccc;">Frecuencia</th></tr></thead>`;
        html += `<tbody>`;
        items.forEach(item => {
          html += `<tr>`;
          html += `<td style="padding: 4px 8px;">${item.name || '?'}</td>`;
          html += `<td style="padding: 4px 8px;">${item.freq}</td>`;
          html += `</tr>`;
        });
        html += `</tbody></table>`;
      } else {
        html += `<p>No hay elementos en este paso.</p>`;
      }
      html += `</div>`;
    });
    stepsContent.innerHTML = html;
  }

  // --- Funciones para resaltado en búsqueda ---
  function clearHighlight() {
    const rows = mainTableBody.querySelectorAll('tr');
    rows.forEach(row => row.classList.remove('highlight'));
  }

  function highlightLetter(letter) {
    clearHighlight();
    const rows = mainTableBody.querySelectorAll('tr');
    for (let row of rows) {
      if (row.dataset.char === letter) {
        row.classList.add('highlight');
        break;
      }
    }
  }

  // --- Crear árbol ---
  async function createTree() {
    const text = messageInput.value.trim();
    if (!text) {
      notifyError('Por favor, ingresa un mensaje.');
      return;
    }

    createBtn.disabled = true;
    createBtn.textContent = 'Creando...';

    try {
      // 1. Crear árbol
      const createRes = await fetch(`${API_BASE}/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });

      if (!createRes.ok) {
        const errData = await createRes.json().catch(() => ({}));
        throw new Error(errData.detail || 'Error al crear el árbol');
      }

      const createData = await createRes.json();
      currentText = text;

      // 2. Obtener tabla completa (códigos, frecuencias, longitudes)
      const tableRes = await fetch(`${API_BASE}/table`);
      if (tableRes.ok) {
        const tableData = await tableRes.json();
        renderMainTable(tableData);
      } else {
        notifyError('No se pudo obtener la tabla de frecuencias.');
      }

      // 3. Obtener pasos
      const stepsRes = await fetch(`${API_BASE}/steps`);
      if (stepsRes.ok) {
        const stepsData = await stepsRes.json();
        steps = stepsData.steps || [];
        renderStepsTable(steps);
      } else {
        steps = [];
        renderStepsTable(steps);
      }

      // 4. Mostrar resultados
      resultsSection.style.display = 'block';
      loadImage(`${API_BASE}/plot`);

      notifySuccess('Árbol de Huffman creado correctamente.');
    } catch (error) {
      notifyError(error.message);
    } finally {
      createBtn.disabled = false;
      createBtn.textContent = 'Crear árbol';
    }
  }

  // --- Buscar letra ---
  async function handleSearchLetter() {
    const letter = searchLetterInput.value.trim();
    if (!letter) {
      notifyError('Ingresa una letra para buscar.');
      return;
    }
    if (letter.length > 1) {
      notifyError('Ingresa solo una letra.');
      return;
    }

    searchBtn.disabled = true;
    const originalText = searchBtn.textContent;
    searchBtn.textContent = 'Buscando...';

    try {
      const response = await fetch(`${API_BASE}/search/${encodeURIComponent(letter)}`);
      const data = await response.json();

      if (response.ok) {
        if (data.position && data.position.length > 0) {
          loadImage(`${API_BASE}/search-plot/${encodeURIComponent(letter)}`);
          searchResult.textContent = `'${letter}' encontrado.`;
          highlightLetter(letter.toUpperCase());
          notifySuccess(`Letra '${letter}' encontrada.`);
        } else {
          loadImage(`${API_BASE}/plot`);
          searchResult.textContent = `'${letter}' no encontrado.`;
          clearHighlight();
          notifyError(`Letra '${letter}' no encontrada.`);
        }
      } else {
        notifyError(data.detail || 'Error en la búsqueda.');
      }
    } catch (error) {
      notifyError('Error de conexión al buscar.');
    } finally {
      searchBtn.disabled = false;
      searchBtn.textContent = originalText;
    }
  }

  // --- Mostrar/ocultar sección de pasos ---
  function toggleSteps() {
    if (stepsSection.style.display === 'none') {
      stepsSection.style.display = 'block';
      showStepsBtn.textContent = 'Ocultar fuentes de información reducidas';
    } else {
      stepsSection.style.display = 'none';
      showStepsBtn.textContent = 'Ver fuentes de información reducidas';
    }
  }

  // --- Inicialización ---
  function initSimulator() {
    createBtn.addEventListener('click', createTree);
    searchBtn.addEventListener('click', handleSearchLetter);
    showStepsBtn.addEventListener('click', toggleSteps);

    searchLetterInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') handleSearchLetter();
    });

    setupImageSizeSlider();

    resultsSection.style.display = 'none';
    stepsSection.style.display = 'none';
    treeImage.src = '';
  }

  window.initSimulator = initSimulator;
})();