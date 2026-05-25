/* eslint-disable no-console */
(() => {
  "use strict";

  const API_BASE = "http://127.0.0.1:8000/graphs";
  let currentGraphId = "miGrafo";
  let graphData = { vertices: [], edges: [], directed: true, weighted: true };
  let canvas, ctx;
  let positions = new Map(); // nombre vértice -> {x, y}
  
  // Variables para arrastre
  let dragging = false;
  let draggedVertex = null;
  let dragOffset = { x: 0, y: 0 };

  // Elementos DOM
  let graphSelector;

  // Normalizar datos del backend
  function normalizeGraphData(data) {
    const vertices = (data.vertices || []).map(v => typeof v === 'object' ? v.name : v);
    const edges = (data.edges || []).map(e => ({
      name: e.name,
      source: typeof e.source === 'object' ? e.source.name : e.source,
      target: typeof e.target === 'object' ? e.target.name : e.target,
      weight: e.weight
    }));
    return { vertices, edges, directed: data.directed, weighted: data.weighted };
  }

  // Layout en cuadrícula (orden alfabético / según el array)
  function computeGridLayout() {
    const n = graphData.vertices.length;
    if (n === 0) return;
    const cols = Math.ceil(Math.sqrt(n));
    const rows = Math.ceil(n / cols);
    const cellW = canvas.width / (cols + 1);
    const cellH = canvas.height / (rows + 1);
    const startX = cellW;
    const startY = cellH;
    graphData.vertices.forEach((v, i) => {
      const col = i % cols;
      const row = Math.floor(i / cols);
      positions.set(v, {
        x: startX + col * cellW,
        y: startY + row * cellH
      });
    });
  }

  // Dibujar el grafo completo (con nombres de aristas)
  function drawGraph() {
    if (!ctx) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    if (graphData.vertices.length === 0) {
      ctx.fillStyle = "#605e5c";
      ctx.font = "14px 'Segoe UI'";
      ctx.fillText("Sin vértices. Agrega un vértice para comenzar.", 20, 40);
      return;
    }

    // Aristas
    graphData.edges.forEach(edge => {
      const from = positions.get(edge.source);
      const to = positions.get(edge.target);
      if (!from || !to) return;
      ctx.beginPath();
      ctx.moveTo(from.x, from.y);
      ctx.lineTo(to.x, to.y);
      ctx.strokeStyle = "#0078d4";
      ctx.lineWidth = 2;
      ctx.stroke();

      if (graphData.directed) {
        const angle = Math.atan2(to.y - from.y, to.x - from.x);
        const arrowSize = 8;
        const arrowX = to.x;
        const arrowY = to.y;
        ctx.fillStyle = "#0078d4";
        ctx.beginPath();
        ctx.moveTo(arrowX, arrowY);
        ctx.lineTo(arrowX - arrowSize * Math.cos(angle - Math.PI/6),
                   arrowY - arrowSize * Math.sin(angle - Math.PI/6));
        ctx.lineTo(arrowX - arrowSize * Math.cos(angle + Math.PI/6),
                   arrowY - arrowSize * Math.sin(angle + Math.PI/6));
        ctx.fill();
      }

      // Mostrar nombre de la arista y peso
      const midX = (from.x + to.x) / 2;
      const midY = (from.y + to.y) / 2;
      ctx.fillStyle = "#323130";
      ctx.font = "12px 'Segoe UI'";
      let label = edge.name;
      if (graphData.weighted && edge.weight !== undefined && edge.weight !== null) {
        label += ` (${edge.weight})`;
      }
      ctx.fillText(label, midX - 15, midY - 8);
    });

    // Vértices
    graphData.vertices.forEach(v => {
      const pos = positions.get(v);
      if (!pos) return;
      ctx.beginPath();
      ctx.arc(pos.x, pos.y, 22, 0, 2 * Math.PI);
      ctx.fillStyle = "#e5f1fb";
      ctx.fill();
      ctx.strokeStyle = "#0078d4";
      ctx.lineWidth = 2;
      ctx.stroke();
      ctx.fillStyle = "#323130";
      ctx.font = "bold 14px 'Segoe UI'";
      ctx.fillText(v, pos.x - 7, pos.y + 5);
    });
  }

  // ---- Eventos de arrastre ----
  function handleMouseDown(e) {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    const mouseX = (e.clientX - rect.left) * scaleX;
    const mouseY = (e.clientY - rect.top) * scaleY;
    
    for (let [v, pos] of positions.entries()) {
      const dx = mouseX - pos.x;
      const dy = mouseY - pos.y;
      const dist = Math.sqrt(dx*dx + dy*dy);
      if (dist <= 22) {
        dragging = true;
        draggedVertex = v;
        dragOffset = { x: pos.x - mouseX, y: pos.y - mouseY };
        canvas.style.cursor = "grabbing";
        e.preventDefault();
        break;
      }
    }
  }

  function handleMouseMove(e) {
    if (!dragging || !draggedVertex) return;
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    let mouseX = (e.clientX - rect.left) * scaleX;
    let mouseY = (e.clientY - rect.top) * scaleY;
    mouseX = Math.min(Math.max(mouseX, 22), canvas.width - 22);
    mouseY = Math.min(Math.max(mouseY, 22), canvas.height - 22);
    const newPos = { x: mouseX + dragOffset.x, y: mouseY + dragOffset.y };
    positions.set(draggedVertex, newPos);
    drawGraph();
  }

  function handleMouseUp() {
    dragging = false;
    draggedVertex = null;
    canvas.style.cursor = "default";
  }

  // ---- Comunicación con el backend ----
  async function refreshGraphState() {
    try {
      const res = await fetch(`${API_BASE}/state`);
      if (!res.ok) throw new Error("Error al obtener estado");
      const state = await res.json();
      const current = state.graphs?.find(g => g.graph_id === currentGraphId);
      if (current) {
        graphData = normalizeGraphData(current);
        document.getElementById("graph-directed").checked = graphData.directed;
        document.getElementById("graph-weighted").checked = graphData.weighted;
        computeGridLayout();
      } else {
        graphData = { vertices: [], edges: [], directed: true, weighted: true };
        positions.clear();
      }
      drawGraph();
      await loadGraphList(); // Actualizar selector después de cada refresh
    } catch (err) {
      console.error(err);
      window.notifyError?.("No se pudo cargar el estado del grafo.");
    }
  }

  async function createGraph() {
    const graphId = document.getElementById("graph-id").value.trim();
    if (!graphId) { window.notifyError?.("ID del grafo vacío."); return; }
    currentGraphId = graphId;
    const directed = document.getElementById("graph-directed").checked;
    const weighted = document.getElementById("graph-weighted").checked;
    try {
      const res = await fetch(`${API_BASE}/create`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ graph_id: currentGraphId, directed, weighted })
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Error al crear");
      }
      await refreshGraphState();
      window.notifySuccess?.("Grafo creado/reseteado.");
      window.markStructureDirty?.();
      document.getElementById("graph-id").value = currentGraphId;
    } catch (err) { window.notifyError?.(err.message); }
  }

  async function addVertex() {
    const name = document.getElementById("vertex-name").value.trim();
    if (!name) { window.notifyError?.("Ingresa nombre del vértice."); return; }
    try {
      const res = await fetch(`${API_BASE}/${currentGraphId}/vertex`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name })
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Error al agregar");
      }
      await refreshGraphState();
      window.notifySuccess?.(`Vértice ${name} agregado.`);
      window.markStructureDirty?.();
      document.getElementById("vertex-name").value = "";
    } catch (err) { window.notifyError?.(err.message); }
  }

  async function addEdge() {
    const name = document.getElementById("edge-name").value.trim();
    const source = document.getElementById("edge-source").value.trim();
    const target = document.getElementById("edge-target").value.trim();
    let weight = parseInt(document.getElementById("edge-weight").value);
    if (!name || !source || !target) { window.notifyError?.("Completa todos los campos."); return; }
    if (graphData.weighted && isNaN(weight)) weight = 1;
    const body = { name, source, target, directed: graphData.directed, weight: graphData.weighted ? weight : undefined };
    try {
      const res = await fetch(`${API_BASE}/${currentGraphId}/edge`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Error al agregar arista");
      }
      await refreshGraphState();
      window.notifySuccess?.(`Arista ${name} agregada.`);
      window.markStructureDirty?.();
      document.getElementById("edge-name").value = "";
      document.getElementById("edge-source").value = "";
      document.getElementById("edge-target").value = "";
      document.getElementById("edge-weight").value = "1";
    } catch (err) { window.notifyError?.(err.message); }
  }

  async function deleteEdge() {
    const name = document.getElementById("delete-edge-name").value.trim();
    if (!name) { window.notifyError?.("Ingresa el nombre de la arista."); return; }
    try {
      const res = await fetch(`${API_BASE}/${currentGraphId}/edge/${encodeURIComponent(name)}`, { method: "DELETE" });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Error al eliminar");
      }
      await refreshGraphState();
      window.notifySuccess?.(`Arista ${name} eliminada.`);
      window.markStructureDirty?.();
      document.getElementById("delete-edge-name").value = "";
    } catch (err) { window.notifyError?.(err.message); }
  }

  // ---- Completar grafo (conectar todos los vértices) ----
  async function completeGraph() {
    if (graphData.vertices.length < 2) {
      window.notifyError?.("Se necesitan al menos 2 vértices para completar el grafo.");
      return;
    }
    const vertices = graphData.vertices;
    const existingEdges = new Set();
    graphData.edges.forEach(edge => {
      const key = graphData.directed 
        ? `${edge.source}-${edge.target}`
        : `${Math.min(edge.source, edge.target)}-${Math.max(edge.source, edge.target)}`;
      existingEdges.add(key);
    });

    let added = 0;
    for (let i = 0; i < vertices.length; i++) {
      for (let j = 0; j < vertices.length; j++) {
        if (i === j) continue;
        const source = vertices[i];
        const target = vertices[j];
        const key = graphData.directed 
          ? `${source}-${target}`
          : `${Math.min(source, target)}-${Math.max(source, target)}`;
        if (existingEdges.has(key)) continue;
        if (!graphData.directed && i > j) continue;
        
        const edgeName = `e_${source}_${target}`;
        const body = {
          name: edgeName,
          source,
          target,
          directed: graphData.directed,
          weight: graphData.weighted ? 1 : undefined
        };
        try {
          const res = await fetch(`${API_BASE}/${currentGraphId}/edge`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body)
          });
          if (res.ok) {
            added++;
            existingEdges.add(key);
          } else {
            console.warn(`No se pudo añadir arista ${edgeName}`);
          }
        } catch (err) {
          console.error(err);
        }
      }
    }
    await refreshGraphState();
    window.notifySuccess?.(`Grafo completado: se añadieron ${added} aristas.`);
  }

  // ---- Cargar lista de grafos existentes ----
  async function loadGraphList() {
    if (!graphSelector) return;
    try {
      const res = await fetch(`${API_BASE}/state`);
      if (!res.ok) return;
      const state = await res.json();
      const graphs = state.graphs || [];
      graphSelector.innerHTML = '<option value="">-- Seleccionar grafo --</option>';
      graphs.forEach(g => {
        const option = document.createElement('option');
        option.value = g.graph_id;
        option.textContent = `${g.graph_id} (${g.vertices?.length || 0} vértices)`;
        if (g.graph_id === currentGraphId) option.selected = true;
        graphSelector.appendChild(option);
      });
    } catch (err) {
      console.error("Error cargando lista de grafos:", err);
    }
  }

  async function switchToGraph(graphId) {
    if (!graphId) return;
    currentGraphId = graphId;
    await refreshGraphState();
    window.markStructureDirty?.();
    document.getElementById("graph-id").value = currentGraphId;
    await loadGraphList();
  }

  // ---- Exportar / Importar ----
  window.exportGraph = async () => {
    try {
      const snapshot = await window.saveUtils.exportStructure('/graphs/export');
      window.saveUtils.downloadJSON(snapshot, `grafo_${currentGraphId}.json`);
      window.notifySuccess?.("Grafo exportado.");
    } catch (err) { window.notifyError?.("Error al exportar."); }
  };

  window.importGraph = async () => {
    try {
      const snapshot = await window.saveUtils.loadJSONFile();
      const res = await fetch(`${API_BASE}/import`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ snapshot })
      });
      if (!res.ok) throw new Error();
      await refreshGraphState();
      window.notifySuccess?.("Grafo importado.");
      window.markStructureDirty?.();
    } catch (err) { window.notifyError?.("Error al importar."); }
  };

  window.refreshStructure = refreshGraphState;

  // ---- Inicialización ----
  function initSimulator() {
    canvas = document.getElementById("graph-canvas");
    ctx = canvas.getContext("2d");
    const resizeCanvas = () => {
      const container = canvas.parentElement;
      canvas.width = container.clientWidth;
      canvas.height = 500;
      computeGridLayout();
      drawGraph();
    };
    window.addEventListener("resize", resizeCanvas);
    resizeCanvas();

    canvas.addEventListener("mousedown", handleMouseDown);
    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", handleMouseUp);

    document.getElementById("create-graph-btn").addEventListener("click", createGraph);
    document.getElementById("add-vertex-btn").addEventListener("click", addVertex);
    document.getElementById("add-edge-btn").addEventListener("click", addEdge);
    document.getElementById("delete-edge-btn").addEventListener("click", deleteEdge);
    document.getElementById("complete-graph-btn").addEventListener("click", completeGraph);

    const edgeOpSelect = document.getElementById("edge-op");
    const addFields = document.getElementById("edge-add-fields");
    const deleteFields = document.getElementById("edge-delete-fields");
    edgeOpSelect.addEventListener("change", () => {
      addFields.style.display = edgeOpSelect.value === "add" ? "flex" : "none";
      deleteFields.style.display = edgeOpSelect.value === "delete" ? "flex" : "none";
    });

    graphSelector = document.getElementById("graph-selector");
    const loadGraphBtn = document.getElementById("load-graph-btn");
    if (loadGraphBtn) {
      loadGraphBtn.addEventListener("click", () => {
        const selected = graphSelector.value;
        if (selected) switchToGraph(selected);
      });
    }

    refreshGraphState();
  }

  window.initSimulator = initSimulator;
})();