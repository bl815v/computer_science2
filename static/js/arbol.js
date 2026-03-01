/* eslint-disable no-console */
(() => {
  "use strict";

  const TREE_TYPES = {
    digital: 'digital',
    simple: 'simple-residue',
    multiple: 'multiple-residue'
  };

  const TREE_ENDPOINTS = {
    digital: API_CONFIG.ENDPOINTS.DIGITAL_TREE,
    simple: API_CONFIG.ENDPOINTS.SIMPLE_RESIDUE,
    multiple: API_CONFIG.ENDPOINTS.MULTIPLE_RESIDUE
  };

  let currentType = TREE_TYPES.digital;
  let baseURL = API_CONFIG.BASE_URL + TREE_ENDPOINTS.digital;

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
  const operationsCard = document.getElementById('operations-card');
  const sliderCard = document.getElementById('slider-card');

  const FIXED_SIZE = 1000;
  const FIXED_DIGITS = 5;
  const FIXED_M = 2;

  function updateBaseURL() {
    baseURL = API_CONFIG.BASE_URL + TREE_ENDPOINTS[currentType];
  }

  function toggleMField() {
    if (mField) {
      mField.style.display = currentType === TREE_TYPES.multiple ? 'block' : 'none';
    }
  }

  function setActiveTypeButton(type) {
    [btnDigital, btnSimple, btnMultiple].forEach(btn => {
      if (btn) btn.classList.remove('active');
    });
    if (type === TREE_TYPES.digital && btnDigital) btnDigital.classList.add('active');
    if (type === TREE_TYPES.simple && btnSimple) btnSimple.classList.add('active');
    if (type === TREE_TYPES.multiple && btnMultiple) btnMultiple.classList.add('active');
  }

  function changeType(type) {
    if (type === currentType || !type) return;
    currentType = type;
    updateBaseURL();
    setActiveTypeButton(type);
    toggleMField();
    if (operationsCard) operationsCard.style.display = 'none';
    if (sliderCard) sliderCard.style.display = 'none';
    if (treeImage) treeImage.src = '';
  }

  function isValidLetter(letter) {
    return /^[A-ZÑ]$/i.test(letter);
  }

  function normalizeLetter(letter) {
    return letter.toUpperCase();
  }

  function enforceSingleLetter(input) {
    if (!input) return;
    
    const raw = input.value;
    const singleValidLetterRegex = /^[A-ZÑ]$/i;

    if (raw === '') return;

    if (singleValidLetterRegex.test(raw)) {
      input.value = raw.toUpperCase();
      return;
    }

    const cleaned = raw.toUpperCase().replace(/[^A-ZÑ]/g, '');
    const newValue = cleaned.length > 0 ? cleaned.charAt(0) : '';
    input.value = newValue;

    if (raw !== '') {
      window.notifyError('Solo se permite una letra del alfabeto español (A-Z, Ñ)', true);
    }
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
    if (!treeImage) return;
    const separator = url.includes('?') ? '&' : '?';
    treeImage.src = `${url}${separator}t=${Date.now()}`;
  }

  async function createStructure() {
    if (!createBtn) return;
    
    const body = {
      size: FIXED_SIZE,
      digits: FIXED_DIGITS
    };
    if (currentType === TREE_TYPES.multiple && mInput) {
      body.m = parseInt(mInput.value) || FIXED_M;
    }

    try {
      const res = await fetchWithTimeout(`${baseURL}/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Error al crear la estructura');
      }
      window.notifySuccess('Estructura creada correctamente', true);
      if (operationsCard) operationsCard.style.display = 'block';
      if (sliderCard) sliderCard.style.display = 'block';
      loadImage(`${baseURL}/plot`);
    } catch (err) {
      window.notifyError(err.message, true);
    }
  }

  async function insertLetter() {
    if (!letterInput) return;
    
    const letterRaw = letterInput.value.trim();
    if (!isValidLetter(letterRaw)) {
      window.notifyError('Ingresa una sola letra válida (A-Z, Ñ)', true);
      return;
    }
    const letter = normalizeLetter(letterRaw);

    try {
      const res = await fetchWithTimeout(`${baseURL}/insert`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ letter })
      });
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Error al insertar la letra');
      }
      window.notifySuccess(`Letra ${letter} insertada correctamente`, true);
      loadImage(`${baseURL}/plot`);
      letterInput.value = '';
    } catch (err) {
      window.notifyError(err.message, true);
    }
  }

  async function searchLetter(showHighlighted = true) {
    if (!letterInput) return;
    
    const letterRaw = letterInput.value.trim();
    if (!isValidLetter(letterRaw)) {
      window.notifyError('Ingresa una sola letra válida (A-Z, Ñ)', true);
      return;
    }
    const letter = normalizeLetter(letterRaw);

    try {
      const searchRes = await fetchWithTimeout(`${baseURL}/search/${encodeURIComponent(letter)}`);
      if (!searchRes.ok) {
        if (searchRes.status === 404) {
          window.notifyError(`Letra ${letter} no encontrada`, true);
          loadImage(`${baseURL}/plot`);
        } else {
          const errorData = await searchRes.json().catch(() => ({}));
          throw new Error(errorData.detail || 'Error en la búsqueda');
        }
        return;
      }
      window.notifySuccess(`Letra ${letter} encontrada`, true);
      if (showHighlighted) {
        loadImage(`${baseURL}/search-plot/${encodeURIComponent(letter)}`);
      } else {
        loadImage(`${baseURL}/plot`);
      }
    } catch (err) {
      window.notifyError(err.message, true);
    }
  }

  async function deleteLetter() {
    if (!letterInput) return;
    
    const letterRaw = letterInput.value.trim();
    if (!isValidLetter(letterRaw)) {
      window.notifyError('Ingresa una sola letra válida (A-Z, Ñ)', true);
      return;
    }
    const letter = normalizeLetter(letterRaw);

    try {
      const res = await fetchWithTimeout(`${baseURL}/delete/${encodeURIComponent(letter)}`, {
        method: 'DELETE'
      });
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Error al eliminar la letra');
      }
      window.notifySuccess(`Letra ${letter} eliminada correctamente`, true);
      loadImage(`${baseURL}/plot`);
      letterInput.value = '';
    } catch (err) {
      window.notifyError(err.message, true);
    }
  }

  function viewTree() {
    loadImage(`${baseURL}/plot`);
  }

  function initSimulator() {
    if (!btnDigital || !btnSimple || !btnMultiple || !createBtn) return;

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
    if (insertBtn) insertBtn.addEventListener('click', insertLetter);
    if (searchBtn) searchBtn.addEventListener('click', () => searchLetter(true));
    if (deleteBtn) deleteBtn.addEventListener('click', deleteLetter);
    if (viewTreeBtn) viewTreeBtn.addEventListener('click', viewTree);

    if (operationsCard) operationsCard.style.display = 'none';
    if (sliderCard) sliderCard.style.display = 'none';
    setActiveTypeButton(currentType);
    toggleMField();
    if (treeImage) treeImage.src = '';
  }

  window.initSimulator = initSimulator;
})();