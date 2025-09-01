    function showContent(type) {
      const ribbon = document.getElementById("ribbon");
      const content = document.getElementById("content");

      if (type === "busqueda_interna") {
        ribbon.innerHTML = `
          <div class="ribbon-buttons">
            <button onclick="showContent('secuencial')">Secuencial</button>
            <button onclick="showContent('binaria')">Binaria</button>
            <button onclick="showContent('hashing')">Hashing</button>
          </div>
        `;
        content.innerHTML = "<h2>Selecciona un algoritmo en la cinta de opciones</h2>";

      } else if (type === "busqueda_externa") {
        ribbon.innerHTML = "";
        content.innerHTML = "<h2>Simulador de búsquedas externas próximamente...</h2>";

      } else if (type === "grafos") {
        ribbon.innerHTML = "";
        content.innerHTML = "<h2>Simulador de grafos próximamente...</h2>";

      } else if (type === "secuencial") {
        ribbon.innerHTML = "";

        content.innerHTML = `
          <h2>Búsqueda Secuencial</h2>
          <div>
            <label>Tamaño estructura: <input type="number" id="sizeStructure" min="1" value="5"></label><br><br>
            <label>Tamaño clave: <input type="number" id="keySize" min="1" value="3"></label><br><br>
            <button id="btnCreate">Crear</button>
          </div>
          <div id="structureContainer" style="margin-top:20px;"></div>
          <div id="operations" style="margin-top:20px; display:none;">
            <input type="text" id="inputKey" placeholder="Clave" maxlength="10">
            <button id="btnInsert">Insertar</button>
            <button id="btnSearch">Buscar</button>
            <button id="btnDelete">Borrar</button>
          </div>
          <div id="message" style="margin-top:10px; color:green;"></div>
        `;

        // Estado de la estructura
        let structure = [];
        let maxSize = 0;
        let keySize = 0;

        const btnCreate = document.getElementById('btnCreate');
        const structureContainer = document.getElementById('structureContainer');
        const operations = document.getElementById('operations');
        const inputKey = document.getElementById('inputKey');
        const btnInsert = document.getElementById('btnInsert');
        const btnSearch = document.getElementById('btnSearch');
        const btnDelete = document.getElementById('btnDelete');
        const message = document.getElementById('message');

        function renderStructure() {
          structureContainer.innerHTML = structure.map(item => {
            if (item === null) {
              return `<div class="empty">-</div>`;
            } else {
              return `<div class="filled">${item}</div>`;
            }
          }).join('');
        }

        btnCreate.onclick = () => {
          maxSize = parseInt(document.getElementById('sizeStructure').value);
          keySize = parseInt(document.getElementById('keySize').value);

          if (isNaN(maxSize) || maxSize <= 0) {
            alert('El tamaño de la estructura debe ser un número mayor que 0');
            return;
          }
          if (isNaN(keySize) || keySize <= 0) {
            alert('El tamaño de la clave debe ser un número mayor que 0');
            return;
          }

          structure = Array(maxSize).fill(null);
          renderStructure();
          operations.style.display = 'block';
          message.style.color = "green";
          message.textContent = "Estructura creada. Ahora puedes insertar, buscar o borrar claves.";
          inputKey.value = '';
        };

        btnInsert.onclick = () => {
          const key = inputKey.value.trim();
          if (key.length === 0) {
            alert('Introduce una clave para insertar');
            return;
          }
          if (key.length > keySize) {
            alert(`La clave no puede ser mayor a ${keySize} caracteres`);
            return;
          }

          const index = structure.indexOf(null);
          if (index === -1) {
            message.style.color = "red";
            message.textContent = "La estructura está llena, no se pueden insertar más claves.";
            return;
          }
          structure[index] = key;
          renderStructure();
          message.style.color = "green";
          message.textContent = `Clave "${key}" insertada en la posición ${index}.`;
          inputKey.value = '';
        };

        btnSearch.onclick = () => {
          const key = inputKey.value.trim();
          if (key.length === 0) {
            alert('Introduce una clave para buscar');
            return;
          }

          const index = structure.indexOf(key);
          if (index === -1) {
            message.style.color = "red";
            message.textContent = `Clave "${key}" NO encontrada.`;
          } else {
            message.style.color = "green";
            message.textContent = `Clave "${key}" encontrada en la posición ${index}.`;
          }
        };

        btnDelete.onclick = () => {
          const key = inputKey.value.trim();
          if (key.length === 0) {
            alert('Introduce una clave para borrar');
            return;
          }

          const index = structure.indexOf(key);
          if (index === -1) {
            message.style.color = "red";
            message.textContent = `Clave "${key}" NO encontrada para borrar.`;
          } else {
            structure[index] = null;
            renderStructure();
            message.style.color = "green";
            message.textContent = `Clave "${key}" borrada de la posición ${index}.`;
            inputKey.value = '';
          }
        };

      } else if (type === "binaria") {
        ribbon.innerHTML = "";
        content.innerHTML =
          "<h2>Búsqueda Binaria</h2><p>Aquí irá el simulador de búsqueda binaria.</p>";

      } else if (type === "hashing") {
        ribbon.innerHTML = "";
        content.innerHTML =
          "<h2>Hashing</h2><p>Aquí irá el simulador de hashing con su tabla.</p>";
      }
    }

    function setActiveTab(selectedType) {
      const tabs = document.querySelectorAll('.tab');
      tabs.forEach(tab => {
        if (tab.getAttribute('data-type') === selectedType) {
          tab.classList.add('active');
        } else {
          tab.classList.remove('active');
        }
      });
    }

    function handleTabClick(type) {
      setActiveTab(type);
      showContent(type);
    }