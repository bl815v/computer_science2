// index.js mejorado
const appState = {
  loadedScripts: new Set(),
  loadedCSS: new Set(),
  currentPage: null,
  currentTab: 'busquedas'
};

function setActiveRibbonButton(button) {
  if (!button) return;
  
  // Buscar el contenedor de botones más cercano
  const container = button.closest(".ribbon-buttons");
  if (container) {
    container.querySelectorAll(".ribbon-btn").forEach(btn =>
      btn.classList.remove("active")
    );
  }
  button.classList.add("active");
}

function setActiveTab(type) {
  document.querySelectorAll(".tab").forEach(tab => {
    tab.classList.toggle("active", tab.dataset.type === type);
  });
  appState.currentTab = type;
}

function handleTabClick(type) {
  setActiveTab(type);
  showContent(type);
}

function showContent(type) {
  const ribbon = document.getElementById("ribbon");
  const content = document.getElementById("content");
  
  if (!ribbon || !content) return;
  
  // Limpiar ribbon
  ribbon.innerHTML = "";
  
  if (type === "busquedas") {
    // Nivel 1: Internas/Externas
    const level1 = document.createElement('div');
    level1.className = 'ribbon-row';
    level1.innerHTML = `
      <div class="ribbon-buttons">
        <button class="ribbon-btn" id="btn-internas">Internas</button>
        <button class="ribbon-btn" id="btn-externas">Externas</button>
      </div>
    `;
    ribbon.appendChild(level1);
    
    content.innerHTML = `
      <h2>Búsquedas</h2>
      <p>Selecciona el tipo de búsqueda.</p>
    `;
    
    document.getElementById("btn-internas")?.addEventListener("click", function() {
      setActiveRibbonButton(this);
      showBusquedaInterna();
    });
    
    document.getElementById("btn-externas")?.addEventListener("click", function() {
      setActiveRibbonButton(this);
      showBusquedaExterna();
    });
  } else if (type === "grafos") {
    content.innerHTML = `
      <h2>Grafos</h2>
      <p>Sección en desarrollo...</p>
    `;
  }
}

function showBusquedaInterna() {
  const ribbon = document.getElementById("ribbon");
  const content = document.getElementById("content");
  
  if (!ribbon || !content) return;
  
  // Limpiar niveles inferiores pero mantener el primero
  while (ribbon.children.length > 1) {
    ribbon.removeChild(ribbon.lastChild);
  }
  
  // Nivel 2: Algoritmos de búsqueda
  const level2 = document.createElement('div');
  level2.className = 'ribbon-row';
  level2.innerHTML = `
    <div class="ribbon-buttons">
      <button class="ribbon-btn" data-page="secuencial">Secuencial</button>
      <button class="ribbon-btn" data-page="binaria">Binaria</button>
      <button class="ribbon-btn" data-page="hash">Hash</button>
      <button class="ribbon-btn" data-page="arbol">Árboles</button>
    </div>
  `;
  ribbon.appendChild(level2);
  
  content.innerHTML = `
    <h2>Búsquedas internas</h2>
    <p>Selecciona un algoritmo.</p>
  `;
  
  level2.querySelectorAll("[data-page]").forEach(btn => {
    btn.addEventListener("click", function() {
      setActiveRibbonButton(this);
      loadExternalPage(this.dataset.page);
    });
  });
}

function showBusquedaExterna() {
  const ribbon = document.getElementById("ribbon");
  const content = document.getElementById("content");
  
  if (!ribbon || !content) return;
  
  // Limpiar niveles inferiores
  while (ribbon.children.length > 1) {
    ribbon.removeChild(ribbon.lastChild);
  }
  
  content.innerHTML = `
    <h2>Búsquedas externas</h2>
    <p>Simulador próximamente…</p>
  `;
}

function loadExternalPage(page) {
  const content = document.getElementById("content");
  if (!content) return;
  
  appState.currentPage = page;
  content.innerHTML = "<p>Cargando simulador…</p>";
  
  const version = Date.now();
  
  fetch(`static/${page}.html`)
    .then(res => {
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return res.text();
    })
    .then(html => {
      content.innerHTML = html;
      
      // Cargar CSS específico
      loadExternalCSS(`static/css/${page}.css?v=${version}`);
      
      // Cargar JS específico
      loadExternalJS(`static/js/${page}.js?v=${version}`, () => {
        if (typeof window.initSimulator === "function") {
          // Pequeño retraso para asegurar que el DOM está listo
          setTimeout(() => {
            try {
              window.initSimulator();
            } catch (error) {
              console.error(`Error inicializando ${page}:`, error);
              window.notifyError(`Error al cargar el simulador: ${error.message}`);
            }
          }, 50);
        }
      });
    })
    .catch(error => {
      content.innerHTML = `
        <div style="color:#d13438; text-align:center; padding:20px;">
          <h3>Error cargando ${page}</h3>
          <p>${error.message}</p>
        </div>
      `;
    });
}

function loadExternalCSS(url) {
  // Verificar si ya está cargado
  const exists = [...document.styleSheets].some(
    s => s.href && s.href.includes(url.split('?')[0])
  );
  
  if (exists || appState.loadedCSS.has(url.split('?')[0])) return;
  
  const link = document.createElement("link");
  link.rel = "stylesheet";
  link.href = url;
  link.onload = () => appState.loadedCSS.add(url.split('?')[0]);
  link.onerror = () => console.warn(`No se pudo cargar CSS: ${url}`);
  document.head.appendChild(link);
}

function loadExternalJS(url, callback) {
  const baseUrl = url.split('?')[0];
  
  if (appState.loadedScripts.has(baseUrl)) {
    if (callback) callback();
    return;
  }
  
  const script = document.createElement("script");
  script.src = url;
  script.onload = () => {
    appState.loadedScripts.add(baseUrl);
    if (callback) callback();
  };
  script.onerror = () => {
    console.error(`Error cargando script: ${url}`);
    window.notifyError(`Error al cargar el módulo ${baseUrl.split('/').pop()}`);
  };
  document.body.appendChild(script);
}

// Inicialización
document.addEventListener("DOMContentLoaded", () => {
  handleTabClick("busquedas");
});