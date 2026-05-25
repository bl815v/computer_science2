/* eslint-disable no-console */
(() => {
  "use strict";

  const TREE_TYPES = {
    digital: 'digital',
    simple: 'simple-residue',
    multiple: 'multiple-residue'
  };

  let currentType = TREE_TYPES.digital;
  let baseURL = `http://127.0.0.1:8000/${currentType}`;

  const btnDigital = document.getElementById('btn-digital');
  const btnSimple = document.getElementById('btn-simple');
  const btnMultiple = document.getElementById('btn-multiple');
  const mField = document.getElementById('m-field');
  const mInput = document.getElementById('m');
  const createBtn = document.getElementById('create-structure');
  const letterInput = document.getElementById('letter-input');
  const insertBtn = document.getElementById('insert-btn');
  const searchBtn = document.getElementById('search-btn');
  const deleteBtn = document.getElementById('delete-btn');
  const viewTreeBtn = document.getElementById('view-tree-btn');
  const treeImage = document.getElementById('tree-image');
  const imageSizeSlider = document.getElementById('image-size-slider');
  const imageSizeValue = document.getElementById('image-size-value');
  const actionsSection = document.getElementById('actions-section');

  const FIXED_SIZE = 1000;
  const FIXED_DIGITS = 5;
  const FIXED_M = 2;

  function updateBaseURL() {
    baseURL = `http://127.0.0.1:8000/${currentType}`;
  }

  function toggleMField() {
    mField.style.display = currentType === TREE_TYPES.multiple ? 'block' : 'none';
  }

  function setActiveTypeButton(type) {
    [btnDigital, btnSimple, btnMultiple].forEach(btn => btn.classList.remove('active'));
    if (type === TREE_TYPES.digital) btnDigital.classList.add('active');
    if (type === TREE_TYPES.simple) btnSimple.classList.add('active');
    if (type === TREE_TYPES.multiple) btnMultiple.classList.add('active');
  }

  function changeType(type) {
    if (type === currentType) return;
    currentType = type;
    updateBaseURL();
    setActiveTypeButton(type);
    toggleMField();
    if (actionsSection) actionsSection.style.display = 'none';
    treeImage.src = '';
  }

  function isValidLetter(letter) {
    return /^[A-Z]$/i.test(letter);
  }

  function normalizeLetter(letter) {
    return letter.toUpperCase();
  }

  function enforceSingleLetter(input) {
    const raw = input.value;
    const singleValidLetterRegex = /^[A-Z]$/i;
    if (raw === '') return;
    if (singleValidLetterRegex.test(raw)) {
      input.value = raw.toUpperCase();
      return;
    }
    const cleaned = raw.toUpperCase().replace(/[^A-Z]/g, '');
    const newValue = cleaned.length > 0 ? cleaned.charAt(0) : '';
    input.value = newValue;
    window.notifyError?.('Solo se permite una letra del alfabeto americano (A-Z)');
  }

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

  function loadImage(url) {
    const separator = url.includes('?') ? '&' : '?';
    treeImage.src = `${url}${separator}t=${Date.now()}`;
  }

  function notify(message, type = 'info') {
    if (type === 'success') window.notifySuccess?.(message);
    else if (type === 'error') window.notifyError?.(message);
    else window.notifyInfo?.(message);
  }

  async function createStructure() {
    const body = {
      size: FIXED_SIZE,
      digits: FIXED_DIGITS
    };
    if (currentType === TREE_TYPES.multiple) {
      let mVal = FIXED_M;
      if (mInput && mInput.value !== undefined && mInput.value !== null && String(mInput.value).trim() !== '') {
        const parsed = parseInt(mInput.value, 10);
        if (!isNaN(parsed) && parsed > 0) mVal = parsed;
      }
      body.m = mVal;
    }

    try {
      const res = await fetch(`${baseURL}/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Error al crear la estructura');
      }
      notify('Estructura creada correctamente', 'success');
      window.markStructureDirty?.();
      if (actionsSection) actionsSection.style.display = 'block';
      loadImage(`${baseURL}/plot`);
    } catch (err) {
      notify(err.message, 'error');
    }
  }

  async function insertLetter() {
    const letterRaw = letterInput.value.trim();
    if (!isValidLetter(letterRaw)) {
      return notify('Ingresa una sola letra válida (A-Z)', 'error');
    }
    const letter = normalizeLetter(letterRaw);

    try {
      const res = await fetch(`${baseURL}/insert`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ letter })
      });
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Error al insertar la letra');
      }
      notify(`Letra ${letter} insertada correctamente`, 'success');
      window.markStructureDirty?.();
      loadImage(`${baseURL}/plot`);
      letterInput.value = '';
    } catch (err) {
      notify(err.message, 'error');
    }
  }

  async function searchLetter(showHighlighted = true) {
    const letterRaw = letterInput.value.trim();
    if (!isValidLetter(letterRaw)) {
      return notify('Ingresa una sola letra válida (A-Z)', 'error');
    }
    const letter = normalizeLetter(letterRaw);

    try {
      const searchRes = await fetch(`${baseURL}/search/${encodeURIComponent(letter)}`);
      if (!searchRes.ok) {
        if (searchRes.status === 404) {
          notify(`Letra ${letter} no encontrada`, 'error');
          loadImage(`${baseURL}/plot`);
        } else {
          const errorData = await searchRes.json().catch(() => ({}));
          throw new Error(errorData.detail || 'Error en la búsqueda');
        }
        return;
      }
      notify(`Letra ${letter} encontrada`, 'success');
      if (showHighlighted) {
        loadImage(`${baseURL}/search-plot/${encodeURIComponent(letter)}`);
      } else {
        loadImage(`${baseURL}/plot`);
      }
    } catch (err) {
      notify(err.message, 'error');
    }
  }

  async function deleteLetter() {
    const letterRaw = letterInput.value.trim();
    if (!isValidLetter(letterRaw)) {
      return notify('Ingresa una sola letra válida (A-Z)', 'error');
    }
    const letter = normalizeLetter(letterRaw);

    try {
      const res = await fetch(`${baseURL}/delete/${encodeURIComponent(letter)}`, {
        method: 'DELETE'
      });
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Error al eliminar la letra');
      }
      notify(`Letra ${letter} eliminada correctamente`, 'success');
      window.markStructureDirty?.();
      loadImage(`${baseURL}/plot`);
      letterInput.value = '';
    } catch (err) {
      notify(err.message, 'error');
    }
  }

  function viewTree() {
    loadImage(`${baseURL}/plot`);
  }

  // ----- Funciones de guardado/carga con detección de tipo -----
  function getCurrentTreeType() {
    if (btnDigital.classList.contains('active')) return 'digital';
    if (btnSimple.classList.contains('active')) return 'simple-residue';
    if (btnMultiple.classList.contains('active')) return 'multiple-residue';
    return 'digital';
  }

  window.exportTree = async () => {
    const type = getCurrentTreeType();
    const endpoint = `/${type}/export`;
    try {
      const response = await fetch(`http://127.0.0.1:8000${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      if (!response.ok) throw new Error('Error al exportar');
      const snapshot = await response.json();
      // Añadir el tipo manualmente
      snapshot._type = type;
      // Guardar usando descarga directa (muestra el diálogo del navegador)
      const filename = `arbol_${type}.json`;
      const jsonString = JSON.stringify(snapshot, null, 2);
      const blob = new Blob([jsonString], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      window.notifySuccess?.(`Árbol guardado como ${filename}`);
    } catch (err) {
      console.error(err);
      window.notifyError?.('Error al guardar el árbol');
    }
  };

  window.importTree = async () => {
    try {
      const snapshot = await window.saveUtils.loadJSONFile();
      if (!snapshot) throw new Error('No se pudo leer el archivo');
      let type = snapshot._type;
      if (!type) {
        // Fallback: intentar inferir por datos del snapshot (opcional)
        if (snapshot.digital) type = 'digital';
        else if (snapshot.simpleResidue) type = 'simple-residue';
        else throw new Error('Archivo inválido: no se detectó el tipo de árbol');
      }
      if (!['digital', 'simple-residue', 'multiple-residue'].includes(type)) {
        throw new Error(`Tipo desconocido: ${type}`);
      }
      // Cambiar UI al tipo correspondiente
      if (type === 'digital') changeType(TREE_TYPES.digital);
      else if (type === 'simple-residue') changeType(TREE_TYPES.simple);
      else if (type === 'multiple-residue') changeType(TREE_TYPES.multiple);
      
      const importEndpoint = `/${type}/import`;
      const response = await fetch(`http://127.0.0.1:8000${importEndpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ snapshot })
      });
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Error al cargar el árbol');
      }
      await window.refreshStructure();
      window.notifySuccess?.('Árbol cargado correctamente');
    } catch (err) {
      window.notifyError?.(err.message || 'Error al cargar el árbol');
    }
  };

  window.refreshStructure = async () => {
    loadImage(`${baseURL}/plot`);
    if (actionsSection) actionsSection.style.display = 'block';
  };

  // Inicialización
  function initSimulator() {
    btnDigital.addEventListener('click', () => changeType(TREE_TYPES.digital));
    btnSimple.addEventListener('click', () => changeType(TREE_TYPES.simple));
    btnMultiple.addEventListener('click', () => changeType(TREE_TYPES.multiple));

    if (letterInput) {
      letterInput.addEventListener('input', function() {
        enforceSingleLetter(this);
      });
    }

    setupImageSizeSlider();

    createBtn.addEventListener('click', createStructure);
    insertBtn.addEventListener('click', insertLetter);
    searchBtn.addEventListener('click', () => searchLetter(true));
    deleteBtn.addEventListener('click', deleteLetter);
    viewTreeBtn.addEventListener('click', viewTree);

    if (actionsSection) actionsSection.style.display = 'none';
    setActiveTypeButton(currentType);
    toggleMField();
    treeImage.src = '';
  }

  window.initSimulator = initSimulator;
})();