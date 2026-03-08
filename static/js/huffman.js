/* eslint-disable no-console */
(() => {
  "use strict";

  const API_BASE = "http://127.0.0.1:8000/huffman";

  // Elementos del DOM
  const messageInput = document.getElementById('message-input');
  const createBtn = document.getElementById('create-tree-btn');
  const resultsSection = document.getElementById('results-section');
  const codesTable = document.getElementById('codes-table');
  const searchLetterInput = document.getElementById('search-letter'); // Renombrado para evitar conflicto
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
  let frequencies = {};
  let stepsData = []; // Array de pasos

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

  // Mostrar notificaciones (usando las globales de notificaciones.js)
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
      card.className = 'code-card';
      card.innerHTML = `
        <span class="code-letter">${letter === ' ' ? '␣' : letter}</span>
        <span class="code-value">${code}</span>
      `;
      codesTable.appendChild(card);
    });
  }

  // Renderizar pasos (formato mejorado)
  function renderSteps() {
    if (!stepsContent) return;
    if (!stepsData || stepsData.length === 0) {
      stepsContent.textContent = 'No hay pasos disponibles.';
      return;
    }
    let html = '';
    stepsData.forEach(step => {
      html += `<div class="step-title">Paso ${step.step}</div>`;
      html += '<div class="step-items">';
      step.items.forEach(item => {
        html += `<div class="step-item">${item.name} (${item.freq})</div>`;
      });
      html += '</div>';
    });
    stepsContent.innerHTML = html;
  }

  // Renderizar tabla de frecuencias (formato tabla)
  function renderFreqTable(freqObj) {
    if (!freqTable) return;
    if (Object.keys(freqObj).length === 0) {
      freqTable.textContent = 'No hay tabla de frecuencias.';
      return;
    }
    const entries = Object.entries(freqObj).sort((a, b) => a[0].localeCompare(b[0]));
    let html = '<table class="freq-table"><tr><th>Carácter</th><th>Frecuencia</th></tr>';
    entries.forEach(([char, freq]) => {
      html += `<tr><td>${char === ' ' ? '␣' : char}</td><td>${freq}</td></tr>`;
    });
    html += '</table>';
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
      // Crear árbol
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
        const stepsDataObj = await stepsRes.json();
        // El backend devuelve { steps: [...] }
        stepsData = stepsDataObj.steps || [];
      } else {
        stepsData = [];
      }

      // Mostrar resultados
      resultsSection.style.display = 'block';
      renderCodesTable(codes);
      renderFreqTable(frequencies);
      renderSteps(); // Renderizar pasos
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
  async function handleSearch() {
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
    searchBtn.addEventListener('click', handleSearch);
    showStepsBtn.addEventListener('click', toggleSteps);

    // Permitir búsqueda con Enter
    searchLetterInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') handleSearch();
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