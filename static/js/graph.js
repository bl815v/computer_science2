const GRAPH_API_BASE = 'http://127.0.0.1:8000/graphs';
const cyInstances = {
  'graphA-container': null,
  'graphB-container': null,
  'graphResult-container': null,
};

const graphEditState = {
  A: { graphId: null, graph: null },
  B: { graphId: null, graph: null },
};

function initSimulator() {
  bindEvents();
  updateOperationInterface();
  clearPreview('A');
  clearPreview('B');
  clearResultPreview();
  refreshGraphSelectors();
  ensureCytoscape().catch(() => {
    logError('No se pudo cargar la librería de visualización. Asegúrate de tener acceso a internet.');
  });
}

window.initSimulator = initSimulator;

function bindEvents() {
  document.getElementById('create-graphA').addEventListener('click', () => createGraph('A'));
  document.getElementById('create-graphB').addEventListener('click', () => createGraph('B'));
  document.getElementById('clear-graphA').addEventListener('click', () => clearGraphForm('A'));
  document.getElementById('clear-graphB').addEventListener('click', () => clearGraphForm('B'));
  document.getElementById('delete-vertex-A').addEventListener('click', () => deleteGraphVertex('A'));
  document.getElementById('delete-edge-A').addEventListener('click', () => deleteGraphEdge('A'));
  document.getElementById('delete-vertex-B').addEventListener('click', () => deleteGraphVertex('B'));
  document.getElementById('delete-edge-B').addEventListener('click', () => deleteGraphEdge('B'));
  document.getElementById('execute-operation').addEventListener('click', executeOperation);
  document.getElementById('reset-all').addEventListener('click', resetView);
  document.getElementById('operation-select').addEventListener('input', updateOperationInterface);
  document.getElementById('graphA-select').addEventListener('change', () => renderSelectedGraph('A'));
  document.getElementById('graphB-select').addEventListener('change', () => renderSelectedGraph('B'));
}

function updateOperationInterface() {
  const operation = document.getElementById('operation-select').value;
  const graphBRow = document.getElementById('graphB-selector-row');
  const label = document.getElementById('execute-label');
  const unaryNote = document.getElementById('unary-note');
  const graphBPanel = document.getElementById('graphB-panel');

  if (operation === 'complement') {
    graphBRow.style.display = 'none';
    graphBPanel.style.opacity = '0.55';
    graphBPanel.style.pointerEvents = 'none';
    unaryNote.style.display = 'block';
    label.textContent = 'Grafo A';
  } else {
    graphBRow.style.display = 'block';
    graphBPanel.style.opacity = '1';
    graphBPanel.style.pointerEvents = 'auto';
    unaryNote.style.display = 'none';
    label.textContent = 'Grafo A';
  }
}

async function ensureCytoscape() {
  if (window.cytoscape) return;
  await loadScript('https://unpkg.com/cytoscape@3.23.0/dist/cytoscape.min.js');
}

function loadScript(src) {
  return new Promise((resolve, reject) => {
    if ([...document.scripts].some(script => script.src === src || script.src.includes(src))) {
      resolve();
      return;
    }

    const script = document.createElement('script');
    script.src = src;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error(`No se pudo cargar ${src}`));
    document.head.appendChild(script);
  });
}

async function refreshGraphSelectors() {
  try {
    const state = await fetchJSON(`${GRAPH_API_BASE}/state`);
    const graphs = Array.isArray(state.graphs) ? state.graphs : [];
    populateSelect('graphA-select', graphs);
    populateSelect('graphB-select', graphs);
    logStatus('Lista de grafos actualizada.');
  } catch (error) {
    logError(error.message);
  }
}

function populateSelect(selectId, graphs) {
  const select = document.getElementById(selectId);
  const previousValue = select.value;
  select.innerHTML = '';

  const placeholder = document.createElement('option');
  placeholder.value = '';
  placeholder.textContent = 'Seleccionar grafo existente';
  select.appendChild(placeholder);

  graphs.forEach(graph => {
    const option = document.createElement('option');
    option.value = graph.graph_id;
    option.textContent = `${graph.graph_id} — ${graph.vertices.length} vértices, ${graph.edges.length} aristas`;
    if (graph.graph_id === previousValue) {
      option.selected = true;
    }
    select.appendChild(option);
  });
}

function fillOptions(select, items) {
  if (!select) return;
  const current = select.value;
  select.innerHTML = '';
  const placeholder = document.createElement('option');
  placeholder.value = '';
  placeholder.textContent = 'Seleccionar...';
  select.appendChild(placeholder);

  items.forEach(item => {
    const option = document.createElement('option');
    option.value = item;
    option.textContent = item;
    if (item === current) option.selected = true;
    select.appendChild(option);
  });
}

function setGraphState(side, graph) {
  graphEditState[side].graphId = graph.graph_id;
  graphEditState[side].graph = graph;
  updateGraphEditors(side, graph);
}

function updateGraphEditors(side, graph) {
  if (!graph) return;
  fillOptions(document.getElementById(`graph${side}-delete-vertex-select`), graph.vertices.map(v => v.name));
  fillOptions(document.getElementById(`graph${side}-delete-edge-select`), graph.edges.map(e => e.name));
}

function getDeletionTarget(side, type) {
  const select = document.getElementById(`graph${side}-delete-${type}-select`);
  const input = document.getElementById(`graph${side}-delete-${type}-text`);
  const typed = input?.value.trim();
  return typed || select?.value || '';
}

async function ensureGraph(side, graphId, directed, weighted) {
  const state = graphEditState[side];
  if (state.graphId === graphId && state.graph) {
    return state.graph;
  }

  const existing = await loadGraphFromState(graphId);
  if (existing) {
    setGraphState(side, existing);
    return existing;
  }

  const created = await fetchJSON(`${GRAPH_API_BASE}/create`, {
    method: 'POST',
    body: JSON.stringify({ graph_id: graphId, directed, weighted }),
  });

  if (created && created.graph_id) {
    setGraphState(side, created);
    return created;
  }

  const loaded = await loadGraphFromState(graphId);
  if (loaded) {
    setGraphState(side, loaded);
    return loaded;
  }

  throw new Error('No se pudo inicializar el grafo.');
}

function parseVerticesInput(text) {
  if (!text) return [];
  const normalized = text.replace(/,/g, '\n');
  return normalized
    .split(/\r?\n/)
    .map(item => item.trim())
    .filter(Boolean)
    .map(item => item.replace(/\s+/g, ''))
    .filter(Boolean);
}

function parseEdgesInput(text, directed, weighted) {
  if (!text) return [];
  return text
    .split(/\r?\n/)
    .map(line => line.trim())
    .filter(Boolean)
    .map((line, index) => {
      const pieces = line.split(',').map(part => part.trim());
      if (pieces.length < 3) {
        throw new Error(`Línea ${index + 1}: formato inválido. Debe tener al menos nombre, origen y destino.`);
      }
      const [name, source, target, weight] = pieces;
      return {
        name,
        source,
        target,
        directed,
        weight: weighted ? (weight ? Number(weight) : null) : null,
      };
    });
}

async function createGraph(side) {
  const idField = document.getElementById(`graph${side}-id`);
  const directedField = document.getElementById(`graph${side}-directed`);
  const weightedField = document.getElementById(`graph${side}-weighted`);
  const verticesField = document.getElementById(`graph${side}-vertices`);
  const edgesField = document.getElementById(`graph${side}-edges`);

  const graphId = idField.value.trim();
  const directed = directedField.checked;
  const weighted = weightedField.checked;

  if (!graphId) {
    logError(`El Id del grafo ${side} es obligatorio.`);
    return;
  }

  const vertices = parseVerticesInput(verticesField.value);
  let edges;
  try {
    edges = parseEdgesInput(edgesField.value, directed, weighted);
  } catch (error) {
    logError(error.message);
    return;
  }

  let graph;
  try {
    graph = await ensureGraph(side, graphId, directed, weighted);
  } catch (error) {
    logError(`No se pudo inicializar el grafo ${side}: ${error.message}`);
    return;
  }

  try {
    if (vertices.length) await addVertices(graphId, vertices);
    if (edges.length) await addEdges(graphId, edges);
    await refreshGraphSelectors();
    const updated = await loadGraphFromState(graphId);
    if (updated) {
      setGraphState(side, updated);
      renderGraph(updated, `graph${side}-container`);
      setSummary(side, updated);
    }
    logStatus(`Grafo ${side} actualizado con ${vertices.length} vértices y ${edges.length} aristas.`);
    document.getElementById(`graph${side}-select`).value = graphId;
    // Limpiar inputs solo tras éxito para flujos de inserción rápida
    document.getElementById(`graph${side}-vertices`).value = '';
    document.getElementById(`graph${side}-edges`).value = '';
  } catch (error) {
    logError(`Error actualizando el grafo ${side}: ${error.message}`);
  }
}

async function addVertices(graphId, vertices) {
  if (!vertices.length) return;
  for (const vertex of vertices) {
    await fetchJSON(`${GRAPH_API_BASE}/${encodeURIComponent(graphId)}/vertex`, {
      method: 'POST',
      body: JSON.stringify({ name: vertex }),
    });
  }
}

async function addEdges(graphId, edges) {
  if (!edges.length) return;
  for (const edge of edges) {
    await fetchJSON(`${GRAPH_API_BASE}/${encodeURIComponent(graphId)}/edge`, {
      method: 'POST',
      body: JSON.stringify({
        name: edge.name,
        source: edge.source,
        target: edge.target,
        directed: edge.directed,
        weight: edge.weight,
      }),
    });
  }
}

async function deleteGraphVertex(side) {
  const state = graphEditState[side];
  const graphId = state.graphId || document.getElementById(`graph${side}-select`).value;
  const vertex = getDeletionTarget(side, 'vertex');
  if (!graphId || !vertex) {
    logError('Selecciona o escribe el vértice a borrar.');
    return;
  }

  const containerId = `graph${side}-container`;
  const container = document.getElementById(containerId);
  if (container) container.classList.add('animating-removal');

  try {
    await fetchJSON(`${GRAPH_API_BASE}/${encodeURIComponent(graphId)}/vertex/${encodeURIComponent(vertex)}`, {
      method: 'DELETE',
    });
    await refreshGraphSelectors();
    const updated = await loadGraphFromState(graphId);
    if (updated) {
      setGraphState(side, updated);
      renderGraph(updated, containerId);
      setSummary(side, updated);
    }
    logStatus(`Vértice ${vertex} borrado de ${graphId}.`);
    // limpiar inputs/select solo tras éxito
    const selV = document.getElementById(`graph${side}-delete-vertex-select`);
    const txtV = document.getElementById(`graph${side}-delete-vertex-text`);
    if (selV) selV.value = '';
    if (txtV) txtV.value = '';
  } catch (error) {
    logError(`Error borrando vértice: ${error.message}`);
  } finally {
    if (container) setTimeout(() => container.classList.remove('animating-removal'), 220);
  }
}

async function deleteGraphEdge(side) {
  const state = graphEditState[side];
  const graphId = state.graphId || document.getElementById(`graph${side}-select`).value;
  const edge = getDeletionTarget(side, 'edge');
  if (!graphId || !edge) {
    logError('Selecciona o escribe la arista a borrar.');
    return;
  }

  const containerId = `graph${side}-container`;
  const container = document.getElementById(containerId);
  if (container) container.classList.add('animating-removal');

  try {
    await fetchJSON(`${GRAPH_API_BASE}/${encodeURIComponent(graphId)}/edge/${encodeURIComponent(edge)}`, {
      method: 'DELETE',
    });
    await refreshGraphSelectors();
    const updated = await loadGraphFromState(graphId);
    if (updated) {
      setGraphState(side, updated);
      renderGraph(updated, containerId);
      setSummary(side, updated);
    }
    logStatus(`Arista ${edge} borrada de ${graphId}.`);
    // limpiar inputs/select solo tras éxito
    const selE = document.getElementById(`graph${side}-delete-edge-select`);
    const txtE = document.getElementById(`graph${side}-delete-edge-text`);
    if (selE) selE.value = '';
    if (txtE) txtE.value = '';
  } catch (error) {
    logError(`Error borrando arista: ${error.message}`);
  } finally {
    if (container) setTimeout(() => container.classList.remove('animating-removal'), 220);
  }
}

function recenterGraph(containerId) {
  const cy = cyInstances[containerId];
  if (!cy) return;
  cy.fit(50);
}

function mountRecenterButton(container, containerId) {
  let button = container.querySelector('.graph-control');
  if (!button) {
    button = document.createElement('button');
    button.type = 'button';
    button.className = 'graph-control';
    button.title = 'Recentrar grafo';
    button.textContent = '⟳';
    container.appendChild(button);
  }
  button.onclick = () => recenterGraph(containerId);
}

async function executeOperation() {
  const operation = document.getElementById('operation-select').value;
  const graphAId = document.getElementById('graphA-select').value;
  const graphBId = document.getElementById('graphB-select').value;
  const resultIdField = document.getElementById('graph-result-id');
  const resultId = resultIdField.value.trim() || `resultado-${operation}-${Date.now()}`;

  if (!graphAId) {
    logError('Selecciona un grafo A para ejecutar la operación.');
    return;
  }

  if (operation !== 'complement' && !graphBId) {
    logError('Selecciona un grafo B para ejecutar esta operación.');
    return;
  }

  let endpoint = `${GRAPH_API_BASE}/${operation}`;
  let body = { result_id: resultId };

  if (operation === 'complement') {
    body.graph_id = graphAId;
  } else {
    body.graph_a_id = graphAId;
    body.graph_b_id = graphBId;
  }

  try {
    const graph = await fetchJSON(endpoint, {
      method: 'POST',
      body: JSON.stringify(body),
    });

    await refreshGraphSelectors();
    renderGraph(graph, 'graphResult-container');
    setSummary('Result', graph);
    logStatus(`Operación ${operation} creada como ${resultId}.`);
    resultIdField.value = resultId;
  } catch (error) {
    logError(`Error al ejecutar ${operation}: ${error.message}`);
  }
}

async function loadGraphFromState(graphId) {
  const state = await fetchJSON(`${GRAPH_API_BASE}/state`);
  const graph = Array.isArray(state.graphs) ? state.graphs.find(item => item.graph_id === graphId) : undefined;
  return graph;
}

function setSummary(side, graph) {
  const summaryId = side === 'Result' ? 'graphResult-summary' : `graph${side}-summary`;
  const summary = document.getElementById(summaryId);
  if (!summary) return;
  summary.textContent = `${graph.vertices.length} vértices, ${graph.edges.length} aristas${graph.directed ? ', dirigido' : ''}${graph.weighted ? ', ponderado' : ''}`;
}

async function renderSelectedGraph(side) {
  const select = document.getElementById(`graph${side}-select`);
  const graphId = select.value;
  if (!graphId) {
    clearPreview(side);
    return;
  }

  try {
    const graph = await loadGraphFromState(graphId);
    if (graph) {
      setGraphState(side, graph);
      renderGraph(graph, `graph${side}-container`);
      setSummary(side, graph);
      logStatus(`Mostrando ${graphId} en la vista ${side}.`);
    }
  } catch (error) {
    logError(error.message);
  }
}

function clearGraphForm(side) {
  document.getElementById(`graph${side}-id`).value = '';
  document.getElementById(`graph${side}-directed`).checked = false;
  document.getElementById(`graph${side}-weighted`).checked = false;
  document.getElementById(`graph${side}-vertices`).value = '';
  document.getElementById(`graph${side}-edges`).value = '';
  document.getElementById(`graph${side}-delete-vertex-select`).innerHTML = '';
  document.getElementById(`graph${side}-delete-edge-select`).innerHTML = '';
  document.getElementById(`graph${side}-delete-vertex-text`).value = '';
  document.getElementById(`graph${side}-delete-edge-text`).value = '';
  document.getElementById(`graph${side}-select`).value = '';
  graphEditState[side].graphId = null;
  graphEditState[side].graph = null;
  clearPreview(side);
  logStatus(`Formulario Grafo ${side} limpiado.`);
}

function resetView() {
  clearGraphForm('A');
  clearGraphForm('B');
  clearResultPreview();
  document.getElementById('graph-result-id').value = '';
  refreshGraphSelectors();
  logStatus('Vista reseteada.');
}

function clearPreview(side) {
  const containerId = `graph${side}-container`;
  if (cyInstances[containerId]) {
    cyInstances[containerId].destroy();
    cyInstances[containerId] = null;
  }
  const container = document.getElementById(containerId);
  if (container) {
    container.innerHTML = '<div class="placeholder">Sin grafo seleccionado</div>';
  }
  const summaryId = `graph${side}-summary`;
  const summary = document.getElementById(summaryId);
  if (summary) summary.textContent = '';
}

function clearResultPreview() {
  if (cyInstances['graphResult-container']) {
    cyInstances['graphResult-container'].destroy();
    cyInstances['graphResult-container'] = null;
  }
  const container = document.getElementById('graphResult-container');
  if (container) {
    container.innerHTML = '<div class="placeholder">Sin resultado</div>';
  }
  const summary = document.getElementById('graphResult-summary');
  if (summary) summary.textContent = '';
}

function renderGraph(graph, containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;

  if (!window.cytoscape) {
    container.innerHTML = '<div class="placeholder">Biblioteca de visualización no cargada.</div>';
    return;
  }

  if (cyInstances[containerId]) {
    cyInstances[containerId].destroy();
  }

  container.innerHTML = '';
  mountRecenterButton(container, containerId);

  const elements = [
    ...graph.vertices.map(vertex => ({ data: { id: vertex.name, label: vertex.name } })),
    ...graph.edges.map(edge => ({
      data: {
        id: edge.name,
        source: edge.source,
        target: edge.target,
        label: edge.weight != null ? String(edge.weight) : '',
      },
      classes: edge.directed ? 'directed' : 'undirected',
    })),
  ];

  const options = {
    container,
    elements,
    style: [
      {
        selector: 'node',
        style: {
          'background-color': '#2563eb',
          label: 'data(label)',
          color: '#ffffff',
          'text-valign': 'center',
          'text-halign': 'center',
          'font-size': 12,
          'text-outline-width': 6,
          'text-outline-color': '#2563eb',
          width: 46,
          height: 46,
        },
      },
      {
        selector: 'edge',
        style: {
          width: 3,
          'line-color': '#9ca3af',
          'target-arrow-color': '#9ca3af',
          'curve-style': 'bezier',
          'target-arrow-shape': 'triangle',
          'label': 'data(label)',
          'font-size': 10,
          'text-margin-x': 0,
          'text-margin-y': -10,
          'text-rotation': 'autorotate',
        },
      },
      {
        selector: '.undirected',
        style: {
          'target-arrow-shape': 'none',
        },
      },
    ],
    layout: {
      name: 'cose',
      animate: true,
      randomize: false,
      idealEdgeLength: 120,
      nodeOverlap: 24,
      gravity: 0.1,
    },
  };

  const instance = cytoscape(options);
  instance.fit(50);
  cyInstances[containerId] = instance;
}

async function fetchJSON(url, options = {}) {
  const requestOptions = {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  };

  const response = await fetch(url, requestOptions);
  const text = await response.text();
  let payload;

  try {
    payload = text ? JSON.parse(text) : null;
  } catch {
    payload = null;
  }

  if (!response.ok) {
    throw new Error(payload?.detail || payload?.message || response.statusText || 'Error de red');
  }

  return payload;
}

function logStatus(message) {
  const log = document.getElementById('graph-log');
  if (!log) return;
  const timestamp = new Date().toLocaleTimeString();
  log.textContent = `${timestamp} · ${message}\n${log.textContent}`;
}

function logError(message) {
  logStatus(`ERROR: ${message}`);
  if (typeof window.notifyError === 'function') {
    window.notifyError(message);
  }
}
