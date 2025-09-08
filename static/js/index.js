// Objeto para controlar el estado de la aplicación
const appState = {
    currentTab: null,
    loadedScripts: new Set()
};

/** 
 * Muestra contenido basado en el tipo seleccionado
 * @param {string} type El tipo de simulación a mostrar
 */
function showContent(type) {
    const ribbonElement = document.getElementById('ribbon');
    const contentElement = document.getElementById('content');
    appState.currentTab = type;
    
    if (type === 'busqueda_interna') {
        ribbonElement.innerHTML = `
            <div class="ribbon-buttons">
                <button class="ribbon-btn" data-page="secuencial">Secuencial</button>
                <button class="ribbon-btn" data-page="binaria">Binaria</button>
                <button class="ribbon-btn" data-page="hashing">Hashing</button>
            </div>
        `;
        contentElement.innerHTML = '<h2>Selecciona un algoritmo en la cinta de opciones</h2>';
        attachRibbonEvents();
    } else if (type === 'busqueda_externa') {
        ribbonElement.innerHTML = '';
        contentElement.innerHTML = '<h2>Simulador de búsquedas externas próximamente...</h2>';
    } else if (type === 'grafos') {
        ribbonElement.innerHTML = '';
        contentElement.innerHTML = '<h2>Simulador de grafos próximamente...</h2>';
    }
}

/**
 * Establece la pestaña activa basada en el tipo seleccionado
 * @param {string} selectedType El tipo de pestaña seleccionada
 */
function setActiveTab(selectedType) {
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach((tab) => {
        if (tab.getAttribute('data-type') === selectedType) {
            tab.classList.add('active');
        } else {
            tab.classList.remove('active');
        }
    });
}

/**
 * Maneja el evento de clic en una pestaña
 * @param {string} type El tipo de pestaña clickeada
 */
function handleTabClick(type) {
    setActiveTab(type);
    showContent(type);
}

/**
 * Adjunta eventos de clic a los botones de la cinta
 */
function attachRibbonEvents() {
    const buttons = document.querySelectorAll('.ribbon-btn');
    const contentElement = document.getElementById('content');
    
    buttons.forEach((button) => {
        button.addEventListener('click', () => {
            const page = button.getAttribute('data-page');
            loadExternalPage(page);
        });
    });
}

/**
 * Carga una página externa y sus recursos
 * @param {string} page Nombre de la página a cargar (sin extensión)
 */
function loadExternalPage(page) {
    const contentElement = document.getElementById('content');
    
    // Mostrar mensaje de carga
    contentElement.innerHTML = '<p>Cargando simulador...</p>';
    
    // Cargar el HTML
    fetch(`static/${page}.html`)
        .then((response) => {
            if (!response.ok) {
                throw new Error('Page not found');
            }
            return response.text();
        })
        .then((html) => {
            contentElement.innerHTML = html;
            
            // Cargar CSS específico si existe
            loadExternalCSS(`static/css/${page}.css`);
            
            // Cargar JS específico si existe
            loadExternalJS(`static/js/${page}.js`, () => {
                // Inicializar el script después de cargar
                if (typeof initSimulator === 'function') {
                    initSimulator();
                }
            });
        })
        .catch(() => {
            contentElement.innerHTML = `<p style="color:red;">Error cargando ${page}.html</p>`;
        });
}

/**
 * Carga un archivo CSS externo dinámicamente
 * @param {string} url URL del archivo CSS
 */
function loadExternalCSS(url) {
    // Verificar si el CSS ya está cargado
    const existingLinks = document.querySelectorAll('link[rel="stylesheet"]');
    for (let link of existingLinks) {
        if (link.getAttribute('href') === url) {
            return; // Ya está cargado, no hacer nada
        }
    }
    
    // Crear nuevo elemento link
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = url;
    document.head.appendChild(link);
}

/**
 * Carga un archivo JS externo dinámicamente
 * @param {string} url URL del archivo JS
 * @param {function} callback Función a ejecutar después de cargar el script
 */
function loadExternalJS(url, callback) {
    // Verificar si el JS ya está cargado
    if (appState.loadedScripts.has(url)) {
        if (callback) callback();
        return;
    }
    
    // Crear nuevo elemento script
    const script = document.createElement('script');
    script.src = url;
    script.onload = () => {
        appState.loadedScripts.add(url);
        if (callback) callback();
    };
    script.onerror = () => {
        console.error(`Error loading script: ${url}`);
        if (callback) callback();
    };
    document.body.appendChild(script);
}

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    // Establecer la pestaña inicial si es necesario
    // handleTabClick('busqueda_interna');
});