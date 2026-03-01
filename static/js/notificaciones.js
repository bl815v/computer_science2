(function () {
  "use strict";

  function createModal(message, type = "info") {

    //Eliminar modal anterior si existe
    const existing = document.querySelector(".modal-overlay");
    if (existing) {
      existing.remove();
    }

    // Overlay
    const overlay = document.createElement("div");
    overlay.className = "modal-overlay";

    // Caja
    const box = document.createElement("div");
    box.className = `modal-box ${type}`;

    const msg = document.createElement("div");
    msg.className = "modal-message";
    msg.textContent = message;

    const btn = document.createElement("button");
    btn.className = "modal-btn";
    btn.textContent = "Aceptar";

    btn.addEventListener("click", () => {
      overlay.remove();
    });

    // Cerrar si se hace click fuera
    overlay.addEventListener("click", (e) => {
      if (e.target === overlay) overlay.remove();
    });

    box.appendChild(msg);
    box.appendChild(btn);
    overlay.appendChild(box);

    document.body.appendChild(overlay);
  }

  // Exponemos funciones globales
  window.notifySuccess = (msg) => createModal(msg, "success");
  window.notifyError = (msg) => createModal(msg, "error");
  window.notifyInfo = (msg) => createModal(msg, "info");
})();