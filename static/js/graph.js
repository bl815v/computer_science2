/* eslint-disable no-console */
(() => {
  "use strict";

  const API_BASE = "http://127.0.0.1:8000/graphs";
  let graphList = [];

  const graphSides = {
    A: {
      graphId: "grafoA",
      graphData: { vertices: [], edges: [], directed: true, weighted: true, derived: {} },
      positions: new Map(),
      dragging: false,
      draggedVertex: null,
      dragOffset: { x: 0, y: 0 }
    },
    B: {
      graphId: "grafoB",
      graphData: { vertices: [], edges: [], directed: true, weighted: true, derived: {} },
      positions: new Map(),
      dragging: false,
      draggedVertex: null,
      dragOffset: { x: 0, y: 0 }
    }
  };

  function normalizeGraphData(data) {
    const vertices = (data.vertices || []).map(v => typeof v === 'object' ? v.name : v);
    const edges = (data.edges || []).map(e => ({
      name: e.name,
      source: typeof e.source === 'object' ? e.source.name : e.source,
      target: typeof e.target === 'object' ? e.target.name : e.target,
      directed: e.directed,
      weight: e.weight
    }));
    return {
      vertices,
      edges,
      directed: data.directed,
      weighted: data.weighted,
      derived: data.derived || {}
    };
  }

  function getGraphState(side) {
    return graphSides[side] || graphSides.A;
  }

  function getCanvas(side) {
    return document.getElementById(`graph-canvas-${side.toLowerCase()}`);
  }

  function getInput(id) {
    return document.getElementById(id);
  }

  function getGraphById(id) {
    if (!id) return null;
    return graphList.find(g => g.graph_id === id) || null;
  }

  function populateSelect(selectId, label, selectedId) {
    const select = getInput(selectId);
    if (!select) return;
    const previousValue = select.value;
    select.innerHTML = `<option value="">${label}</option>`;
    graphList.forEach(g => {
      const option = document.createElement('option');
      option.value = g.graph_id;
      option.textContent = `${g.graph_id} (${(g.vertices || []).length} vértices)`;
      if (g.graph_id === selectedId || g.graph_id === previousValue) option.selected = true;
      select.appendChild(option);
    });
    if (selectedId && !graphList.some(g => g.graph_id === previousValue)) {
      select.value = selectedId;
    }
  }

  function populateGraphSelectors() {
    const selectedA = getInput('graphA-selector')?.value || graphSides.A.graphId;
    const selectedB = getInput('graphB-selector')?.value || graphSides.B.graphId;
    const selectedBinaryA = getInput('binary-graph-a')?.value;
    const selectedBinaryB = getInput('binary-graph-b')?.value;
    const selectedUnary = getInput('unary-graph')?.value;
    const selectedPath = getInput('path-graph')?.value;

    populateSelect('graphA-selector', '-- Seleccionar A --', selectedA);
    populateSelect('graphB-selector', '-- Seleccionar B --', selectedB);
    populateSelect('binary-graph-a', '-- Grafo A --', selectedBinaryA);
    populateSelect('binary-graph-b', '-- Grafo B --', selectedBinaryB);
    populateSelect('unary-graph', '-- Grafo --', selectedUnary);
    populateSelect('path-graph', '-- Grafo --', selectedPath);
  }

  function renderSummaryCard(title, graph) {
    if (!graph) return `<div class="result-card"><h4>${title}</h4><p>Sin grafo seleccionado.</p></div>`;
    return `<div class="result-card"><h4>${title}</h4>${renderSummary(graph)}</div>`;
  }

  function refreshGraphState() {
    return fetch(`${API_BASE}/state`)
      .then(res => {
        if (!res.ok) throw new Error('Error al obtener estado');
        return res.json();
      })
      .then(state => {
        graphList = state.graphs || [];
        populateGraphSelectors();

        ['A', 'B'].forEach(side => {
          const sideState = getGraphState(side);
          const selector = getInput(`graph${side}-selector`);
          if (selector && selector.value) {
            sideState.graphId = selector.value;
          }
          const current = getGraphById(sideState.graphId) || graphList[0] || null;
          if (current) {
            sideState.graphData = normalizeGraphData(current);
            getInput(`graph${side}-directed`).checked = sideState.graphData.directed;
            getInput(`graph${side}-weighted`).checked = sideState.graphData.weighted;
            getInput(`graph${side}-id`).value = sideState.graphId;
          } else {
            sideState.graphData = { vertices: [], edges: [], directed: true, weighted: true, derived: {} };
            sideState.positions.clear();
          }
        });

        renderAllGraphCanvases();
        renderGraphResult('Resumen actual', `${renderSummaryCard('Graph A', getGraphById(graphSides.A.graphId))}${renderSummaryCard('Graph B', getGraphById(graphSides.B.graphId))}`);
      })
      .catch(err => {
        console.error(err);
        window.notifyError?.('No se pudo cargar el estado del grafo.');
      });
  }

  function resizeCanvas(side) {
    const canvas = getCanvas(side);
    if (!canvas) return;
    const container = canvas.parentElement;
    canvas.width = container.clientWidth;
    canvas.height = 400;
  }

  function renderAllGraphCanvases() {
    ['A', 'B'].forEach(side => {
      const sideState = getGraphState(side);
      const graph = getGraphById(sideState.graphId);
      renderGraphOnCanvas(`graph-canvas-${side.toLowerCase()}`, graph, sideState.positions);
    });
  }

  function renderGraphResult(title, content) {
    const container = getInput('graph-results');
    if (!container) return;
    container.innerHTML = `
      <div class="result-card">
        <h4>${title}</h4>
        <div class="result-content">${content}</div>
      </div>
    `;
  }

  function renderSummary(graph) {
    if (!graph) return '<p>No hay datos de grafo.</p>';
    return `<div class="graph-summary" style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.75rem">
      <div><strong>Vértices:</strong> ${graph.vertices.length}</div>
      <div><strong>Aristas:</strong> ${graph.edges.length}</div>
      <div><strong>Dirigido:</strong> ${graph.directed ? 'Sí' : 'No'}</div>
      <div><strong>Ponderado:</strong> ${graph.weighted ? 'Sí' : 'No'}</div>
    </div>`;
  }

  function renderKeyValueList(obj) {
    if (!obj || Object.keys(obj).length === 0) return '<p>No hay resultados.</p>';
    return `<dl style="display:grid;grid-gap:.5rem">${Object.entries(obj).map(([key, value]) => `<div><strong>${key}:</strong> ${typeof value === 'object' ? JSON.stringify(value) : value}</div>`).join('')}</dl>`;
  }

  function renderMatrix(title, payload) {
    if (!payload || !payload.matrix) return `<p>Sin datos de matriz.</p>`;
    const rows = payload.rows || [];
    const cols = payload.cols || [];
    const matrix = payload.matrix;
    const header = [''].concat(cols).map(c => `<th>${c}</th>`).join('');
    const body = rows.map((rowLabel, rowIndex) => {
      const rowCells = matrix[rowIndex].map(cell => `<td>${cell}</td>`).join('');
      return `<tr><th>${rowLabel}</th>${rowCells}</tr>`;
    }).join('');
    return `<div class="matrix-card"><h5>${title}</h5><div class="table-scroll"><table><thead><tr>${header}</tr></thead><tbody>${body}</tbody></table></div></div>`;
  }

  function renderCircuitResult(payload) {
    if (!payload || !payload.circuits) return '<p>Sin circuitos.</p>';
    return payload.circuits.map((circuit, index) => `<div><strong>Circuito ${index + 1}:</strong> ${circuit.join(', ')}</div>`).join('');
  }

  function showAlgorithmResult(title, payload) {
    if (!payload) {
      renderGraphResult(title, '<p>No hay resultados.</p>');
      return;
    }
    if (payload.matrix) {
      renderGraphResult(title, renderMatrix(title, payload));
      return;
    }
    if (payload.circuits) {
      renderGraphResult(title, renderCircuitResult(payload));
      return;
    }
    if (payload.path) {
      const pathHtml = `<div><strong>Camino:</strong> ${payload.path.join(' → ')}</div>`;
      renderGraphResult(title, `${pathHtml}${renderKeyValueList(payload)}`);
      return;
    }
    renderGraphResult(title, renderKeyValueList(payload));
  }

  function createGraph(side) {
    const graphIdInput = getInput(`graph${side}-id`);
    if (!graphIdInput) return;
    const graphId = graphIdInput.value.trim();
    if (!graphId) { window.notifyError?.('ID del grafo vacío.'); return; }
    const directed = getInput(`graph${side}-directed`)?.checked;
    const weighted = getInput(`graph${side}-weighted`)?.checked;

    return fetch(`${API_BASE}/create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ graph_id: graphId, directed, weighted })
    })
      .then(res => {
        if (!res.ok) return res.json().then(err => { throw new Error(err.detail || 'Error al crear'); });
        graphSides[side].graphId = graphId;
        return refreshGraphState();
      })
      .then(() => {
        window.notifySuccess?.('Grafo creado/reseteado.');
      })
      .catch(err => {
        window.notifyError?.(err.message);
      });
  }

  function loadGraphSide(side) {
    const selector = getInput(`graph${side}-selector`);
    if (!selector) return;
    if (!selector.value) {
      window.notifyError?.('Selecciona un grafo para cargar.');
      return;
    }
    graphSides[side].graphId = selector.value;
    refreshGraphState();
  }

  function addVertex(side) {
    const nameInput = getInput(`graph${side}-vertex-name`);
    if (!nameInput) return;
    const name = nameInput.value.trim();
    const sideState = getGraphState(side);
    if (!name) { window.notifyError?.('Ingresa nombre del vértice.'); return; }

    return fetch(`${API_BASE}/${encodeURIComponent(sideState.graphId)}/vertex`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name })
    })
      .then(res => {
        if (!res.ok) return res.json().then(err => { throw new Error(err.detail || 'Error al agregar'); });
        return refreshGraphState();
      })
      .then(() => {
        window.notifySuccess?.(`Vértice ${name} agregado.`);
        window.markStructureDirty?.();
        nameInput.value = '';
      })
      .catch(err => {
        window.notifyError?.(err.message);
      });
  }

  function addEdge(side) {
    const sideState = getGraphState(side);
    const name = getInput(`graph${side}-edge-name`)?.value.trim();
    const source = getInput(`graph${side}-edge-source`)?.value.trim();
    const target = getInput(`graph${side}-edge-target`)?.value.trim();
    const weightValue = getInput(`graph${side}-edge-weight`)?.value;
    let weight = parseInt(weightValue, 10);
    if (!name || !source || !target) { window.notifyError?.('Completa todos los campos.'); return; }
    if (sideState.graphData.weighted && isNaN(weight)) weight = 1;

    return fetch(`${API_BASE}/${encodeURIComponent(sideState.graphId)}/edge`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, source, target, directed: sideState.graphData.directed, weight: sideState.graphData.weighted ? weight : undefined })
    })
      .then(res => {
        if (!res.ok) return res.json().then(err => { throw new Error(err.detail || 'Error al agregar arista'); });
        return refreshGraphState();
      })
      .then(() => {
        window.notifySuccess?.(`Arista ${name} agregada.`);
        window.markStructureDirty?.();
        getInput(`graph${side}-edge-name`).value = '';
        getInput(`graph${side}-edge-source`).value = '';
        getInput(`graph${side}-edge-target`).value = '';
        getInput(`graph${side}-edge-weight`).value = '1';
      })
      .catch(err => {
        window.notifyError?.(err.message);
      });
  }

  function deleteEdge(side) {
    const sideState = getGraphState(side);
    const name = getInput(`graph${side}-delete-edge-name`)?.value.trim();
    if (!name) { window.notifyError?.('Ingresa el nombre de la arista.'); return; }

    return fetch(`${API_BASE}/${encodeURIComponent(sideState.graphId)}/edge/${encodeURIComponent(name)}`, {
      method: 'DELETE'
    })
      .then(res => {
        if (!res.ok) return res.json().then(err => { throw new Error(err.detail || 'Error al eliminar'); });
        return refreshGraphState();
      })
      .then(() => {
        window.notifySuccess?.(`Arista ${name} eliminada.`);
        window.markStructureDirty?.();
        getInput(`graph${side}-delete-edge-name`).value = '';
      })
      .catch(err => {
        window.notifyError?.(err.message);
      });
  }

  function completeGraph(side) {
    const sideState = getGraphState(side);
    const graphData = sideState.graphData;
    if (graphData.vertices.length < 2) {
      window.notifyError?.('Se necesitan al menos 2 vértices para completar el grafo.');
      return Promise.resolve();
    }

    const existingEdges = new Set();
    graphData.edges.forEach(edge => {
      const source = typeof edge.source === 'object' ? edge.source.name : edge.source;
      const target = typeof edge.target === 'object' ? edge.target.name : edge.target;
      const key = graphData.directed ? `${source}-${target}` : `${Math.min(source, target)}-${Math.max(source, target)}`;
      existingEdges.add(key);
    });

    const requests = [];
    graphData.vertices.forEach((source, i) => {
      graphData.vertices.forEach((target, j) => {
        if (i === j) return;
        const key = graphData.directed ? `${source}-${target}` : `${Math.min(source, target)}-${Math.max(source, target)}`;
        if (existingEdges.has(key)) return;
        if (!graphData.directed && i > j) return;

        const edgeName = `e_${source}_${target}`;
        const body = { name: edgeName, source, target, directed: graphData.directed, weight: graphData.weighted ? 1 : undefined };
        requests.push(fetch(`${API_BASE}/${encodeURIComponent(sideState.graphId)}/edge`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body)
        }).then(res => {
          if (!res.ok) console.warn(`No se pudo añadir arista ${edgeName}`);
        }));
      });
    });

    return Promise.all(requests)
      .then(() => refreshGraphState())
      .then(() => {
        window.notifySuccess?.('Grafo completado.');
      })
      .catch(err => {
        console.error(err);
      });
  }

  function highlightDerivedEdges(graph) {
    const highlights = new Set();
    const addEntries = entries => {
      if (!entries) return;
      if (Array.isArray(entries)) {
        entries.forEach(entry => {
          if (Array.isArray(entry)) {
            entry.forEach(item => item && highlights.add(item));
          } else if (entry) {
            highlights.add(entry);
          }
        });
      }
    };
    addEntries(graph.derived?.mst_edges);
    addEntries(graph.derived?.circuits);
    addEntries(graph.derived?.fundamental_circuits?.circuits);
    if (graph.derived?.path) {
      pathToEdges(graph.derived.path, graph).forEach(name => highlights.add(name));
    }
    return highlights;
  }

  function pathToEdges(path, graph) {
    const edgeNames = new Set();
    if (!Array.isArray(path) || path.length < 2) return edgeNames;
    for (let i = 0; i < path.length - 1; i++) {
      const u = path[i];
      const v = path[i + 1];
      (graph.edges || []).forEach(edge => {
        const source = typeof edge.source === 'object' ? edge.source.name : edge.source;
        const target = typeof edge.target === 'object' ? edge.target.name : edge.target;
        if (source === u && target === v) edgeNames.add(edge.name);
        if (!graph.directed && source === v && target === u) edgeNames.add(edge.name);
      });
    }
    return edgeNames;
  }

  function layoutPositionsFor(graph, canvas) {
    const positionsLocal = new Map();
    if (!graph || !canvas) return positionsLocal;
    const n = (graph.vertices || []).length;
    if (n === 0) return positionsLocal;
    const cols = Math.ceil(Math.sqrt(n));
    const rows = Math.ceil(n / cols);
    const cellW = canvas.width / (cols + 1);
    const cellH = canvas.height / (rows + 1);
    const startX = cellW;
    const startY = cellH;
    (graph.vertices || []).forEach((v, i) => {
      const col = i % cols;
      const row = Math.floor(i / cols);
      positionsLocal.set(typeof v === 'object' ? v.name : v, { x: startX + col * cellW, y: startY + row * cellH });
    });
    return positionsLocal;
  }

  function renderGraphOnCanvas(canvasId, graph, positionsMap) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctxLocal = canvas.getContext('2d');
    ctxLocal.clearRect(0, 0, canvas.width, canvas.height);

    if (!graph || (graph.vertices || []).length === 0) {
      ctxLocal.fillStyle = '#605e5c';
      ctxLocal.font = "14px 'Segoe UI'";
      ctxLocal.fillText('Sin vértices. Agrega un vértice para comenzar.', 20, 40);
      return;
    }

    const positionsLocal = positionsMap && positionsMap.size > 0 ? positionsMap : layoutPositionsFor(graph, canvas);

    const highlights = highlightDerivedEdges(graph);

    (graph.edges || []).forEach(edge => {
      const source = typeof edge.source === 'object' ? edge.source.name : edge.source;
      const target = typeof edge.target === 'object' ? edge.target.name : edge.target;
      const from = positionsLocal.get(source);
      const to = positionsLocal.get(target);
      if (!from || !to) return;
      const isHighlighted = highlights.has(edge.name);
      ctxLocal.beginPath();
      ctxLocal.moveTo(from.x, from.y);
      ctxLocal.lineTo(to.x, to.y);
      ctxLocal.strokeStyle = isHighlighted ? '#d13438' : '#0078d4';
      ctxLocal.lineWidth = isHighlighted ? 3 : 2;
      ctxLocal.stroke();
      if (graph.directed) {
        const angle = Math.atan2(to.y - from.y, to.x - from.x);
        const arrowSize = 8;
        ctxLocal.fillStyle = '#0078d4';
        ctxLocal.beginPath();
        ctxLocal.moveTo(to.x, to.y);
        ctxLocal.lineTo(to.x - arrowSize * Math.cos(angle - Math.PI / 6), to.y - arrowSize * Math.sin(angle - Math.PI / 6));
        ctxLocal.lineTo(to.x - arrowSize * Math.cos(angle + Math.PI / 6), to.y - arrowSize * Math.sin(angle + Math.PI / 6));
        ctxLocal.fill();
      }
      const midX = (from.x + to.x) / 2;
      const midY = (from.y + to.y) / 2;
      ctxLocal.fillStyle = '#323130';
      ctxLocal.font = "12px 'Segoe UI'";
      let label = edge.name || '';
      if (graph.weighted && edge.weight !== undefined && edge.weight !== null) label += ` (${edge.weight})`;
      ctxLocal.fillText(label, midX - 15, midY - 8);
    });

    const pathVertices = (graph.derived && graph.derived.path) || [];
    (graph.vertices || []).forEach(v => {
      const name = typeof v === 'object' ? v.name : v;
      const pos = positionsLocal.get(name);
      if (!pos) return;
      const isOnPath = pathVertices.includes(name);
      ctxLocal.beginPath();
      ctxLocal.arc(pos.x, pos.y, 22, 0, 2 * Math.PI);
      ctxLocal.fillStyle = isOnPath ? '#ffd2d0' : '#e5f1fb';
      ctxLocal.fill();
      ctxLocal.strokeStyle = '#0078d4';
      ctxLocal.lineWidth = 2;
      ctxLocal.stroke();
      ctxLocal.fillStyle = '#323130';
      ctxLocal.font = "bold 14px 'Segoe UI'";
      ctxLocal.fillText(name, pos.x - 7, pos.y + 5);
    });
  }

  function canvasPointerDown(side, event) {
    const canvas = getCanvas(side);
    const sideState = getGraphState(side);
    const graph = getGraphById(sideState.graphId);
    if (!canvas || !graph) return;

    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    const mouseX = (event.clientX - rect.left) * scaleX;
    const mouseY = (event.clientY - rect.top) * scaleY;
    if (sideState.positions.size === 0) {
      sideState.positions = layoutPositionsFor(graph, canvas);
    }

    for (const [vertex, pos] of sideState.positions.entries()) {
      const dx = mouseX - pos.x;
      const dy = mouseY - pos.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist <= 22) {
        sideState.dragging = true;
        sideState.draggedVertex = vertex;
        sideState.dragOffset = { x: pos.x - mouseX, y: pos.y - mouseY };
        canvas.setPointerCapture(event.pointerId);
        canvas.style.cursor = 'grabbing';
        event.preventDefault();
        break;
      }
    }
  }

  function canvasPointerMove(side, event) {
    const canvas = getCanvas(side);
    const sideState = getGraphState(side);
    if (!canvas || !sideState.dragging || !sideState.draggedVertex) return;

    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    let mouseX = (event.clientX - rect.left) * scaleX;
    let mouseY = (event.clientY - rect.top) * scaleY;
    mouseX = Math.min(Math.max(mouseX, 22), canvas.width - 22);
    mouseY = Math.min(Math.max(mouseY, 22), canvas.height - 22);
    const newPos = { x: mouseX + sideState.dragOffset.x, y: mouseY + sideState.dragOffset.y };
    sideState.positions.set(sideState.draggedVertex, newPos);
    renderGraphOnCanvas(canvas.id, getGraphById(sideState.graphId), sideState.positions);
  }

  function canvasPointerUp(side, event) {
    const canvas = getCanvas(side);
    const sideState = getGraphState(side);
    if (!canvas) return;
    sideState.dragging = false;
    sideState.draggedVertex = null;
    canvas.style.cursor = 'default';
    canvas.releasePointerCapture?.(event.pointerId);
  }

  function exportGraph() {
    return window.saveUtils.exportStructure('/graphs/export')
      .then(snapshot => {
        const graphId = getInput('graphA-selector')?.value || getInput('graphA-id')?.value.trim() || 'graph_export';
        window.saveUtils.downloadJSON(snapshot, `grafo_${graphId}.json`);
        window.notifySuccess?.('Grafo exportado.');
      })
      .catch(() => window.notifyError?.('Error al exportar.'));
  }

  function importGraph() {
    return window.saveUtils.loadJSONFile()
      .then(snapshot => fetch(`${API_BASE}/import`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ snapshot })
      }))
      .then(res => {
        if (!res.ok) return res.json().then(err => { throw new Error(err.detail || 'Error al importar'); });
        return res.json();
      })
      .then(body => {
        if (body.graphs && body.graphs.length > 0) {
          graphSides.A.graphId = body.graphs[0].graph_id;
        }
        return refreshGraphState();
      })
      .then(() => {
        window.notifySuccess?.('Grafo importado.');
        window.markStructureDirty?.();
      })
      .catch(err => {
        window.notifyError?.(err.message || 'Error al importar.');
      });
  }

  async function performBinaryOperation() {
    const graphA = getInput('binary-graph-a')?.value;
    const graphB = getInput('binary-graph-b')?.value;
    const operation = getInput('binary-op')?.value;
    const resultId = getInput('binary-result-id')?.value.trim() || 'result_graph';
    if (!graphA || !graphB || !operation) {
      window.notifyError?.('Selecciona ambos grafos y la operación.');
      return;
    }

    try {
      const res = await fetch(`${API_BASE}/${operation}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ graph_a_id: graphA, graph_b_id: graphB, result_id: resultId })
      });
      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || 'Error al ejecutar operación binaria');
      }
      const payload = await res.json();
      graphSides.A.graphId = resultId;
      await refreshGraphState();
      showAlgorithmResult(`Resultado ${operation}`, payload);
      window.notifySuccess?.('Operación binaria ejecutada.');
    } catch (err) {
      window.notifyError?.(err.message);
    }
  }

  async function performUnaryOperation() {
    const graphId = getInput('unary-graph')?.value;
    const operation = getInput('unary-op')?.value;
    if (!graphId || !operation) {
      window.notifyError?.('Selecciona el grafo y la operación unaria.');
      return;
    }
    try {
      let endpoint = `${API_BASE}/${graphId}/${operation}`;
      let options = { method: 'POST', headers: { 'Content-Type': 'application/json' } };
      if (operation === 'complement') {
        endpoint = `${API_BASE}/complement`;
        options.body = JSON.stringify({ graph_id: graphId, result_id: 'result_graph' });
      }
      const res = await fetch(endpoint, options);
      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || 'Error al ejecutar operación unaria');
      }
      const payload = await res.json();
      if (operation === 'complement') {
        graphSides.A.graphId = 'result_graph';
      }
      await refreshGraphState();
      showAlgorithmResult(`Resultado ${operation}`, payload);
      window.notifySuccess?.('Operación unaria ejecutada.');
    } catch (err) {
      window.notifyError?.(err.message);
    }
  }

  async function computeBellman() {
    const graphId = getInput('path-graph')?.value;
    const source = getInput('path-source')?.value.trim();
    const target = getInput('path-target')?.value.trim();
    if (!graphId || !source) {
      window.notifyError?.('Selecciona grafo y origen.');
      return;
    }
    try {
      const body = { source };
      if (target) body.target = target;
      const res = await fetch(`${API_BASE}/${graphId}/bellman`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || 'Error Bellman');
      }
      const payload = await res.json();
      showAlgorithmResult('Bellman', payload);
    } catch (err) {
      window.notifyError?.(err.message);
    }
  }

  async function computeDijkstra() {
    const graphId = getInput('path-graph')?.value;
    const source = getInput('path-source')?.value.trim();
    const target = getInput('path-target')?.value.trim();
    if (!graphId || !source) {
      window.notifyError?.('Selecciona grafo y origen.');
      return;
    }
    try {
      const body = { source };
      if (target) body.target = target;
      const res = await fetch(`${API_BASE}/${graphId}/dijkstra`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || 'Error Dijkstra');
      }
      const payload = await res.json();
      showAlgorithmResult('Dijkstra', payload);
    } catch (err) {
      window.notifyError?.(err.message);
    }
  }

  async function computeMatrix() {
    const graphId = getInput('path-graph')?.value;
    const type = getInput('matrix-type')?.value;
    if (!graphId || !type) {
      window.notifyError?.('Selecciona grafo y tipo de matriz.');
      return;
    }
    try {
      const res = await fetch(`${API_BASE}/${graphId}/matrices/${type}`);
      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || 'Error cargando matriz');
      }
      const payload = await res.json();
      renderGraphResult(`Matriz ${type.replace('-', ' ')}`, renderMatrix(type, payload));
    } catch (err) {
      window.notifyError?.(err.message);
    }
  }

  function initSimulator() {
    ['A', 'B'].forEach(side => {
      resizeCanvas(side);
      const canvas = getCanvas(side);
      if (!canvas) return;
      canvas.addEventListener('pointerdown', event => canvasPointerDown(side, event));
      canvas.addEventListener('pointermove', event => canvasPointerMove(side, event));
      canvas.addEventListener('pointerup', event => canvasPointerUp(side, event));
      canvas.addEventListener('pointerleave', event => canvasPointerUp(side, event));
    });

    window.addEventListener('resize', () => {
      ['A', 'B'].forEach(side => {
        resizeCanvas(side);
      });
      renderAllGraphCanvases();
    });

    getInput('create-graphA-btn')?.addEventListener('click', () => createGraph('A'));
    getInput('create-graphB-btn')?.addEventListener('click', () => createGraph('B'));
    getInput('load-graphA-btn')?.addEventListener('click', () => loadGraphSide('A'));
    getInput('load-graphB-btn')?.addEventListener('click', () => loadGraphSide('B'));
    getInput('add-vertexA-btn')?.addEventListener('click', () => addVertex('A'));
    getInput('add-vertexB-btn')?.addEventListener('click', () => addVertex('B'));
    getInput('add-edgeA-btn')?.addEventListener('click', () => addEdge('A'));
    getInput('add-edgeB-btn')?.addEventListener('click', () => addEdge('B'));
    getInput('delete-edgeA-btn')?.addEventListener('click', () => deleteEdge('A'));
    getInput('delete-edgeB-btn')?.addEventListener('click', () => deleteEdge('B'));
    getInput('complete-graphA-btn')?.addEventListener('click', () => completeGraph('A'));
    getInput('complete-graphB-btn')?.addEventListener('click', () => completeGraph('B'));
    getInput('binary-op-btn')?.addEventListener('click', performBinaryOperation);
    getInput('unary-op-btn')?.addEventListener('click', performUnaryOperation);
    getInput('bellman-btn')?.addEventListener('click', computeBellman);
    getInput('dijkstra-btn')?.addEventListener('click', computeDijkstra);
    getInput('matrix-btn')?.addEventListener('click', computeMatrix);
    getInput('export-graph-btn')?.addEventListener('click', exportGraph);
    getInput('import-graph-btn')?.addEventListener('click', importGraph);
    getInput('refresh-graph-btn')?.addEventListener('click', refreshGraphState);

    ['graphA-edge-op', 'graphB-edge-op'].forEach(opId => {
      const opSelect = getInput(opId);
      if (!opSelect) return;
      opSelect.addEventListener('change', () => {
        const side = opId.startsWith('graphA') ? 'A' : 'B';
        const addFields = getInput(`graph${side}-edge-add-fields`);
        const deleteFields = getInput(`graph${side}-edge-delete-fields`);
        const showAdd = opSelect.value === 'add';
        if (addFields) addFields.style.display = showAdd ? 'flex' : 'none';
        if (deleteFields) deleteFields.style.display = showAdd ? 'none' : 'flex';
      });
    });

    getInput('graphA-selector')?.addEventListener('change', () => {
      const graphId = getInput('graphA-selector').value;
      graphSides.A.graphId = graphId;
      const current = getGraphById(graphId);
      if (current) {
        graphSides.A.graphData = normalizeGraphData(current);
        graphSides.A.positions.clear();
        getInput('graphA-directed').checked = graphSides.A.graphData.directed;
        getInput('graphA-weighted').checked = graphSides.A.graphData.weighted;
      }
      renderAllGraphCanvases();
    });
    getInput('graphB-selector')?.addEventListener('change', () => {
      const graphId = getInput('graphB-selector').value;
      graphSides.B.graphId = graphId;
      const current = getGraphById(graphId);
      if (current) {
        graphSides.B.graphData = normalizeGraphData(current);
        graphSides.B.positions.clear();
        getInput('graphB-directed').checked = graphSides.B.graphData.directed;
        getInput('graphB-weighted').checked = graphSides.B.graphData.weighted;
      }
      renderAllGraphCanvases();
    });

    refreshGraphState();
  }

  window.refreshStructure = refreshGraphState;
  window.initSimulator = initSimulator;
})();
