const appState = {
  loadedScripts: new Set(),
  structureDirty: false,
  currentSimulator: null,
};

window.markStructureDirty = () => {
  appState.structureDirty = true;
};

window.resetStructureDirty = () => {
  appState.structureDirty = false;
};

function setActiveRibbonButton(button) {
  const container = button.closest(".ribbon-buttons");

  if (container) {
    container.querySelectorAll(".ribbon-btn").forEach(btn =>
      btn.classList.remove("active")
    );
  }

  button.classList.add("active");
}

/* ---------------- Tabs ---------------- */

function setActiveTab(type) {
  document.querySelectorAll(".tab").forEach(tab => {
    tab.classList.toggle("active", tab.dataset.type === type);
  });
}

function handleTabClick(type) {
  if (appState.structureDirty) {
    window.confirmModal(
      "Has creado una estructura. Si cambias de pestaña, se perderán los datos no guardados. ¿Deseas continuar?",
      () => {
        resetAllServices();
        setActiveTab(type);
        showContent(type);
        window.resetStructureDirty();
      },
      () => {} // cancelar no hace nada
    );
  } else {
    resetAllServices();
    setActiveTab(type);
    showContent(type);
  }
}

/* ---------------- Main switch ---------------- */

function showContent(type) {
  const lvl1 = document.getElementById("ribbon-level-1");
  const lvl2 = document.getElementById("ribbon-level-2");
  const lvl3 = document.getElementById("ribbon-level-3");
  const content = document.getElementById("content");

  lvl1.innerHTML = "";
  lvl2.innerHTML = "";
  lvl3.innerHTML = "";

  if (type === "busquedas") {
    lvl1.innerHTML = `
      <div class="ribbon-buttons">
        <button class="ribbon-btn" id="btn-internas">Internas</button>
        <button class="ribbon-btn" id="btn-externas">Externas</button>
      </div>
    `;

    content.innerHTML = `
      <h2>Búsquedas</h2>
      <p>Selecciona el tipo de búsqueda.</p>
    `;

    document.getElementById("btn-internas")
      .addEventListener("click", function () {
        setActiveRibbonButton(this);
        showBusquedaInterna();
      });

    document.getElementById("btn-externas")
      .addEventListener("click", function () {
        setActiveRibbonButton(this);
        showBusquedaExterna();
      });
  }
}

function showBusquedaInterna() {
  const lvl2 = document.getElementById("ribbon-level-2");
  const lvl3 = document.getElementById("ribbon-level-3");
  const content = document.getElementById("content");

  lvl2.innerHTML = `
    <div class="ribbon-buttons">
      <button class="ribbon-btn" data-page="secuencial">Secuencial</button>
      <button class="ribbon-btn" data-page="binaria">Binaria</button>
      <button class="ribbon-btn" data-page="hash">Hash</button>
      <button class="ribbon-btn" data-page="arbol">Árboles</button>
      <button class="ribbon-btn" data-page="huffman">Huffman</button>
      <button class="ribbon-btn" data-page="indices">Índices</button>
    </div>
  `;

  lvl3.innerHTML = "";

  content.innerHTML = `
    <h2>Búsquedas internas</h2>
    <p>Selecciona un algoritmo.</p>
  `;

  lvl2.querySelectorAll("[data-page]").forEach(btn => {
    btn.addEventListener("click", function () {

      if (appState.structureDirty) {
        window.confirmModal(
          "Has creado una estructura. Si cambias de simulador, se perderán los datos no guardados. ¿Deseas continuar?",
          () => {
            setActiveRibbonButton(this);
            loadExternalPage(this.dataset.page);
            window.resetStructureDirty();
          },
          () => {}
        );
      } else {
        setActiveRibbonButton(this);
        loadExternalPage(this.dataset.page);
      }

    });
  });
}

function showBusquedaExterna() {
  const lvl2 = document.getElementById("ribbon-level-2");
  const lvl3 = document.getElementById("ribbon-level-3");
  const content = document.getElementById("content");

  lvl2.innerHTML = `
    <div class="ribbon-buttons">
      <button class="ribbon-btn" data-page="lineal_externa">Lineal</button>
      <button class="ribbon-btn" data-page="binaria_externa">Binaria</button>
      <button class="ribbon-btn" data-page="hash_externa">Hash</button>
      <button class="ribbon-btn" data-page="hash_dinamica">Dinámica</button>
    </div>
  `;

  lvl3.innerHTML = "";

  content.innerHTML = `
    <h2>Búsquedas externas</h2>
    <p>Selecciona un método.</p>
  `;

  lvl2.querySelectorAll("[data-page]").forEach(btn => {
    btn.addEventListener("click", function () {

      if (appState.structureDirty) {
        window.confirmModal(
          "Has creado una estructura. Si cambias de simulador, se perderán los datos no guardados. ¿Deseas continuar?",
          () => {
            setActiveRibbonButton(this);
            loadExternalPage(this.dataset.page);
            window.resetStructureDirty();
          },
          () => {}
        );
      } else {
        setActiveRibbonButton(this);
        loadExternalPage(this.dataset.page);
      }

    });
  });
}

/* ---------------- Loader ---------------- */

function resetAllServices() {
  const services = ['http://127.0.0.1:8000/linear-search/reset', 'http://127.0.0.1:8000/binary-search/reset'];
  services.forEach(url => {
    fetch(url, { method: 'POST' }).catch(() => {});
  });
}

function loadExternalPage(page) {
  appState.currentSimulator = page;
  resetAllServices();
  window.resetStructureDirty();
  const content = document.getElementById("content");
  content.innerHTML = "<p>Cargando simulador…</p>";

  fetch(`static/${page}.html`)

    .then(res => {
      if (!res.ok) throw new Error();
      return res.text();
    })
    .then(html => {
      content.innerHTML = html;
      const version = Date.now();
      loadExternalCSS(`static/css/${page}.css?v=${version}`);
      loadExternalJS(`static/js/${page}.js?v=${version}`, () => {
        if (typeof window.initSimulator === "function") {
          window.initSimulator();
        }
      });
    })
    .catch(() => {
      content.innerHTML =
        `<p style="color:#d13438">Error cargando ${page}</p>`;
    });
}

function loadExternalCSS(url) {
  if ([...document.styleSheets].some(s => s.href?.includes(url))) return;

  const link = document.createElement("link");
  link.rel = "stylesheet";
  link.href = url;
  document.head.appendChild(link);
}

function loadExternalJS(url, callback) {
  if (appState.loadedScripts.has(url)) {
    if (callback) callback();
    return;
  }

  const script = document.createElement("script");
  script.src = url;
  script.onload = () => {
    appState.loadedScripts.add(url);
    if (callback) callback();
  };
  document.body.appendChild(script);
}

/* ---------------- Impresión sin nueva ventana ---------------- */

function printCurrentView() {
  const content = document.getElementById("content");
  if (!content) return;

  // Guardar el HTML original
  const originalHTML = content.innerHTML;

  // Convertir inputs a texto
  const inputs = content.querySelectorAll('input');
  inputs.forEach(input => {
    const span = document.createElement('span');
    span.textContent = input.value;
    span.className = input.className;
    input.parentNode.replaceChild(span, input);
  });

  // Convertir selects a texto
  const selects = content.querySelectorAll('select');
  selects.forEach(select => {
    const selectedOption = select.options[select.selectedIndex];
    const span = document.createElement('span');
    span.textContent = selectedOption ? selectedOption.text : '';
    span.className = select.className;
    select.parentNode.replaceChild(span, select);
  });

  // Eliminar botones
  const buttons = content.querySelectorAll('button');
  buttons.forEach(btn => btn.remove());

  // Eliminar contenedores de acciones
  const actionSections = content.querySelectorAll('#actions-section, .actions-section');
  actionSections.forEach(section => section.remove());

  // Añadir clase temporal al body para ocultar elementos no deseados
  document.body.classList.add('printing');

  // Llamar a la impresión
  window.print();

  // Restaurar contenido y quitar clase tras un breve retraso
  setTimeout(() => {
    content.innerHTML = originalHTML;
    document.body.classList.remove('printing');
    // Reiniciar el simulador si existe la función
    if (typeof window.initSimulator === "function") {
      window.initSimulator();
    }
  }, 100);
}

/* ---------------- Init ---------------- */

document.addEventListener("DOMContentLoaded", () => {
  handleTabClick("busquedas");

  const printBtn = document.getElementById("print-btn");
  if (printBtn) {
    printBtn.disabled = false;
    printBtn.addEventListener("click", printCurrentView);
  }

  // Setup save/open buttons
  const saveBtn = document.getElementById("save-btn");
  const openBtn = document.getElementById("open-btn");

  if (saveBtn) {
    saveBtn.addEventListener("click", handleSave);
  }

  if (openBtn) {
    openBtn.addEventListener("click", handleOpen);
  }
});

/**
 * Map page names to API endpoints and filenames
 */
function getSimulatorConfig(pageName) {
  const configs = {
    secuencial: { endpoint: '/linear-search/export', filename: 'busqueda_secuencial.json' },
    binaria: { endpoint: '/binary-search/export', filename: 'busqueda_binaria.json' },
    hash: { endpoint: '/hash/export', filename: 'tabla_hash.json' },
    arbol: { endpoint: null, filename: null }, // Has submenu (simple, multiple, digital)
    'simple-residue': { endpoint: '/simple-residue/export', filename: 'arbol_simple.json' },
    'multiple-residue': { endpoint: '/multiple-residue/export', filename: 'arbol_multiple.json' },
    digital: { endpoint: '/digital/export', filename: 'arbol_digital.json' },
    huffman: { endpoint: '/huffman/export', filename: 'arbol_huffman.json' },
    indices: { endpoint: null, filename: null }, // Has multiple index types
    'primary-index': { endpoint: '/search/index/primary/export', filename: 'indice_primario.json' },
    'secondary-index': { endpoint: '/search/index/secondary/export', filename: 'indice_secundario.json' },
    lineal_externa: { endpoint: '/external/linear/export', filename: 'busqueda_lineal_externa.json' },
    binaria_externa: { endpoint: '/external/binary/export', filename: 'busqueda_binaria_externa.json' },
    hash_externa: { endpoint: '/hash-external/export', filename: 'hash_externo.json' },
    hash_dinamica: { endpoint: '/dynamic-hash/export', filename: 'hash_dinamico.json' },
  };
  return configs[pageName];
}

/**
 * Detect current simulator page
 */
function getCurrentSimulatorPage() {
  // Primary: use tracked current simulator
  if (appState.currentSimulator) {
    return appState.currentSimulator;
  }

  // Fallback 1: find active ribbon button
  const activeBtn = document.querySelector('.ribbon-btn.active');
  if (activeBtn && activeBtn.dataset.page) {
    return activeBtn.dataset.page;
  }

  // Fallback 2: detect from loaded scripts
  for (let url of appState.loadedScripts) {
    const match = url.match(/\/js\/(\w+)\.js/);
    if (match) {
      const page = match[1];
      if (page !== 'index' && page !== 'notificaciones' && page !== 'save-utils') {
        return page;
      }
    }
  }

  return null;
}

/**
 * Handle save button click
 */
async function handleSave() {
  const page = getCurrentSimulatorPage();
  
  if (!page) {
    if (window.notifyInfo) {
      window.notifyInfo('Por favor, selecciona un simulador primero.');
    }
    return;
  }

  const config = getSimulatorConfig(page);
  
  if (!config || !config.endpoint) {
    if (window.notifyError) {
      window.notifyError('Este simulador aún no soporta guardar.');
    }
    return;
  }

  try {
    if (!window.saveUtils) {
      if (window.notifyError) {
        window.notifyError('Sistema de guardado no disponible.');
      }
      return;
    }

    await window.saveUtils.saveStructureAs(config.endpoint, config.filename);
    window.resetStructureDirty?.();
  } catch (error) {
    console.error('Save error:', error);
  }
}

/**
 * Handle open button click
 */
async function handleOpen() {
  const page = getCurrentSimulatorPage();
  
  if (!page) {
    if (window.notifyInfo) {
      window.notifyInfo('Por favor, selecciona un simulador primero.');
    }
    return;
  }

  const config = getSimulatorConfig(page);
  
  if (!config || !config.endpoint) {
    if (window.notifyError) {
      window.notifyError('Este simulador aún no soporta abrir archivos.');
    }
    return;
  }

  try {
    if (!window.saveUtils) {
      if (window.notifyError) {
        window.notifyError('Sistema de carga no disponible.');
      }
      return;
    }

    // Extract endpoint without /export to get import endpoint
    const importEndpoint = config.endpoint.replace('/export', '/import');
    const state = await window.saveUtils.loadStructure(importEndpoint);
    
    // Give backend a moment to update state, then reload simulator
    await new Promise(resolve => setTimeout(resolve, 100));
    
    if (typeof window.initSimulator === 'function') {
      window.initSimulator();
    }
    
    window.notifySuccess('Estructura cargada correctamente.');
    window.resetStructureDirty?.();
  } catch (error) {
    console.error('Open error:', error);
    if (window.notifyError) {
      window.notifyError('Error al cargar la estructura: ' + (error.message || 'Error desconocido'));
    }
  }
}