/**
 * Displays content based on the selected type.
 * @param {string} type The type of simulation to display.
 */
function showContent(type) {
  const ribbonElement = document.getElementById('ribbon');
  const contentElement = document.getElementById('content');

  if (type === 'busqueda_interna') {
    ribbonElement.innerHTML = `
      <div class="ribbon-buttons">
        <button class="ribbon-btn" data-page="/static/secuencial.html">Secuencial</button>
        <button class="ribbon-btn" data-page="/static/binaria.html">Binaria</button>
        <button class="ribbon-btn" data-page="/static/hashing.html">Hashing</button>
      </div>
    `;
    contentElement.innerHTML =
      '<h2>Selecciona un algoritmo en la cinta de opciones</h2>';

    attachRibbonEvents();
  } else if (type === 'busqueda_externa') {
    ribbonElement.innerHTML = '';
    contentElement.innerHTML =
      '<h2>Simulador de búsquedas externas próximamente...</h2>';
  } else if (type === 'grafos') {
    ribbonElement.innerHTML = '';
    contentElement.innerHTML =
      '<h2>Simulador de grafos próximamente...</h2>';
  }
}

/**
 * Sets the active tab based on the selected type.
 * @param {string} selectedType The type of tab selected.
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
 * Handles tab click event.
 * @param {string} type The type of tab clicked.
 */
function handleTabClick(type) {
  setActiveTab(type);
  showContent(type);
}

/**
 * Attaches click events to ribbon buttons.
 */
function attachRibbonEvents() {
  const buttons = document.querySelectorAll('.ribbon-btn');
  const contentElement = document.getElementById('content');

  buttons.forEach((button) => {
    button.addEventListener('click', () => {
      const page = button.getAttribute('data-page');

      fetch(page)
        .then((response) => {
          if (!response.ok) {
            throw new Error('Page not found');
          }
          return response.text();
        })
        .then((html) => {
          contentElement.innerHTML = html;
        })
        .catch(() => {
          contentElement.innerHTML =
            `<p style="color:red;">Error cargando ${page}</p>`;
        });
    });
  });
}
