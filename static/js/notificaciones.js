// static/js/notificaciones.js
(function () {
  "use strict";

  function createModal(message, type = "info", autoClose = true) {
    // Eliminar modal anterior si existe
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

    const closeModal = () => overlay.remove();

    btn.addEventListener("click", closeModal);
    
    overlay.addEventListener("click", (e) => {
      if (e.target === overlay) closeModal();
    });

    box.appendChild(msg);
    box.appendChild(btn);
    overlay.appendChild(box);

    document.body.appendChild(overlay);

    // Auto-cierre después de 3 segundos (ahora activado por defecto)
    if (autoClose) {
      setTimeout(closeModal, 3000);
    }
  }

  // Por defecto todas se cierran automáticamente
  window.notifySuccess = (msg, autoClose = true) => createModal(msg, "success", autoClose);
  window.notifyError = (msg, autoClose = true) => createModal(msg, "error", autoClose);
  window.notifyInfo = (msg, autoClose = true) => createModal(msg, "info", autoClose);
})();