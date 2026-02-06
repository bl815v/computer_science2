const appState = {
    currentTab: null,
    loadedScripts: new Set()
};

/** 
 * Display content based on the selected type
 * @param {string} type The type of simulation to show
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
 * Sets the active tab based on the selected type
 * @param {string} selectedType The type of tab selected
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
 * Handle the click event on a tab
 * @param {string} type The type of tab clicked
 */
function handleTabClick(type) {
    setActiveTab(type);
    showContent(type);
}

/**
 * Attach click events to ribbon buttons
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
 * Attach click events to ribbon buttons
 * @param {string} page Name of the page to load (without extension)
 */
function loadExternalPage(page) {
    const contentElement = document.getElementById('content');

    contentElement.innerHTML = '<p>Cargando simulador...</p>';

    fetch(`static/${page}.html`)
        .then((response) => {
            if (!response.ok) {
                throw new Error('Page not found');
            }
            return response.text();
        })
        .then((html) => {
            contentElement.innerHTML = html;

            loadExternalCSS(`static/css/${page}.css`);

            loadExternalJS(`static/js/${page}.js`, () => {
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
 * Load an external CSS file dynamically
 * @param {string} url CSS file URLb
 */
function loadExternalCSS(url) {
    const existingLinks = document.querySelectorAll('link[rel="stylesheet"]');
    for (let link of existingLinks) {
        if (link.getAttribute('href') === url) {
            return;
        }
    }

    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = url;
    document.head.appendChild(link);
}

/**
 * Load an external JS file dynamically
 * @param {string} url JS file URL
 * @param {function} callback Function to execute after loading the script
 */
function loadExternalJS(url, callback) {
    if (appState.loadedScripts.has(url)) {
        if (callback) callback();
        return;
    }

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

document.addEventListener('DOMContentLoaded', function () {
    // Set the initial tab if necessary
    // handleTabClick('busqueda_interna');
});