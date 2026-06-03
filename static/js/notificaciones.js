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
  function createToast(message, type = "info") {
    let container = document.querySelector(".toast-container");
    if (!container) {
      container = document.createElement("div");
      container.className = "toast-container";
      document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);

    requestAnimationFrame(() => toast.classList.add("visible"));

    setTimeout(() => {
      toast.classList.remove("visible");
      toast.addEventListener(
        "transitionend",
        () => {
          toast.remove();
          if (!container.querySelector(".toast")) {
            container.remove();
          }
        },
        { once: true }
      );
    }, 3000);

    return toast;
  }

  window.notifySuccess = (msg) => createToast(msg, "success");
  window.notifyError = (msg) => createModal(msg, "error");
  window.notifyInfo = (msg) => createToast(msg, "info");

  window.confirmModal = (message, onConfirm, onCancel) => {
    const existing = document.querySelector(".modal-overlay");
    if (existing) existing.remove();
  
    const overlay = document.createElement("div");
    overlay.className = "modal-overlay";
  
    const box = document.createElement("div");
    box.className = "modal-box info";
  
    const msg = document.createElement("div");
    msg.className = "modal-message";
    msg.textContent = message;
  
    // Botón Confirmar (estilo primary)
    const btnConfirm = document.createElement("button");
    btnConfirm.className = "modal-btn";
    btnConfirm.textContent = "Continuar";
    btnConfirm.style.marginRight = "8px";
    btnConfirm.style.background = "var(--ms-blue)";
    btnConfirm.style.color = "white";
    btnConfirm.style.border = "none";
    btnConfirm.style.cursor = "pointer";
    btnConfirm.style.transition = "all var(--transition-base)";
    btnConfirm.onmouseenter = () => {
      btnConfirm.style.background = "var(--ms-blue-hover)";
    };
    btnConfirm.onmouseleave = () => {
      btnConfirm.style.background = "var(--ms-blue)";
    };
  
    // Botón Cancelar (estilo danger)
    const btnCancel = document.createElement("button");
    btnCancel.className = "modal-btn";
    btnCancel.textContent = "Cancelar";
    btnCancel.style.background = "white";
    btnCancel.style.color = "var(--ms-error)";
    btnCancel.style.border = `1px solid var(--ms-error)`;
    btnCancel.style.cursor = "pointer";
    btnCancel.style.transition = "all var(--transition-base)";
    btnCancel.onmouseenter = () => {
      btnCancel.style.background = "var(--ms-error)";
      btnCancel.style.color = "white";
    };
    btnCancel.onmouseleave = () => {
      btnCancel.style.background = "white";
      btnCancel.style.color = "var(--ms-error)";
    };
  
    const buttonGroup = document.createElement("div");
    buttonGroup.appendChild(btnConfirm);
    buttonGroup.appendChild(btnCancel);
  
    btnConfirm.addEventListener("click", () => {
      overlay.remove();
      if (onConfirm) onConfirm();
    });
    btnCancel.addEventListener("click", () => {
      overlay.remove();
      if (onCancel) onCancel();
    });
    overlay.addEventListener("click", (e) => {
      if (e.target === overlay) overlay.remove();
    });
  
    box.appendChild(msg);
    box.appendChild(buttonGroup);
    overlay.appendChild(box);
    document.body.appendChild(overlay);
  };
})();