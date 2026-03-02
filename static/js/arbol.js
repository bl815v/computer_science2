/* eslint-disable no-console */
(() => {
  "use strict";

  // Tipos de árbol y sus bases de URL (los endpoints siguen en inglés)
  const TREE_TYPES = {
    digital: 'digital',
    simple: 'simple-residue',
    multiple: 'multiple-residue'
  };

  let currentType = TREE_TYPES.digital;
  let baseURL = `http://127.0.0.1:8000/${currentType}`;

  // Elementos del DOM
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

  // Valores fijos para la creación
  const FIXED_SIZE = 1000;
  const FIXED_DIGITS = 5;
  const FIXED_M = 2;

  // --- Utilidades ---
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
    // Ocultar operaciones hasta que se cree la nueva estructura
    if (actionsSection) actionsSection.style.display = 'none';
    treeImage.src = '';
  }

  // Validación de letra (solo una del alfabeto español)
  function isValidLetter(letter) {
    return /^[A-ZÑ]$/i.test(letter);
  }

  function normalizeLetter(letter) {
    return letter.toUpperCase();
  }

  // --- Validación en tiempo real (mejorada, sin molestias) ---
  function enforceSingleLetter(input) {
    const raw = input.value;
    // Expresión regular para una sola letra válida (mayúscula o minúscula)
    const singleValidLetterRegex = /^[A-ZÑ]$/i;

    // Si está vacío, no hacemos nada
    if (raw === '') return;

    // Si es una sola letra válida, normalizamos a mayúscula sin notificación
    if (singleValidLetterRegex.test(raw)) {
      input.value = raw.toUpperCase();
      return;
    }

    // Si no es válido (número, símbolo, múltiples caracteres), limpiamos y mostramos error
    // Extraemos solo letras válidas y tomamos la primera si existe
    const cleaned = raw.toUpperCase().replace(/[^A-ZÑ]/g, '');
    const newValue = cleaned.length > 0 ? cleaned.charAt(0) : '';
    input.value = newValue;

    // Mostramos notificación solo si el usuario había ingresado algo no vacío
    window.notifyError?.('Solo se permite una letra del alfabeto español (A-Z, Ñ)');
  }

  // Control deslizante para el tamaño de la imagen
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

  // Notificaciones
  function notify(message, type = 'info') {
    if (type === 'success') window.notifySuccess?.(message);
    else if (type === 'error') window.notifyError?.(message);
    else window.notifyInfo?.(message);
  }

  // --- API Calls ---
  async function createStructure() {
    const body = {
      size: FIXED_SIZE,
      digits: FIXED_DIGITS
    };
    if (currentType === TREE_TYPES.multiple) {
      body.m = parseInt(mInput.value) || FIXED_M;
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
      // Mostrar las operaciones y el slider
      if (actionsSection) actionsSection.style.display = 'block';
      loadImage(`${baseURL}/plot`);
    } catch (err) {
      notify(err.message, 'error');
    }
  }

  async function insertLetter() {
    const letterRaw = letterInput.value.trim();
    if (!isValidLetter(letterRaw)) {
      return notify('Ingresa una sola letra válida (A-Z, Ñ)', 'error');
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
      loadImage(`${baseURL}/plot`);
      letterInput.value = '';
    } catch (err) {
      notify(err.message, 'error');
    }
  }

  async function searchLetter(showHighlighted = true) {
    const letterRaw = letterInput.value.trim();
    if (!isValidLetter(letterRaw)) {
      return notify('Ingresa una sola letra válida (A-Z, Ñ)', 'error');
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
      return notify('Ingresa una sola letra válida (A-Z, Ñ)', 'error');
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
      loadImage(`${baseURL}/plot`);
      letterInput.value = '';
    } catch (err) {
      notify(err.message, 'error');
    }
  }

  function viewTree() {
    loadImage(`${baseURL}/plot`);
  }

  // --- Inicialización ---
  function initSimulator() {
    // Eventos de cambio de tipo
    btnDigital.addEventListener('click', () => changeType(TREE_TYPES.digital));
    btnSimple.addEventListener('click', () => changeType(TREE_TYPES.simple));
    btnMultiple.addEventListener('click', () => changeType(TREE_TYPES.multiple));

    // Validación en tiempo real en el campo de letra
    if (letterInput) {
      letterInput.addEventListener('input', function() {
        enforceSingleLetter(this);
      });
    }

    // Configurar slider de tamaño
    setupImageSizeSlider();

    // Botones de acción
    createBtn.addEventListener('click', createStructure);
    insertBtn.addEventListener('click', insertLetter);
    searchBtn.addEventListener('click', () => searchLetter(true));
    deleteBtn.addEventListener('click', deleteLetter);
    viewTreeBtn.addEventListener('click', viewTree);

    // Estado inicial: operaciones ocultas
    if (actionsSection) actionsSection.style.display = 'none';
    setActiveTypeButton(currentType);
    toggleMField();
    treeImage.src = '';
  }

  window.initSimulator = initSimulator;
})();