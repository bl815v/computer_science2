const appState = {
  loadedScripts: new Set(),
  structureDirty: false,
  currentSimulator: null,
};

window.simulatorRegistry = window.simulatorRegistry || {
  initializers: {},
  teardowns: {},
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

function teardownCurrentSimulator() {
  const currentPage = appState.currentSimulator;
  const teardown = currentPage ? window.simulatorRegistry.teardowns[currentPage] : null;
  if (typeof teardown === 'function') {
    try {
      teardown();
    } catch (error) {
      console.error('Simulator teardown error:', error);
    }
  }
  appState.currentSimulator = null;
}

function handleTabClick(type) {
  if (appState.structureDirty) {
    window.confirmModal(
      "Has creado una estructura. Si cambias de pestaña, se perderán los datos no guardados. ¿Deseas continuar?",
      () => {
        teardownCurrentSimulator();
        resetAllServices();
        setActiveTab(type);
        showContent(type);
        window.resetStructureDirty();
      },
      () => {} // cancelar no hace nada
    );
  } else {
    teardownCurrentSimulator();
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
  } else if (type === "grafos") {
    lvl1.innerHTML = `
      <div class="ribbon-buttons">
        <button class="ribbon-btn" data-category="operations">Operaciones</button>
        <button class="ribbon-btn" data-category="traversals">Árboles</button>
        <button class="ribbon-btn" data-category="paths">Caminos</button>
        <button class="ribbon-btn" data-category="coloring">Coloreado</button>
      </div>
    `;
    lvl2.innerHTML = "";
    lvl3.innerHTML = "";
    content.innerHTML = `
      <h2>Grafos</h2>
      <p>Selecciona una categoría para abrir el simulador de grafos y mostrar sólo las herramientas relevantes.</p>
    `;

    lvl1.querySelectorAll('[data-category]').forEach(btn => {
      btn.addEventListener('click', function () {
        if (appState.structureDirty) {
          window.confirmModal(
            'Has creado una estructura. Si cambias de categoría, se perderán los datos no guardados. ¿Deseas continuar?',
            () => {
              setActiveRibbonButton(this);
              selectGraphCategory(this.dataset.category);
              window.resetStructureDirty();
            },
            () => {}
          );
        } else {
          setActiveRibbonButton(this);
          selectGraphCategory(this.dataset.category);
        }
      });
    });
  }
}

function selectGraphCategory(category) {
  window.graphInitialCategory = category;
  loadExternalPage('graph');
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
      <button class="ribbon-btn" data-page="indices">Índices</button>
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
  const previousPage = appState.currentSimulator;
  const teardown = previousPage ? window.simulatorRegistry.teardowns[previousPage] : null;
  if (typeof teardown === 'function') {
    try {
      teardown();
    } catch (error) {
      console.error('Simulator teardown error:', error);
    }
  }

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
        const initializer = window.simulatorRegistry.initializers[page] || window.initSimulator;
        if (typeof initializer === "function") {
          initializer();
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
  const normalizedUrl = url.replace(/\?.*$/, '');
  if (appState.loadedScripts.has(normalizedUrl)) {
    if (callback) callback();
    return;
  }

  const script = document.createElement('script');
  script.src = url;
  script.onload = () => {
    appState.loadedScripts.add(normalizedUrl);
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

/* ---------------- Save / Open ---------------- */

/**
 * Map page names to API endpoints and filenames
 */
function getSimulatorConfig(pageName) {
  const configs = {
    secuencial: { endpoint: '/linear-search/export', filename: 'busqueda_secuencial.json' },
    binaria: { endpoint: '/binary-search/export', filename: 'busqueda_binaria.json' },
    hash: { endpoint: '/hash/export', filename: 'tabla_hash.json' },
    arbol: { endpoint: null, filename: null }, // handled separately
    huffman: { endpoint: '/huffman/export', filename: 'arbol_huffman.json' },
    indices: { endpoint: null, filename: null }, // handled separately
    lineal_externa: { endpoint: '/external/linear/export', filename: 'busqueda_lineal_externa.json' },
    binaria_externa: { endpoint: '/external/binary/export', filename: 'busqueda_binaria_externa.json' },
    hash_externa: { endpoint: '/hash-external/export', filename: 'hash_externo.json' },
    hash_dinamica: { endpoint: '/dynamic-hash/export', filename: 'hash_dinamico.json' },
    graph: { endpoint: '/graphs/export', filename: 'grafo.json' },
  };
  return configs[pageName];
}

/**
 * Detect current simulator page
 */
function getCurrentSimulatorPage() {
  if (appState.currentSimulator) {
    return appState.currentSimulator;
  }

  const activeBtn = document.querySelector('.ribbon-btn.active');
  if (activeBtn && activeBtn.dataset.page) {
    return activeBtn.dataset.page;
  }

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

  // Caso especial para árboles
  if (page === 'arbol') {
    if (typeof window.exportTree === 'function') {
      try {
        await window.exportTree();
        window.resetStructureDirty?.();
      } catch (err) {
        console.error('Export error:', err);
      }
    } else {
      if (window.notifyError) {
        window.notifyError('El simulador de árboles no soporta guardado todavía.');
      }
    }
    return;
  }

  // Caso especial para índices
  if (page === 'indices') {
    if (typeof window.exportIndex === 'function') {
      try {
        await window.exportIndex();
        window.resetStructureDirty?.();
      } catch (err) {
        console.error('Export error:', err);
      }
    } else {
      if (window.notifyError) {
        window.notifyError('El simulador de índices no soporta guardado todavía.');
      }
    }
    return;
  }

  // Caso especial para grafos
  if (page === 'graph') {
    if (typeof window.exportGraph === 'function') {
      try {
        await window.exportGraph();
        window.resetStructureDirty?.();
      } catch (err) {
        console.error('Export error:', err);
      }
    } else {
      if (window.notifyError) {
        window.notifyError('El simulador de grafos no soporta guardado todavía.');
      }
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

  // Caso especial para árboles
  if (page === 'arbol') {
    if (typeof window.importTree === 'function') {
      try {
        await window.importTree();
        // Refrescar visualización después de importar
        if (typeof window.refreshStructure === 'function') {
          await window.refreshStructure();
        }
        window.resetStructureDirty?.();
      } catch (err) {
        console.error('Import error:', err);
        if (window.notifyError) {
          window.notifyError('Error al cargar el árbol: ' + (err.message || 'Error desconocido'));
        }
      }
    } else {
      if (window.notifyError) {
        window.notifyError('El simulador de árboles no soporta cargar archivos todavía.');
      }
    }
    return;
  }

  // Caso especial para índices
  if (page === 'indices') {
    if (typeof window.importIndex === 'function') {
      try {
        await window.importIndex();
        // Refrescar visualización después de importar
        if (typeof window.refreshStructure === 'function') {
          await window.refreshStructure();
        }
        window.resetStructureDirty?.();
      } catch (err) {
        console.error('Import error:', err);
        if (window.notifyError) {
          window.notifyError('Error al cargar el índice: ' + (err.message || 'Error desconocido'));
        }
      }
    } else {
      if (window.notifyError) {
        window.notifyError('El simulador de índices no soporta cargar archivos todavía.');
      }
    }
    return;
  }

  // Caso especial para grafos
  if (page === 'graph') {
    if (typeof window.importGraph === 'function') {
      try {
        await window.importGraph();
        if (typeof window.refreshStructure === 'function') {
          await window.refreshStructure();
        }
        window.resetStructureDirty?.();
      } catch (err) {
        console.error('Import error:', err);
        if (window.notifyError) {
          window.notifyError('Error al cargar el grafo: ' + (err.message || 'Error desconocido'));
        }
      }
    } else {
      if (window.notifyError) {
        window.notifyError('El simulador de grafos no soporta cargar archivos todavía.');
      }
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
    
    // Give backend sufficient time to update state before reinitializing
    await new Promise(resolve => setTimeout(resolve, 300));
    
    // Refresh the current simulator's UI (if available)
    if (typeof window.refreshStructure === 'function') {
      await window.refreshStructure();
    } else if (typeof window.initSimulator === 'function') {
      // Fallback: reinitialize completely
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
    saveBtn.disabled = false;
    saveBtn.addEventListener("click", handleSave);
  }

  if (openBtn) {
    openBtn.disabled = false;
    openBtn.addEventListener("click", handleOpen);
  }
});