const appState = {
  loadedScripts: new Set(),
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
  setActiveTab(type);
  showContent(type);
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
      <button class="ribbon-btn" disabled>Hashing</button>
    </div>
  `;


  lvl3.innerHTML = ""; // por si luego agregas más niveles

  content.innerHTML = `
    <h2>Búsquedas internas</h2>
    <p>Selecciona un algoritmo.</p>
  `;

  lvl2.querySelectorAll("[data-page]").forEach(btn => {
    btn.addEventListener("click", function () {
      setActiveRibbonButton(this);
      loadExternalPage(this.dataset.page);
    });
  });
}

function showBusquedaExterna() {
  document.getElementById("ribbon-level-2").innerHTML = "";
  document.getElementById("ribbon-level-3").innerHTML = "";

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
