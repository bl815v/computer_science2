/* eslint-disable no-console */
(() => {
  "use strict";

  const API_BASE = "http://127.0.0.1:8000/huffman";

  // Elementos del DOM
  const messageInput = document.getElementById('message-input');
  const createBtn = document.getElementById('create-tree-btn');
  const resultsSection = document.getElementById('results-section');
  const codesTable = document.getElementById('codes-table');
  const searchLetterInput = document.getElementById('search-letter'); // Renombrado
  const searchBtn = document.getElementById('search-btn');
  const searchResult = document.getElementById('search-result');
  const treeImage = document.getElementById('tree-image');
  const imageSizeSlider = document.getElementById('image-size-slider');
  const imageSizeValue = document.getElementById('image-size-value');
  const showStepsBtn = document.getElementById('show-steps-btn');
  const stepsSection = document.getElementById('steps-section');
  const stepsContent = document.getElementById('steps-content');
  const freqTable = document.getElementById('freq-table');

  // Estado
  let currentText = '';
  let codes = {}; // { letra: codigo }
  let steps = [];
  let frequencies = {};

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

  // Renderizar tabla de códigos
  function renderCodesTable(codesObj) {
    if (!codesTable) return;
    codesTable.innerHTML = '';
    const entries = Object.entries(codesObj);
    if (entries.length === 0) {
      codesTable.textContent = 'No hay códigos generados.';
      return;
    }
    entries.sort((a, b) => a[0].localeCompare(b[0]));
    entries.forEach(([letter, code]) => {
      const card = document.createElement('div');
      card.style = 'background: var(--ms-panel); border: 1px solid var(--ms-border); border-radius: 4px; padding: 8px 16px; display: inline-flex; align-items: center; gap: 12px;';
      card.innerHTML = `
        <span style="font-weight: bold; font-size: 18px;">${letter === ' ' ? '␣' : letter}</span>
        <span style="font-family: monospace; background: #f0f0f0; padding: 4px 8px; border-radius: 4px;">${code}</span>
      `;
      codesTable.appendChild(card);
    });
  }

  // Renderizar pasos en formato tabla vertical
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
      // Crear una tabla para cada paso
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

  // Renderizar tabla de frecuencias (formato tabla)
  function renderFreqTable(freqObj) {
    if (!freqTable) return;
    if (!freqObj || Object.keys(freqObj).length === 0) {
      freqTable.innerHTML = '<p>No hay tabla de frecuencias.</p>';
      return;
    }
    const entries = Object.entries(freqObj).sort((a, b) => a[0].localeCompare(b[0]));
    let html = `<table style="width: 100%; border-collapse: collapse; font-family: monospace;">`;
    html += `<thead><tr><th style="text-align: left; border-bottom: 1px solid #ccc;">Carácter</th><th style="text-align: left; border-bottom: 1px solid #ccc;">Frecuencia</th></tr></thead>`;
    html += `<tbody>`;
    entries.forEach(([char, freq]) => {
      html += `<tr>`;
      html += `<td style="padding: 4px 8px;">${char === ' ' ? '␣' : char}</td>`;
      html += `<td style="padding: 4px 8px;">${freq}</td>`;
      html += `</tr>`;
    });
    html += `</tbody></table>`;
    freqTable.innerHTML = html;
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
      const response = await fetch(`${API_BASE}/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || 'Error al crear el árbol');
      }

      const data = await response.json();
      currentText = text;
      codes = data.codes || {};
      frequencies = data.frequencies || {};

      // Obtener pasos
      const stepsRes = await fetch(`${API_BASE}/steps`);
      if (stepsRes.ok) {
        const stepsData = await stepsRes.json();
        steps = stepsData.steps || [];
      } else {
        steps = [];
      }

      // Mostrar resultados
      resultsSection.style.display = 'block';
      renderCodesTable(codes);
      renderFreqTable(frequencies);
      renderStepsTable(steps); // Usar nueva función
      loadImage(`${API_BASE}/plot`);

      notifySuccess('Árbol de Huffman creado correctamente.');
    } catch (error) {
      notifyError(error.message);
    } finally {
      createBtn.disabled = false;
      createBtn.textContent = 'Crear árbol';
    }
  }

  // --- Buscar letra (renombrada para evitar conflicto) ---
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
          // Mostrar imagen resaltada
          loadImage(`${API_BASE}/search-plot/${encodeURIComponent(letter)}`);
          searchResult.textContent = `'${letter}' encontrado.`;
          notifySuccess(`Letra '${letter}' encontrada.`);
        } else {
          // Si no se encuentra, mostrar árbol normal
          loadImage(`${API_BASE}/plot`);
          searchResult.textContent = `'${letter}' no encontrado.`;
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
    // Eventos
    createBtn.addEventListener('click', createTree);
    searchBtn.addEventListener('click', handleSearchLetter);
    showStepsBtn.addEventListener('click', toggleSteps);

    // Permitir búsqueda con Enter
    searchLetterInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') handleSearchLetter();
    });

    // Configurar slider
    setupImageSizeSlider();

    // Estado inicial
    resultsSection.style.display = 'none';
    stepsSection.style.display = 'none';
    treeImage.src = '';
  }

  window.initSimulator = initSimulator;
})();