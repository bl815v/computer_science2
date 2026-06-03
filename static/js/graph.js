const GRAPH_API_BASE = 'http://127.0.0.1:8000/graphs';
const GRAPH_CATEGORY_TOOLSETS = {
  operations: [
    { value: 'union', label: 'Unión' },
    { value: 'intersection', label: 'Intersección' },
    { value: 'ring-sum', label: 'Suma anillo' },
    { value: 'sum', label: 'Suma de grafos' },
    { value: 'complement', label: 'Complemento' },
    { value: 'cartesian-product', label: 'Producto cartesiano' },
    { value: 'tensor-product', label: 'Producto tensor' },
    { value: 'composition', label: 'Composición' },
  ],
  traversals: [
    { value: 'center', label: 'Centro / Bicentro' },
    { value: 'mst', label: 'MST' },
    { value: 'tree-distance', label: 'Distancia entre árboles' },
  ],
  paths: [
    { value: 'ordinal', label: 'Ordinal' },
    { value: 'bellman', label: 'Bellman' },
    { value: 'dijkstra', label: 'Dijkstra' },
    { value: 'floyd-warshall', label: 'Caminos mínimos' },
  ],
  coloring: [
    { value: 'vertex-coloring', label: 'Coloreado de vértices' },
    { value: 'edge-coloring', label: 'Coloreado de aristas' },
  ],
  matrices: [
    { value: 'incidence', label: 'Incidencia' },
    { value: 'vertex-adjacency', label: 'Adyacencia de vértices' },
    { value: 'edge-adjacency', label: 'Adyacencia de aristas' },
  ],
};

const GRAPH_MATRIX_DEFINITIONS = [
  {
    key: 'incidence',
    label: 'Incidencia',
    title: 'Matriz de incidencia',
    rowTitle: 'Vértice',
    endpoint: 'incidence',
  },
  {
    key: 'vertex-adjacency',
    label: 'Adyacencia de vértices',
    title: 'Matriz de adyacencia de vértices',
    rowTitle: 'Vértice',
    endpoint: 'vertex-adjacency',
  },
  {
    key: 'edge-adjacency',
    label: 'Adyacencia de aristas',
    title: 'Matriz de adyacencia de aristas',
    rowTitle: 'Arista',
    endpoint: 'edge-adjacency',
  },
];

const cyInstances = {
  'graphA-container': null,
  'graphB-container': null,
  'graphResult-container': null,
};

const graphEditState = {
  A: { graphId: null, graph: null },
  B: { graphId: null, graph: null },
  Result: { graphId: null, graph: null, detail: null },
};

const matrixExplorerState = {
  graphId: '',
  activeKey: 'incidence',
  loading: false,
  error: '',
  matrices: {},
};

function getGraphCategory() {
  return window.graphInitialCategory || 'operations';
}

function getGraphToolset(category = getGraphCategory()) {
  return GRAPH_CATEGORY_TOOLSETS[category] || GRAPH_CATEGORY_TOOLSETS.operations;
}

function isBinaryGraphOperation(operation) {
  return ['union', 'intersection', 'ring-sum', 'sum', 'cartesian-product', 'tensor-product', 'composition'].includes(operation);
}

function needsGraphBEditor(category, operation) {
  if (category === 'operations') return isBinaryGraphOperation(operation);
  if (category === 'traversals') return operation === 'tree-distance';
  return false;
}

function needsPathParameters(category, operation) {
  return category === 'paths' && ['bellman', 'dijkstra'].includes(operation);
}

function needsResultIdentifier(category) {
  return category === 'operations';
}

function getEditableGraphId(side) {
  const state = graphEditState[side];
  const selectedGraphId = document.getElementById(`graph${side}-select`)?.value?.trim() || '';
  const inputGraphId = document.getElementById(`graph${side}-id`)?.value?.trim() || '';
  return state.graphId || selectedGraphId || inputGraphId;
}

function updateDirectionStatus(side, directed) {
  const status = document.getElementById(`graph${side}-direction-status`);
  if (status) {
    status.textContent = directed ? 'Dirigido' : 'No dirigido';
  }
}

function syncGraphControlState(side, graph) {
  if (!graph) return;

  const directedField = document.getElementById(`graph${side}-directed`);
  const weightedField = document.getElementById(`graph${side}-weighted`);

  if (directedField) directedField.checked = !!graph.directed;
  if (weightedField) weightedField.checked = !!graph.weighted;
  updateDirectionStatus(side, !!graph.directed);
  updateWeightedStatus(side, !!graph.weighted);
}

function updateWeightedStatus(side, weighted) {
  const status = document.getElementById(`graph${side}-weight-status`);
  if (status) {
    status.textContent = weighted ? 'Ponderado' : 'No ponderado';
  }
}

function createMatrixExplorerShell() {
  const graphInfo = document.getElementById('graph-info');
  if (!graphInfo) return null;

  let root = document.getElementById('matrix-explorer-root');
  if (!root) {
    root = document.createElement('div');
    root.id = 'matrix-explorer-root';
    root.className = 'matrix-explorer-root';

    const toolbar = document.createElement('div');
    toolbar.className = 'matrix-explorer-toolbar';
    toolbar.innerHTML = `
      <div class="matrix-select-group">
        <label for="matrix-graph-select-visible">Grafo</label>
        <select id="matrix-graph-select-visible"></select>
      </div>
      <button id="matrix-refresh-visible" class="secondary" type="button">Actualizar</button>
    `;

    const tabs = document.createElement('div');
    tabs.id = 'matrix-tabs';
    tabs.className = 'matrix-tabs';

    const status = document.createElement('div');
    status.id = 'matrix-status';
    status.className = 'matrix-status';

    const output = document.createElement('div');
    output.id = 'matrix-output';
    output.className = 'matrix-output';

    root.appendChild(toolbar);
    root.appendChild(tabs);
    root.appendChild(status);
    root.appendChild(output);
    graphInfo.appendChild(root);

    const select = document.getElementById('matrix-graph-select-visible');
    if (select) {
      select.addEventListener('change', () => renderMatrixExplorer());
    }
    const refresh = document.getElementById('matrix-refresh-visible');
    if (refresh) {
      refresh.addEventListener('click', () => renderMatrixExplorer(true));
    }
  }

  return root;
}

function safePopulateSelect(selectId, graphs) {
  const select = document.getElementById(selectId);
  if (!select) return;
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

function populateGraphIdDatalist(graphs) {
  const datalist = document.getElementById('graph-id-list');
  if (!datalist) return;
  datalist.innerHTML = '';
  graphs.forEach(graph => {
    const option = document.createElement('option');
    option.value = graph.graph_id;
    datalist.appendChild(option);
  });
}

function initSimulator() {
  bindEvents();
  updateLayoutToggleIcon(document.getElementById('graph-layout-toggle'), document.getElementById('graph-cards')?.classList.contains('full-width'));
  updateOperationInterface();
  clearPreview('A');
  clearPreview('B');
  clearResultPreview();
  renderMatrixExplorer();
  refreshGraphSelectors();
  ensureCytoscape().catch(() => {
    logError('No se pudo cargar la librería de visualización. Asegúrate de tener acceso a internet.');
  });
}

function teardownSimulator() {
  clearPreview('A');
  clearPreview('B');
  clearResultPreview();
}

async function refreshGraphStructure() {
  updateOperationInterface();
  await refreshGraphSelectors();
  refreshRenderedGraphs();
  if (getGraphCategory() === 'matrices') {
    await renderMatrixExplorer();
  }
}

window.initSimulator = initSimulator;
window.refreshStructure = refreshGraphStructure;
window.simulatorRegistry = window.simulatorRegistry || { initializers: {}, teardowns: {} };
window.simulatorRegistry.initializers.graph = initSimulator;
window.simulatorRegistry.teardowns.graph = teardownSimulator;

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

  document.getElementById('graphA-id').addEventListener('input', () => loadInputGraphIfExists('A'));
  document.getElementById('graphB-id').addEventListener('input', () => loadInputGraphIfExists('B'));
  document.getElementById('graph-layout-toggle').addEventListener('click', toggleGraphLayout);
  const graphADirected = document.getElementById('graphA-directed');
  const graphBDirected = document.getElementById('graphB-directed');
  if (graphADirected) graphADirected.addEventListener('change', () => handleGraphDirectionChange('A'));
  if (graphBDirected) graphBDirected.addEventListener('change', () => handleGraphDirectionChange('B'));
  const graphAWeighted = document.getElementById('graphA-weighted');
  const graphBWeighted = document.getElementById('graphB-weighted');
  if (graphAWeighted) graphAWeighted.addEventListener('change', () => handleGraphWeightChange('A'));
  if (graphBWeighted) graphBWeighted.addEventListener('change', () => handleGraphWeightChange('B'));

  const edgeNameToggle = document.getElementById('edge-label-name-toggle');
  const edgeWeightToggle = document.getElementById('edge-label-weight-toggle');
  if (edgeNameToggle) edgeNameToggle.addEventListener('change', refreshRenderedGraphs);
  if (edgeWeightToggle) edgeWeightToggle.addEventListener('change', refreshRenderedGraphs);

  const edgeSelectA = document.getElementById('graphA-edit-edge-select');
  const edgeSelectB = document.getElementById('graphB-edit-edge-select');
  if (edgeSelectA) edgeSelectA.addEventListener('change', () => syncEdgeEditor('A'));
  if (edgeSelectB) edgeSelectB.addEventListener('change', () => syncEdgeEditor('B'));
  const edgeDirectedA = document.getElementById('graphA-edit-edge-directed');
  const edgeDirectedB = document.getElementById('graphB-edit-edge-directed');
  if (edgeDirectedA) edgeDirectedA.addEventListener('change', () => syncEdgeWeightState('A'));
  if (edgeDirectedB) edgeDirectedB.addEventListener('change', () => syncEdgeWeightState('B'));
  const edgeWeightedA = document.getElementById('graphA-edit-edge-weighted');
  const edgeWeightedB = document.getElementById('graphB-edit-edge-weighted');
  if (edgeWeightedA) edgeWeightedA.addEventListener('change', () => syncEdgeWeightState('A'));
  if (edgeWeightedB) edgeWeightedB.addEventListener('change', () => syncEdgeWeightState('B'));
  const updateEdgeA = document.getElementById('update-edge-A');
  const updateEdgeB = document.getElementById('update-edge-B');
  if (updateEdgeA) updateEdgeA.addEventListener('click', () => updateGraphEdge('A'));
  if (updateEdgeB) updateEdgeB.addEventListener('click', () => updateGraphEdge('B'));

  const matrixGraphSelect = document.getElementById('matrix-graph-select');
  if (matrixGraphSelect) matrixGraphSelect.addEventListener('change', () => renderMatrixExplorer());
  const matrixGraphSelectVisible = document.getElementById('matrix-graph-select-visible');
  if (matrixGraphSelectVisible) matrixGraphSelectVisible.addEventListener('change', () => renderMatrixExplorer());
  const matrixRefresh = document.getElementById('matrix-refresh');
  if (matrixRefresh) matrixRefresh.addEventListener('click', () => renderMatrixExplorer(true));
  const matrixRefreshVisible = document.getElementById('matrix-refresh-visible');
  if (matrixRefreshVisible) matrixRefreshVisible.addEventListener('click', () => renderMatrixExplorer(true));
}

function updateOperationInterface() {
  const category = getGraphCategory();
  const select = document.getElementById('operation-select');
  const operationsPanel = document.getElementById('operations-panel');
  const matricesPanel = document.getElementById('matrices-panel');
  const graphBRow = document.getElementById('graphB-selector-row');
  const label = document.getElementById('execute-label');
  const unaryNote = document.getElementById('unary-note');
  const graphBPanel = document.getElementById('graphB-panel');
  const graphBCard = document.getElementById('graphB-card');
  const pathParamsRow = document.getElementById('path-params-row');
  const resultRow = document.getElementById('graph-result-row');
  const matrixRow = document.getElementById('matrix-view-row');
  const edgeLabelRow = document.getElementById('edge-label-options-row');

  if (operationsPanel) operationsPanel.style.display = category === 'matrices' ? 'none' : 'block';
  if (matricesPanel) matricesPanel.style.display = 'none';

  if (category === 'matrices') {
    if (graphBRow) graphBRow.style.display = 'none';
    if (graphBPanel) graphBPanel.style.display = 'none';
    if (graphBCard) graphBCard.style.display = 'none';
    if (pathParamsRow) pathParamsRow.style.display = 'none';
    if (resultRow) resultRow.style.display = 'none';
    if (matrixRow) matrixRow.style.display = 'none';
    if (edgeLabelRow) edgeLabelRow.style.display = 'none';
    if (unaryNote) unaryNote.style.display = 'none';
    if (label) label.textContent = 'Grafo A';
    renderMatrixExplorer();
    return;
  }

  populateOperationOptions(getGraphToolset(category));

  const operation = select.value;
  const showGraphBEditor = needsGraphBEditor(category, operation);
  const showPathParams = needsPathParameters(category, operation);
  const showResultIdentifier = needsResultIdentifier(category);
  const showEdgeLabels = category === 'operations';

  graphBRow.style.display = showGraphBEditor ? 'block' : 'none';
  graphBPanel.style.display = showGraphBEditor ? 'block' : 'none';
  if (graphBCard) graphBCard.style.display = showGraphBEditor ? 'block' : 'none';
  if (pathParamsRow) pathParamsRow.style.display = showPathParams ? 'grid' : 'none';
  if (resultRow) resultRow.style.display = showResultIdentifier ? 'block' : 'none';
  if (matrixRow) matrixRow.style.display = 'none';
  if (edgeLabelRow) edgeLabelRow.style.display = showEdgeLabels ? 'flex' : 'none';

  if (unaryNote) {
    if (category === 'operations' && operation === 'complement') {
      unaryNote.style.display = 'block';
      unaryNote.textContent = 'El complemento solo usa Grafo A. Grafo B se mantiene inactivo.';
    } else {
      unaryNote.style.display = 'none';
    }
  }

  label.textContent = 'Grafo A';
}

async function ensureCytoscape() {
  if (window.cytoscape) return;
  await loadScript('static/js/cytoscape.min.js');
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
    safePopulateSelect('graphA-select', graphs);
    safePopulateSelect('graphB-select', graphs);
    safePopulateSelect('matrix-graph-select', graphs);
    safePopulateSelect('matrix-graph-select-visible', graphs);
    populateGraphIdDatalist(graphs);
    logStatus('Lista de grafos actualizada.');
    if (getGraphCategory() === 'matrices') {
      const matrixSelect = document.getElementById('matrix-graph-select-visible') || document.getElementById('matrix-graph-select');
      const preferredGraphId = matrixSelect?.value || document.getElementById('graphA-select')?.value || '';
      if (matrixSelect && preferredGraphId) {
        const hasOption = Array.from(matrixSelect.options).some(option => option.value === preferredGraphId);
        if (hasOption) matrixSelect.value = preferredGraphId;
      }
      await renderMatrixExplorer();
    }
  } catch (error) {
    logError(error.message);
  }
}

function populateSelect(selectId, graphs) {
  const select = document.getElementById(selectId);
  if (!select) return;
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

function populateGraphIdDatalist(graphs) {
  const datalist = document.getElementById('graph-id-list');
  if (!datalist) return;
  datalist.innerHTML = '';
  graphs.forEach(graph => {
    const option = document.createElement('option');
    option.value = graph.graph_id;
    datalist.appendChild(option);
  });
}

function loadInputGraphIfExists(side) {
  const idField = document.getElementById(`graph${side}-id`);
  const graphId = idField.value.trim();
  if (!graphId) return;
  if (graphEditState[side].graphId === graphId) return;

  const existingOption = Array.from(document.querySelectorAll('#graph-id-list option')).find(opt => opt.value === graphId);
  if (!existingOption) return;
  loadGraphIntoSide(side, graphId);
}

async function loadGraphIntoSide(side, graphId) {
  try {
    const graph = await loadGraphFromState(graphId);
    if (!graph) return;
    setGraphState(side, graph);
    renderGraph(graph, `graph${side}-container`);
    setSummary(side, graph);
    document.getElementById(`graph${side}-id`).value = graphId;
    logStatus(`Grafo ${graphId} cargado automáticamente en ${side}.`);
  } catch (error) {
    logError(error.message);
  }
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
    option.value = item.value || item;
    option.textContent = item.label || item;
    if (option.value === current) option.selected = true;
    select.appendChild(option);
  });

  if (!select.value && items.length) {
    select.value = items[0].value || items[0];
  }
}

function populateOperationOptions(options) {
  const select = document.getElementById('operation-select');
  if (!select) return;
  const current = select.value;
  select.innerHTML = '';

  options.forEach(item => {
    const option = document.createElement('option');
    option.value = item.value || item;
    option.textContent = item.label || item;
    if (option.value === current) option.selected = true;
    select.appendChild(option);
  });

  if (!select.value && options.length) {
    select.value = options[0].value || options[0];
  }
}

function isColorOperation(operation) {
  return ['vertex-coloring', 'edge-coloring'].includes(operation);
}

function toggleGraphLayout() {
  const cards = document.getElementById('graph-cards');
  const button = document.getElementById('graph-layout-toggle');
  if (!cards) return;
  cards.classList.toggle('full-width');
  updateLayoutToggleIcon(button, cards.classList.contains('full-width'));
}

function refreshRenderedGraphs() {
  if (graphEditState.A.graph) renderGraph(graphEditState.A.graph, 'graphA-container');
  if (graphEditState.B.graph) renderGraph(graphEditState.B.graph, 'graphB-container');
  if (graphEditState.Result.graph) renderGraph(graphEditState.Result.graph, 'graphResult-container');
}

function setGraphState(side, graph) {
  graphEditState[side].graphId = graph.graph_id;
  graphEditState[side].graph = graph;
  syncGraphControlState(side, graph);
  updateGraphEditors(side, graph);
}

function updateGraphEditors(side, graph) {
  if (!graph) return;
  fillOptions(document.getElementById(`graph${side}-delete-vertex-select`), graph.vertices.map(v => v.name));
  fillOptions(document.getElementById(`graph${side}-delete-edge-select`), graph.edges.map(e => e.name));
  fillOptions(document.getElementById(`graph${side}-edit-edge-select`), graph.edges.map(e => e.name));
  syncEdgeEditor(side);
}

function syncEdgeEditor(side) {
  const graph = graphEditState[side].graph;
  if (!graph) return;

  const edgeSelect = document.getElementById(`graph${side}-edit-edge-select`);
  const edgeName = edgeSelect?.value;
  const edge = graph.edges.find(item => item.name === edgeName) || graph.edges[0];
  if (!edge) return;

  if (edgeSelect && !edgeSelect.value) {
    edgeSelect.value = edge.name;
  }

  const directedField = document.getElementById(`graph${side}-edit-edge-directed`);
  const weightedField = document.getElementById(`graph${side}-edit-edge-weighted`);
  const weightField = document.getElementById(`graph${side}-edit-edge-weight`);

  if (directedField) directedField.checked = !!edge.directed;
  if (weightedField) weightedField.checked = edge.weight != null;
  if (weightField) {
    weightField.value = edge.weight != null ? String(edge.weight) : '';
    weightField.disabled = !(weightedField?.checked);
  }
}

function syncEdgeWeightState(side) {
  const weightedField = document.getElementById(`graph${side}-edit-edge-weighted`);
  const weightField = document.getElementById(`graph${side}-edit-edge-weight`);
  if (weightField) weightField.disabled = !(weightedField?.checked);
}

function getEdgeEditPayload(side) {
  const graph = graphEditState[side].graph;
  const edgeSelect = document.getElementById(`graph${side}-edit-edge-select`);
  const edgeName = edgeSelect?.value;
  const edge = graph?.edges.find(item => item.name === edgeName);
  if (!edge) return null;

  const directed = document.getElementById(`graph${side}-edit-edge-directed`)?.checked ?? edge.directed;
  const weighted = document.getElementById(`graph${side}-edit-edge-weighted`)?.checked ?? (edge.weight != null);
  const weightInput = document.getElementById(`graph${side}-edit-edge-weight`)?.value.trim() || '';
  const parsedWeight = weighted ? (weightInput ? Number(weightInput) : null) : null;

  return {
    original: edge,
    directed,
    weighted,
    weight: Number.isFinite(parsedWeight) ? parsedWeight : null,
  };
}

async function updateGraphEdge(side) {
  const state = graphEditState[side];
  const graphId = state.graphId || document.getElementById(`graph${side}-select`).value;
  const payload = getEdgeEditPayload(side);
  if (!graphId || !payload) {
    logError('Selecciona una arista para editar.');
    return;
  }

  try {
    await fetchJSON(`${GRAPH_API_BASE}/${encodeURIComponent(graphId)}/edge/${encodeURIComponent(payload.original.name)}`, {
      method: 'DELETE',
    });

    await fetchJSON(`${GRAPH_API_BASE}/${encodeURIComponent(graphId)}/edge`, {
      method: 'POST',
      body: JSON.stringify({
        name: payload.original.name,
        source: payload.original.source,
        target: payload.original.target,
        directed: payload.directed,
        weight: payload.weight,
      }),
    });

    await refreshGraphSelectors();
    const updated = await loadGraphFromState(graphId);
    if (updated) {
      setGraphState(side, updated);
      renderGraph(updated, `graph${side}-container`);
      setSummary(side, updated);
      syncEdgeEditor(side);
      if (getGraphCategory() === 'matrices') {
        await renderMatrixExplorer(true);
      }
    }

    logStatus(`Arista ${payload.original.name} actualizada en ${graphId}.`);
  } catch (error) {
    logError(`Error editando arista: ${error.message}`);
  }
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
      if (getGraphCategory() === 'matrices') {
        await renderMatrixExplorer(true);
      }
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
      if (getGraphCategory() === 'matrices') {
        await renderMatrixExplorer(true);
      }
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
      if (getGraphCategory() === 'matrices') {
        await renderMatrixExplorer(true);
      }
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
  const category = getGraphCategory();
  const operation = document.getElementById('operation-select').value;
  const graphAId = document.getElementById('graphA-select').value;
  const graphBId = document.getElementById('graphB-select').value;
  const resultIdField = document.getElementById('graph-result-id');
  const resultId = resultIdField.value.trim() || `resultado-${operation}-${Date.now()}`;
  const sourceField = document.getElementById('path-source');
  const targetField = document.getElementById('path-target');
  const source = sourceField ? sourceField.value.trim() : '';
  const target = targetField ? targetField.value.trim() : '';

  if (!graphAId) {
    logError('Selecciona un grafo A para ejecutar la operación.');
    return;
  }

  try {
    if (category === 'operations') {
      if (!isColorOperation(operation) && operation !== 'complement' && !graphBId) {
        logError('Selecciona un grafo B para ejecutar esta operación.');
        return;
      }

      if (isColorOperation(operation)) {
        const endpoint = `${GRAPH_API_BASE}/${encodeURIComponent(graphAId)}/${operation}`;
        const payload = await fetchJSON(endpoint, {
          method: 'POST',
        });
        await refreshGraphSelectors();
        const updated = await loadGraphFromState(graphAId);
        if (updated) {
          setGraphState('A', updated);
          renderGraph(updated, 'graphResult-container');
          graphEditState.Result.graph = updated;
          graphEditState.Result.graphId = graphAId;
          setSummary('Result', updated);
          renderGraphInfo(operation, payload, updated);
        }
        logStatus(`Operación ${operation} ejecutada sobre ${graphAId}.`);
        return;
      }

      const endpoint = `${GRAPH_API_BASE}/${operation}`;
      const body = { result_id: resultId };

      if (operation === 'complement') {
        body.graph_id = graphAId;
      } else {
        body.graph_a_id = graphAId;
        body.graph_b_id = graphBId;
      }

      const graph = await fetchJSON(endpoint, {
        method: 'POST',
        body: JSON.stringify(body),
      });

      await refreshGraphSelectors();
      renderGraph(graph, 'graphResult-container');
      graphEditState.Result.graph = graph;
      graphEditState.Result.graphId = graph.graph_id || resultId;
      setSummary('Result', graph);
      renderGraphInfo(operation, graph, graph);
      logStatus(`Operación ${operation} creada como ${resultId}.`);
      resultIdField.value = resultId;
      return;
    }

    if (category === 'traversals') {
      if (operation === 'tree-distance') {
        if (!graphBId) {
          logError('Selecciona un grafo B para calcular la distancia entre árboles.');
          return;
        }
        const graph = await fetchJSON(`${GRAPH_API_BASE}/tree-distance`, {
          method: 'POST',
          body: JSON.stringify({ graph_a_id: graphAId, graph_b_id: graphBId }),
        });
        renderResultPayload(operation, graph, null);
        logStatus(`Distancia entre árboles calculada para ${graphAId} y ${graphBId}.`);
        return;
      }

      const graph = await fetchJSON(`${GRAPH_API_BASE}/${encodeURIComponent(graphAId)}/${operation}`, {
        method: 'POST',
      });
      renderResultPayload(operation, graph, graph?.visualization || null);
      logStatus(`Operación ${operation} ejecutada sobre ${graphAId}.`);
      return;
    }

    if (category === 'paths') {
      if ((operation === 'bellman' || operation === 'dijkstra') && !source) {
        logError('Indica un vértice origen para ejecutar esta operación.');
        return;
      }

      const payload = operation === 'floyd-warshall'
        ? await fetchJSON(`${GRAPH_API_BASE}/${encodeURIComponent(graphAId)}/floyd-warshall`, { method: 'POST' })
        : await fetchJSON(`${GRAPH_API_BASE}/${encodeURIComponent(graphAId)}/${operation}`, {
            method: 'POST',
            body: JSON.stringify({ source, target: target || null }),
          });

      renderResultPayload(operation, payload, payload?.visualization || null);
      logStatus(`Operación ${operation} ejecutada sobre ${graphAId}.`);
      return;
    }

    if (category === 'coloring') {
      const payload = await fetchJSON(`${GRAPH_API_BASE}/${encodeURIComponent(graphAId)}/${operation}`, {
        method: 'POST',
      });
      await refreshGraphSelectors();
      const updated = await loadGraphFromState(graphAId);
      if (updated) {
        setGraphState('A', updated);
        renderGraph(updated, 'graphResult-container');
        graphEditState.Result.graph = updated;
        graphEditState.Result.graphId = graphAId;
        setSummary('Result', updated);
        renderGraphInfo(operation, payload, updated);
      }
      logStatus(`Operación ${operation} ejecutada sobre ${graphAId}.`);
    }
  } catch (error) {
    logError(`Error al ejecutar ${operation}: ${error.message}`);
  }
}

function createEmptyState(message, className = 'matrix-empty') {
  const block = document.createElement('div');
  block.className = className;
  block.textContent = message;
  return block;
}

function formatMatrixCellValue(value) {
  if (value === Infinity) return '∞';
  if (value === -Infinity) return '-∞';
  if (value === null || value === undefined) return '—';
  return String(value);
}

function createTabbedPanel(tabs, initialKey, tabClassName = 'matrix-tab') {
  const wrapper = document.createElement('div');
  const tabBar = document.createElement('div');
  tabBar.className = 'matrix-tabs';
  const content = document.createElement('div');
  content.className = 'matrix-output';

  let activeKey = initialKey || tabs[0]?.key || '';

  const renderContent = () => {
    content.innerHTML = '';
    const activeTab = tabs.find(tab => tab.key === activeKey) || tabs[0];
    if (!activeTab) {
      content.appendChild(createEmptyState('No hay información disponible.'));
      return;
    }

    const rendered = typeof activeTab.render === 'function' ? activeTab.render() : null;
    if (rendered) {
      content.appendChild(rendered);
    } else {
      content.appendChild(createEmptyState('No hay información disponible.'));
    }

    tabBar.querySelectorAll('button').forEach(button => {
      button.classList.toggle('active', button.dataset.key === activeKey);
    });
  };

  tabs.forEach(tab => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = tabClassName;
    button.dataset.key = tab.key;
    button.textContent = tab.label;
    button.addEventListener('click', () => {
      activeKey = tab.key;
      renderContent();
      if (typeof tab.onSelect === 'function') {
        tab.onSelect(tab.key);
      }
    });
    tabBar.appendChild(button);
  });

  wrapper.appendChild(tabBar);
  wrapper.appendChild(content);
  renderContent();

  return wrapper;
}

function createMatrixTableFromData(matrixData) {
  if (!matrixData || !Array.isArray(matrixData.rows) || !Array.isArray(matrixData.columns) || !Array.isArray(matrixData.matrix)) {
    return createEmptyState('La matriz no tiene un formato válido.');
  }

  const wrapper = document.createElement('div');
  wrapper.className = 'graph-info-classes';
  const heading = document.createElement('strong');
  heading.textContent = matrixData.title;
  wrapper.appendChild(heading);

  const table = document.createElement('table');
  table.className = 'graph-info-table';

  const headerRow = document.createElement('tr');
  const corner = document.createElement('th');
  corner.textContent = matrixData.rowTitle;
  headerRow.appendChild(corner);
  matrixData.columns.forEach(label => {
    const th = document.createElement('th');
    th.textContent = label;
    headerRow.appendChild(th);
  });
  table.appendChild(headerRow);

  matrixData.rows.forEach((label, rowIndex) => {
    const row = document.createElement('tr');
    const rowLabel = document.createElement('th');
    rowLabel.textContent = label;
    row.appendChild(rowLabel);
    (matrixData.matrix[rowIndex] || []).forEach(value => {
      const cell = document.createElement('td');
      cell.textContent = formatMatrixCellValue(value);
      row.appendChild(cell);
    });
    table.appendChild(row);
  });

  wrapper.appendChild(table);
  return wrapper;
}

function normalizeMatrixPayload(matrixData, title, rowTitle) {
  if (!matrixData) return null;
  const rows = Array.isArray(matrixData.rows) ? matrixData.rows : Array.isArray(matrixData.vertex_labels) ? matrixData.vertex_labels : [];
  const columns = Array.isArray(matrixData.cols) ? matrixData.cols : Array.isArray(matrixData.columns) ? matrixData.columns : rows;
  const matrix = Array.isArray(matrixData.matrix) ? matrixData.matrix : [];
  if (!rows.length || !columns.length || !matrix.length) return null;

  return {
    title,
    rowTitle,
    rows,
    columns,
    matrix,
  };
}

async function handleGraphDirectionChange(side) {
  const checkbox = document.getElementById(`graph${side}-directed`);
  const desiredDirected = !!checkbox?.checked;
  updateDirectionStatus(side, desiredDirected);

  const graphId = getEditableGraphId(side);
  if (!graphId) {
    return;
  }

  const currentGraph = graphEditState[side].graph?.graph_id === graphId
    ? graphEditState[side].graph
    : await loadGraphFromState(graphId);

  if (!currentGraph) {
    return;
  }

  if (currentGraph.directed === desiredDirected) {
    return;
  }

  try {
    await persistGraphDirection(graphId, desiredDirected);
    await refreshGraphSelectors();
    await refreshGraphViewForGraph(graphId);
    if (getGraphCategory() === 'matrices') {
      await renderMatrixExplorer(true);
    }
    logStatus(`Grafo ${graphId} cambiado a ${desiredDirected ? 'dirigido' : 'no dirigido'}.`);
  } catch (error) {
    logError(`No se pudo cambiar la dirección del grafo: ${error.message}`);
    if (checkbox) checkbox.checked = !desiredDirected;
    updateDirectionStatus(side, !desiredDirected);
  }
}

async function handleGraphWeightChange(side) {
  const checkbox = document.getElementById(`graph${side}-weighted`);
  const desiredWeighted = !!checkbox?.checked;
  updateWeightedStatus(side, desiredWeighted);

  const graphId = getEditableGraphId(side);
  if (!graphId) {
    return;
  }

  const currentGraph = graphEditState[side].graph?.graph_id === graphId
    ? graphEditState[side].graph
    : await loadGraphFromState(graphId);

  if (!currentGraph) {
    return;
  }

  if (currentGraph.weighted === desiredWeighted) {
    return;
  }

  try {
    await persistGraphWeight(graphId, desiredWeighted);
    await refreshGraphSelectors();
    await refreshGraphViewForGraph(graphId);
    logStatus(`Grafo ${graphId} cambiado a ${desiredWeighted ? 'ponderado' : 'no ponderado'}.`);
  } catch (error) {
    logError(`No se pudo cambiar la ponderación del grafo: ${error.message}`);
    if (checkbox) checkbox.checked = !desiredWeighted;
    updateWeightedStatus(side, !desiredWeighted);
  }
}

async function persistGraphDirection(graphId, directed) {
  const snapshot = await fetchJSON(`${GRAPH_API_BASE}/export`, { method: 'POST' });
  const graphs = Array.isArray(snapshot?.state?.graphs) ? snapshot.state.graphs : [];
  const targetGraph = graphs.find(graph => graph.graph_id === graphId);
  if (!targetGraph) {
    throw new Error(`No se encontró el grafo ${graphId}.`);
  }

  targetGraph.directed = directed;
  targetGraph.edges = Array.isArray(targetGraph.edges)
    ? targetGraph.edges.map(edge => ({ ...edge, directed }))
    : [];

  await fetchJSON(`${GRAPH_API_BASE}/import`, {
    method: 'POST',
    body: JSON.stringify({ snapshot }),
  });
}

async function persistGraphWeight(graphId, weighted) {
  const snapshot = await fetchJSON(`${GRAPH_API_BASE}/export`, { method: 'POST' });
  const graphs = Array.isArray(snapshot?.state?.graphs) ? snapshot.state.graphs : [];
  const targetGraph = graphs.find(graph => graph.graph_id === graphId);
  if (!targetGraph) {
    throw new Error(`No se encontró el grafo ${graphId}.`);
  }

  targetGraph.weighted = weighted;

  await fetchJSON(`${GRAPH_API_BASE}/import`, {
    method: 'POST',
    body: JSON.stringify({ snapshot }),
  });
}

async function refreshGraphViewForGraph(graphId) {
  for (const side of ['A', 'B']) {
    const sideSelect = document.getElementById(`graph${side}-select`);
    const shouldRefresh = graphEditState[side].graphId === graphId || sideSelect?.value === graphId;
    if (!shouldRefresh) continue;

    const updated = await loadGraphFromState(graphId);
    if (!updated) continue;

    setGraphState(side, updated);
    renderGraph(updated, `graph${side}-container`);
    setSummary(side, updated);
  }

  if (graphEditState.Result.graphId === graphId) {
    const updated = await loadGraphFromState(graphId);
    if (updated) {
      graphEditState.Result.graph = updated;
      renderGraph(updated, 'graphResult-container');
      setSummary('Result', updated);
    }
  }

  refreshRenderedGraphs();
}

function isElementVisible(element) {
  return !!element && window.getComputedStyle(element).display !== 'none';
}

async function renderMatrixExplorer(forceRefresh = false) {
  const graphInfo = document.getElementById('graph-info');
  if (!graphInfo) {
    return;
  }

  const explorerRoot = createMatrixExplorerShell();
  if (!explorerRoot) {
    return;
  }

  const matrixSelect = document.getElementById('matrix-graph-select-visible') || document.getElementById('matrix-graph-select');
  const output = document.getElementById('matrix-output');
  const tabsContainer = document.getElementById('matrix-tabs');
  const status = document.getElementById('matrix-status');

  const selectedGraphId = matrixSelect?.value || document.getElementById('graphA-select')?.value || matrixExplorerState.graphId || '';

  if (matrixSelect && selectedGraphId && matrixSelect.value !== selectedGraphId) {
    matrixSelect.value = selectedGraphId;
  }

  if (!selectedGraphId) {
    matrixExplorerState.graphId = '';
    matrixExplorerState.error = '';
    matrixExplorerState.loading = false;
    matrixExplorerState.matrices = {};
    if (tabsContainer) tabsContainer.innerHTML = '';
    if (status) status.textContent = 'Selecciona un grafo para ver sus matrices.';
    if (output) {
      output.innerHTML = '';
      output.appendChild(createEmptyState('No hay grafo seleccionado.'));
    }
    return;
  }

  if (!forceRefresh && matrixExplorerState.graphId === selectedGraphId && Object.keys(matrixExplorerState.matrices).length) {
    renderMatrixExplorerContent();
    return;
  }

  matrixExplorerState.graphId = selectedGraphId;
  matrixExplorerState.loading = true;
  matrixExplorerState.error = '';
  matrixExplorerState.matrices = {};
  if (status) status.textContent = 'Cargando matrices...';
  if (output) {
    output.innerHTML = '';
    output.appendChild(createEmptyState('Cargando matrices...', 'matrix-loading'));
  }

  const responses = await Promise.allSettled(
    GRAPH_MATRIX_DEFINITIONS.map(definition =>
      fetchJSON(`${GRAPH_API_BASE}/${encodeURIComponent(selectedGraphId)}/matrices/${definition.endpoint}`, { method: 'GET' })
        .then(payload => ({ key: definition.key, payload }))
    )
  );

  const matrices = {};
  const errors = [];

  responses.forEach((result, index) => {
    const definition = GRAPH_MATRIX_DEFINITIONS[index];
    if (result.status === 'fulfilled') {
      matrices[definition.key] = result.value.payload;
    } else {
      const message = result.reason?.message || 'No se pudo cargar la matriz.';
      matrices[definition.key] = { error: message };
      errors.push(`${definition.label}: ${message}`);
    }
  });

  matrixExplorerState.loading = false;
  matrixExplorerState.matrices = matrices;
  matrixExplorerState.error = errors.length === GRAPH_MATRIX_DEFINITIONS.length ? errors.join(' | ') : '';

  renderMatrixExplorerContent();
}

function renderMatrixExplorerContent() {
  const output = document.getElementById('matrix-output');
  const tabsContainer = document.getElementById('matrix-tabs');
  const status = document.getElementById('matrix-status');
  if (!output || !tabsContainer || !status) return;

  const definitions = GRAPH_MATRIX_DEFINITIONS.map(definition => ({
    ...definition,
    data: matrixExplorerState.matrices[definition.key],
  }));

  tabsContainer.innerHTML = '';
  output.innerHTML = '';

  if (matrixExplorerState.loading) {
    status.textContent = 'Cargando matrices...';
    output.appendChild(createEmptyState('Cargando matrices...', 'matrix-loading'));
    return;
  }

  if (!definitions.some(definition => definition.data && !definition.data.error)) {
    status.textContent = matrixExplorerState.error || 'No se encontraron matrices para este grafo.';
    output.appendChild(createEmptyState(matrixExplorerState.error || 'No se encontraron matrices para este grafo.'));
    return;
  }

  status.textContent = `Mostrando matrices de ${matrixExplorerState.graphId}.`;
  const activeKey = definitions.some(definition => definition.key === matrixExplorerState.activeKey && definition.data && !definition.data.error)
    ? matrixExplorerState.activeKey
    : definitions.find(definition => definition.data && !definition.data.error)?.key || 'incidence';
  matrixExplorerState.activeKey = activeKey;

  const panel = createTabbedPanel(
    definitions.map(definition => ({
      key: definition.key,
      label: definition.label,
      onSelect: key => {
        matrixExplorerState.activeKey = key;
      },
      render: () => {
        if (!definition.data || definition.data.error) {
          return createEmptyState(definition.data?.error || 'No se pudo cargar la matriz.', 'matrix-error');
        }
        const matrixData = normalizeMatrixPayload(definition.data, definition.title, definition.rowTitle);
        if (!matrixData) {
          return createEmptyState('La matriz no tiene datos válidos.', 'matrix-error');
        }
        return createMatrixTableFromData(matrixData);
      },
    })),
    activeKey,
    'matrix-tab'
  );

  output.appendChild(panel);
}

function renderResultPayload(operation, payload, visualization) {
  const container = document.getElementById('graphResult-container');
  const renderableGraph = visualization && Array.isArray(visualization.vertices) && Array.isArray(visualization.edges)
    ? visualization
    : payload && Array.isArray(payload.vertices) && Array.isArray(payload.edges)
      ? payload
      : null;

  if (renderableGraph) {
    renderGraph(renderableGraph, 'graphResult-container');
    graphEditState.Result.graph = renderableGraph;
    graphEditState.Result.graphId = renderableGraph.graph_id || null;
    setSummary('Result', renderableGraph);
  } else if (container) {
    if (cyInstances['graphResult-container']) {
      cyInstances['graphResult-container'].destroy();
      cyInstances['graphResult-container'] = null;
    }
    container.innerHTML = '<div class="placeholder">Sin vista gráfica</div>';
    const summary = document.getElementById('graphResult-summary');
    if (summary) summary.textContent = '';
    graphEditState.Result.graphId = null;
    graphEditState.Result.graph = null;
  }

  renderGraphInfo(operation, payload, renderableGraph);
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

function renderGraphInfo(operation, payload, graph) {
  const container = document.getElementById('graph-info');
  if (!container) return;
  container.innerHTML = '';

  graphEditState.Result.detail = { operation, payload, graph };

  if (!payload) {
    container.innerHTML = '<div class="placeholder">No hay detalles disponibles.</div>';
    return;
  }

  const title = document.createElement('div');
  title.className = 'graph-info-title';
  title.textContent = `Detalle: ${document.getElementById('operation-select').selectedOptions[0].textContent}`;
  container.appendChild(title);

  const summaryRow = document.createElement('div');
  summaryRow.className = 'graph-info-row';

  if (getGraphCategory() === 'operations') {
    renderOperationDetails(container, operation, payload, graph, summaryRow);
    return;
  }

  if (operation === 'vertex-coloring') {
    summaryRow.appendChild(createInfoCard('Número cromático', payload.chromatic_number));
    summaryRow.appendChild(createInfoCard('Clases de color', Object.keys(payload.chromatic_classes || {}).length));
    summaryRow.appendChild(createInfoCard('Polinomio cromático', payload.chromatic_polynomial || 'N/A'));
    container.appendChild(summaryRow);
    container.appendChild(createClassList('Colores de vértices', payload.chromatic_classes));
  } else if (operation === 'edge-coloring') {
    summaryRow.appendChild(createInfoCard('Índice cromático', payload.chromatic_index));
    summaryRow.appendChild(createInfoCard('Clases de aristas', Object.keys(payload.edge_chromatic_classes || {}).length));
    container.appendChild(summaryRow);
    container.appendChild(createClassList('Colores de aristas', payload.edge_chromatic_classes));
  } else if (operation === 'center') {
    summaryRow.appendChild(createInfoCard('Tipo', payload.type || 'N/A'));
    summaryRow.appendChild(createInfoCard('Centros', Array.isArray(payload.centers) ? payload.centers.length : 0));
    container.appendChild(summaryRow);
    container.appendChild(createClassList('Centros', { centros: payload.centers || [] }));
  } else if (operation === 'mst') {
    summaryRow.appendChild(createInfoCard('Peso total', payload.total_weight ?? 'N/A'));
    summaryRow.appendChild(createInfoCard('Rango', payload.rank ?? 'N/A'));
    summaryRow.appendChild(createInfoCard('Nulidad', payload.nullity ?? 'N/A'));
    container.appendChild(summaryRow);
    container.appendChild(createClassList('Aristas del MST', { ramas: payload.branches || [], cuerdas: payload.chords || [] }));
  } else if (operation === 'tree-distance') {
    summaryRow.appendChild(createInfoCard('Distancia', payload.distance ?? 'N/A'));
    summaryRow.appendChild(createInfoCard('Suma unión', payload.union_weight_sum ?? 'N/A'));
    summaryRow.appendChild(createInfoCard('Suma intersección', payload.intersection_weight_sum ?? 'N/A'));
    container.appendChild(summaryRow);
    container.appendChild(createClassList('Operaciones', { union: payload.union_edges || [], intersección: payload.intersection_edges || [] }));
  } else if (operation === 'ordinal') {
    summaryRow.appendChild(createInfoCard('Orden', Array.isArray(payload.traversal_order) ? payload.traversal_order.length : 0));
    container.appendChild(summaryRow);
    container.appendChild(createJsonBlock('Mapa ordinal', payload.ordinal_map || {}));
  } else if (operation === 'bellman') {
    summaryRow.appendChild(createInfoCard('Origen', payload.source || 'N/A'));
    summaryRow.appendChild(createInfoCard('Destino', payload.target || 'N/A'));
    container.appendChild(summaryRow);
    container.appendChild(createJsonBlock('Lambda', payload.lambda_values || {}));
    if (Array.isArray(payload.path) && payload.path.length) {
      container.appendChild(createOrderedList('Camino', payload.path));
    }
  } else if (operation === 'dijkstra') {
    summaryRow.appendChild(createInfoCard('Origen', payload.source || 'N/A'));
    summaryRow.appendChild(createInfoCard('Destino', payload.target || 'N/A'));
    container.appendChild(summaryRow);
    container.appendChild(createJsonBlock('Distancias', payload.distances || {}));
    if (Array.isArray(payload.path) && payload.path.length) {
      container.appendChild(createOrderedList('Camino', payload.path));
    }
  } else if (operation === 'floyd-warshall') {
    summaryRow.appendChild(createInfoCard('Vertices', graph && graph.vertices ? graph.vertices.length : 'N/A'));
    summaryRow.appendChild(createInfoCard('Ciclo negativo', payload.negative_cycle_detected ? 'Sí' : 'No'));
    container.appendChild(summaryRow);
    const vertexLabels = graph && Array.isArray(graph.vertices) ? graph.vertices.map(vertex => vertex.name) : [];
    const distanceMatrix = normalizeMatrixPayload(
      { rows: vertexLabels, cols: vertexLabels, matrix: payload.distance_matrix || [] },
      'Matriz de distancias',
      'Vértice'
    );
    const predecessorMatrix = normalizeMatrixPayload(
      { rows: vertexLabels, cols: vertexLabels, matrix: payload.predecessor_matrix || [] },
      'Matriz de predecesores',
      'Vértice'
    );
    const floydTabs = createTabbedPanel([
      {
        key: 'distance',
        label: 'Distancia',
        render: () => distanceMatrix ? createMatrixTableFromData(distanceMatrix) : createEmptyState('No hay matriz de distancias disponible.'),
      },
      {
        key: 'predecessor',
        label: 'Predecesores',
        render: () => predecessorMatrix ? createMatrixTableFromData(predecessorMatrix) : createEmptyState('No hay matriz de predecesores disponible.'),
      },
      {
        key: 'paths',
        label: 'Caminos',
        render: () => createJsonBlock('Caminos mínimos', payload.shortest_paths || {}),
      },
    ], 'distance', 'matrix-tab');
    container.appendChild(floydTabs);
  } else if (graph && Array.isArray(graph.vertices) && Array.isArray(graph.edges)) {
    summaryRow.appendChild(createInfoCard('Grafo resultante', graph.graph_id || 'resultado'));
    summaryRow.appendChild(createInfoCard('Vértices', graph.vertices.length));
    summaryRow.appendChild(createInfoCard('Aristas', graph.edges.length));
    summaryRow.appendChild(createInfoCard('Dirigido', graph.directed ? 'Sí' : 'No'));
    summaryRow.appendChild(createInfoCard('Ponderado', graph.weighted ? 'Sí' : 'No'));
    container.appendChild(summaryRow);

    if (graph.vertices.length && graph.edges.length) {
      const adjacency = createGraphInfoTable(graph);
      if (adjacency) container.appendChild(adjacency);
    }
  } else {
    container.innerHTML = '<div class="placeholder">Resultados no disponibles para esta operación.</div>';
  }
}

function renderStoredResultDetails() {
  const detail = graphEditState.Result.detail;
  if (!detail) return;
  renderGraphInfo(detail.operation, detail.payload, detail.graph);
}

function renderOperationDetails(container, operation, payload, graph, summaryRow) {
  const currentGraph = graph && Array.isArray(graph.vertices) && Array.isArray(graph.edges) ? graph : null;

  summaryRow.appendChild(createInfoCard('Tipo', document.getElementById('operation-select').selectedOptions[0]?.textContent || operation));
  summaryRow.appendChild(createInfoCard('Vértices', currentGraph?.vertices?.length ?? 0));
  summaryRow.appendChild(createInfoCard('Aristas', currentGraph?.edges?.length ?? 0));
  summaryRow.appendChild(createInfoCard('Dirigido', currentGraph?.directed ? 'Sí' : 'No'));
  summaryRow.appendChild(createInfoCard('Ponderado', currentGraph?.weighted ? 'Sí' : 'No'));
  container.appendChild(summaryRow);
  const info = createOperationSummaryList(operation, payload, currentGraph);
  if (info) container.appendChild(info);
}

function createOperationSummaryList(operation, payload, graph) {
  const wrapper = document.createElement('div');
  wrapper.className = 'graph-info-classes';
  const list = document.createElement('div');
  list.className = 'graph-info-list';

  const entries = [];
  if (operation === 'union' || operation === 'intersection' || operation === 'ring-sum' || operation === 'sum' || operation === 'cartesian-product' || operation === 'tensor-product' || operation === 'composition' || operation === 'complement') {
    entries.push(`Resultado: ${payload?.graph_id || payload?.result_id || 'N/A'}`);
    entries.push(`Vértices resultantes: ${graph?.vertices?.length ?? 0}`);
    entries.push(`Aristas resultantes: ${graph?.edges?.length ?? 0}`);
  }

  entries.forEach(text => {
    const row = document.createElement('div');
    row.textContent = text;
    list.appendChild(row);
  });

  wrapper.appendChild(list);
  return wrapper;
}

function createMatrixTable(graph, matrixType) {
  const matrixData = getGraphMatrixData(graph, matrixType);
  if (!matrixData) return null;
  return createMatrixTableFromData(matrixData);
}

function getGraphMatrixData(graph, matrixType) {
  if (!graph || !Array.isArray(graph.vertices) || !Array.isArray(graph.edges)) return null;

  const vertexLabels = graph.vertices.map(vertex => vertex.name);
  const edgeLabels = graph.edges.map(edge => edge.name);

  if (matrixType === 'incidence') {
    const matrix = vertexLabels.map(() => edgeLabels.map(() => 0));
    graph.edges.forEach((edge, edgeIndex) => {
      const sourceIndex = vertexLabels.indexOf(edge.source);
      const targetIndex = vertexLabels.indexOf(edge.target);
      if (sourceIndex >= 0) matrix[sourceIndex][edgeIndex] = edge.directed ? -1 : 1;
      if (targetIndex >= 0) matrix[targetIndex][edgeIndex] = 1;
    });
    return { title: 'Matriz de incidencia', rowTitle: 'Vértice', rows: vertexLabels, columns: edgeLabels, matrix };
  }

  if (matrixType === 'vertex-adjacency') {
    const matrix = vertexLabels.map(() => vertexLabels.map(() => 0));
    graph.edges.forEach(edge => {
      const sourceIndex = vertexLabels.indexOf(edge.source);
      const targetIndex = vertexLabels.indexOf(edge.target);
      if (sourceIndex >= 0 && targetIndex >= 0) {
        matrix[sourceIndex][targetIndex] += 1;
        if (!edge.directed) matrix[targetIndex][sourceIndex] += 1;
      }
    });
    return { title: 'Matriz de adyacencia de vértices', rowTitle: 'Vértice', rows: vertexLabels, columns: vertexLabels, matrix };
  }

  if (matrixType === 'edge-adjacency') {
    const matrix = edgeLabels.map(() => edgeLabels.map(() => 0));
    graph.edges.forEach((leftEdge, leftIndex) => {
      graph.edges.forEach((rightEdge, rightIndex) => {
        if (leftIndex === rightIndex) return;
        const leftVertices = new Set([leftEdge.source, leftEdge.target]);
        const rightVertices = new Set([rightEdge.source, rightEdge.target]);
        if ([...leftVertices].some(vertex => rightVertices.has(vertex))) {
          matrix[leftIndex][rightIndex] = 1;
        }
      });
    });
    return { title: 'Matriz de adyacencia de aristas', rowTitle: 'Arista', rows: edgeLabels, columns: edgeLabels, matrix };
  }

  return null;
}

function createGraphInfoTable(graph) {
  if (!graph || !Array.isArray(graph.vertices) || !Array.isArray(graph.edges)) return null;

  const table = document.createElement('table');
  table.className = 'graph-info-table';
  const headerRow = document.createElement('tr');
  ['Vértice', 'Aristas adjacentes'].forEach(text => {
    const th = document.createElement('th');
    th.textContent = text;
    headerRow.appendChild(th);
  });
  table.appendChild(headerRow);

  const adjacency = graph.edges.reduce((acc, edge) => {
    acc[edge.source] = acc[edge.source] || [];
    acc[edge.target] = acc[edge.target] || [];
    acc[edge.source].push(edge.name);
    if (edge.source !== edge.target) acc[edge.target].push(edge.name);
    return acc;
  }, {});
  graph.vertices.forEach(vertex => {
    const row = document.createElement('tr');
    const vertexCell = document.createElement('td');
    vertexCell.textContent = vertex.name;
    const edgesCell = document.createElement('td');
    edgesCell.textContent = (adjacency[vertex.name] || []).join(', ');
    row.appendChild(vertexCell);
    row.appendChild(edgesCell);
    table.appendChild(row);
  });

  return table;
}

function createInfoCard(label, value) {
  const card = document.createElement('div');
  card.className = 'graph-info-card';
  card.innerHTML = `<strong>${label}</strong><span>${value}</span>`;
  return card;
}

function createClassList(title, classes, flatten = false) {
  const wrapper = document.createElement('div');
  wrapper.className = 'graph-info-classes';
  const heading = document.createElement('strong');
  heading.textContent = title;
  wrapper.appendChild(heading);

  const list = document.createElement('div');
  list.className = 'graph-info-list';

  if (flatten && Array.isArray(classes)) {
    classes.forEach((item, index) => {
      const row = document.createElement('div');
      row.textContent = `${index + 1}. ${Array.isArray(item) ? item.join(', ') : item}`;
      list.appendChild(row);
    });
  } else {
    Object.entries(classes || {}).forEach(([group, items]) => {
      const row = document.createElement('div');
      row.innerHTML = `<strong>${group}</strong>: ${Array.isArray(items) ? items.join(', ') : items}`;
      list.appendChild(row);
    });
  }

  wrapper.appendChild(list);
  return wrapper;
}

function createOrderedList(title, values) {
  const wrapper = document.createElement('div');
  wrapper.className = 'graph-info-classes';
  const heading = document.createElement('strong');
  heading.textContent = title;
  wrapper.appendChild(heading);

  const list = document.createElement('div');
  list.className = 'graph-info-list';
  values.forEach((value, index) => {
    const row = document.createElement('div');
    row.textContent = `${index + 1}. ${value}`;
    list.appendChild(row);
  });

  wrapper.appendChild(list);
  return wrapper;
}

function createJsonBlock(title, value) {
  const wrapper = document.createElement('div');
  wrapper.className = 'graph-info-classes';
  const heading = document.createElement('strong');
  heading.textContent = title;
  wrapper.appendChild(heading);

  const pre = document.createElement('pre');
  pre.textContent = JSON.stringify(value, null, 2);
  wrapper.appendChild(pre);
  return wrapper;
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
  updateDirectionStatus(side, false);
  updateWeightedStatus(side, false);
  document.getElementById(`graph${side}-vertices`).value = '';
  document.getElementById(`graph${side}-edges`).value = '';
  document.getElementById(`graph${side}-delete-vertex-select`).innerHTML = '';
  document.getElementById(`graph${side}-delete-edge-select`).innerHTML = '';
  document.getElementById(`graph${side}-delete-vertex-text`).value = '';
  document.getElementById(`graph${side}-delete-edge-text`).value = '';
  const editEdgeSelect = document.getElementById(`graph${side}-edit-edge-select`);
  const editEdgeDirected = document.getElementById(`graph${side}-edit-edge-directed`);
  const editEdgeWeighted = document.getElementById(`graph${side}-edit-edge-weighted`);
  const editEdgeWeight = document.getElementById(`graph${side}-edit-edge-weight`);
  if (editEdgeSelect) editEdgeSelect.innerHTML = '';
  if (editEdgeDirected) editEdgeDirected.checked = false;
  if (editEdgeWeighted) editEdgeWeighted.checked = false;
  if (editEdgeWeight) {
    editEdgeWeight.value = '';
    editEdgeWeight.disabled = true;
  }
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
  const pathSource = document.getElementById('path-source');
  const pathTarget = document.getElementById('path-target');
  if (pathSource) pathSource.value = '';
  if (pathTarget) pathTarget.value = '';
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
  const infoContainer = document.getElementById('graph-info');
  if (infoContainer) infoContainer.innerHTML = '';
  graphEditState.Result.graphId = null;
  graphEditState.Result.graph = null;
  graphEditState.Result.detail = null;
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

  const forceTreeLabels = getGraphCategory() === 'traversals';
  const showEdgeNames = forceTreeLabels || document.getElementById('edge-label-name-toggle')?.checked;
  const showEdgeWeights = forceTreeLabels || (!!graph.weighted && document.getElementById('edge-label-weight-toggle')?.checked);
  const renderDerivedColors = containerId === 'graphResult-container';
  const vertexColorClasses = renderDerivedColors ? graph.derived?.vertex_coloring?.chromatic_classes || {} : {};
  const edgeColorClasses = renderDerivedColors ? graph.derived?.edge_coloring?.edge_chromatic_classes || {} : {};
  const vertexColorLookup = buildColorLookup(vertexColorClasses);
  const edgeColorLookup = buildColorLookup(edgeColorClasses);

  const elements = [
    ...graph.vertices.map(vertex => ({
      data: { id: vertex.name, label: vertex.name },
      style: vertexColorLookup[vertex.name]
        ? { 'background-color': vertexColorLookup[vertex.name], 'text-outline-color': vertexColorLookup[vertex.name] }
        : {},
    })),
    ...graph.edges.map(edge => ({
      data: {
        id: edge.name,
        source: edge.source,
        target: edge.target,
        label: formatEdgeLabel(edge, showEdgeNames, showEdgeWeights),
      },
      classes: edge.directed ? 'directed' : 'undirected',
      style: edgeColorLookup[edge.name] ? { 'line-color': edgeColorLookup[edge.name], 'target-arrow-color': edgeColorLookup[edge.name] } : {},
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
          'font-size': 13,
          'text-outline-width': 5,
          'text-outline-color': '#2563eb',
          width: 40,
          height: 40,
        },
      },
      {
        selector: 'edge',
        style: {
          width: 3,
          'line-color': '#9ca3af',
          'target-arrow-color': '#9ca3af',
          'curve-style': 'straight',
          'target-arrow-shape': 'triangle',
          label: 'data(label)',
          'font-size': 11,
          'text-margin-x': 0,
          'text-margin-y': -10,
          'text-rotation': 'autorotate',
          'text-background-color': '#ffffff',
          'text-background-opacity': 0.7,
          'text-background-shape': 'roundrectangle',
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
      name: 'grid',
      animate: true,
      fit: true,
      avoidOverlap: true,
      avoidOverlapPadding: 24,
      nodeDimensionsIncludeLabels: true,
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
    throw new Error(translateGraphError(payload?.detail || payload?.message || response.statusText || 'Error de red'));
  }

  return payload;
}

function logStatus(message) {
  const log = document.getElementById('graph-log');
  if (!log) return;
  const timestamp = new Date().toLocaleTimeString();
  log.textContent = `${timestamp} · ${message}\n${log.textContent}`;
}

function formatEdgeLabel(edge, showName, showWeight) {
  const labelParts = [];
  if (showName) labelParts.push(edge.name);
  if (showWeight && edge.weight != null) labelParts.push(`(${edge.weight})`);
  return labelParts.join(' ').trim();
}

function buildColorLookup(classes) {
  const lookup = {};
  const palette = generatePalette(Object.keys(classes).length);
  Object.entries(classes).forEach(([group, items], index) => {
    const color = palette[index] || '#6b7280';
    if (Array.isArray(items)) {
      items.forEach(item => {
        lookup[item] = color;
      });
    }
  });
  return lookup;
}

function generatePalette(count) {
  const defaultPalette = [
    '#2563eb', '#16a34a', '#dc2626', '#d97706', '#9333ea', '#0ea5e9', '#14b8a6', '#db2777', '#f97316', '#84cc16', '#8b5cf6', '#ec4899',
  ];
  return defaultPalette.slice(0, Math.max(1, count));
}

function logError(message) {
  const translated = translateGraphError(message);
  logStatus(`ERROR: ${translated}`);
  if (typeof window.notifyError === 'function') {
    window.notifyError(translated);
  }
}

function updateLayoutToggleIcon(button, isCompact) {
  if (!button) return;
  button.title = isCompact ? 'Disposición horizontal' : 'Disposición vertical';
  button.setAttribute('aria-label', button.title);
  button.innerHTML = isCompact
    ? '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M4 12h16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path d="M9 7l-5 5 5 5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M15 7l5 5-5 5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    : '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M12 4v16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path d="M7 9l5-5 5 5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M7 15l5 5 5-5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
}

function translateGraphError(message) {
  const text = String(message || '').trim();
  const normalized = text.toLowerCase();
  const translations = [
    ['graph already exists', 'El grafo ya existe'],
    ['snapshot type mismatch', 'El tipo de estructura no coincide'],
    ['graph direction compatibility mismatch', 'Los grafos tienen distinta dirección'],
    ['graph weight compatibility mismatch', 'Los grafos tienen distinta ponderación'],
    ['graph does not exist', 'El grafo no existe'],
    ['graph not found', 'No se encontró el grafo'],
    ['bad request', 'Solicitud incorrecta'],
    ['internal server error', 'Error interno del servidor'],
    ['failed to fetch', 'No se pudo conectar con el servidor'],
    ['error de red', 'Error de red'],
  ];

  for (const [needle, replacement] of translations) {
    if (normalized.includes(needle)) return replacement;
  }

  return text;
}
