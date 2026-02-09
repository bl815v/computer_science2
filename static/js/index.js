const appState = {
  loadedScripts: new Set(),
};

/* ---------------- Tabs ---------------- */

function setActiveTab(type) {
  document.querySelectorAll(".tab").forEach(tab => {
    tab.classList.toggle("active", tab.dataset.type === type);
  });
}

function handleTabClick(type) {
  setActiveTab(type);
  showContent(type);
}

/* ---------------- Main switch ---------------- */

function showContent(type) {
  const ribbon = document.getElementById("ribbon");
  const content = document.getElementById("content");

  if (type === "busquedas") {
    ribbon.innerHTML = `
      <div class="ribbon-buttons">
        <button class="ribbon-btn" id="btn-internas">
          Internas
        </button>
        <button class="ribbon-btn" id="btn-externas">
          Externas
        </button>
      </div>
    `;

    content.innerHTML = `
      <h2>Búsquedas</h2>
      <p>Selecciona el tipo de búsqueda.</p>
    `;

    document.getElementById("btn-internas")
      .addEventListener("click", showBusquedaInterna);

    document.getElementById("btn-externas")
      .addEventListener("click", showBusquedaExterna);
  }

  if (type === "grafos") {
    ribbon.innerHTML = "";
    content.innerHTML = `
      <h2>Grafos</h2>
      <p>Simulador próximamente…</p>
    `;
  }
}

/* ---------------- Búsquedas ---------------- */

function showBusquedaInterna() {
  const ribbon = document.getElementById("ribbon");
  const content = document.getElementById("content");

  ribbon.innerHTML = `
    <div class="ribbon-buttons">
      <button class="ribbon-btn" data-page="secuencial">
        Secuencial
      </button>
      <button class="ribbon-btn" disabled>
        Binaria
      </button>
      <button class="ribbon-btn" disabled>
        Hashing
      </button>
    </div>
  `;

  content.innerHTML = `
    <h2>Búsquedas internas</h2>
    <p>Selecciona un algoritmo.</p>
  `;

  ribbon.querySelectorAll("[data-page]").forEach(btn => {
    btn.addEventListener("click", () => {
      loadExternalPage(btn.dataset.page);
    });
  });
}

function showBusquedaExterna() {
  document.getElementById("ribbon").innerHTML = "";
  document.getElementById("content").innerHTML = `
    <h2>Búsquedas externas</h2>
    <p>Simulador próximamente…</p>
  `;
}

/* ---------------- Loader ---------------- */

function loadExternalPage(page) {
  const content = document.getElementById("content");
  content.innerHTML = "<p>Cargando simulador…</p>";

  fetch(`static/${page}.html`)
    .then(res => {
      if (!res.ok) throw new Error();
      return res.text();
    })
    .then(html => {
      content.innerHTML = html;
      loadExternalCSS(`static/css/${page}.css`);
      loadExternalJS(`static/js/${page}.js`, () => {
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

/* ---------------- Init ---------------- */

document.addEventListener("DOMContentLoaded", () => {
  handleTabClick("busquedas");
});
