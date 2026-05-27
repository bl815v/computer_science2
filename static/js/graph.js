const GRAPH_API_BASE = 'http://127.0.0.1:8000/graphs';
const cyInstances = {
  'graphA-container': null,
  'graphB-container': null,
  'graphResult-container': null,
};

const graphEditState = {
  A: { graphId: null, graph: null },
  B: { graphId: null, graph: null },
  Result: { graphId: null, graph: null },
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

  document.getElementById('graphA-id').addEventListener('input', () => loadInputGraphIfExists('A'));
  document.getElementById('graphB-id').addEventListener('input', () => loadInputGraphIfExists('B'));
  document.getElementById('graph-layout-toggle').addEventListener('click', toggleGraphLayout);

  const edgeNameToggle = document.getElementById('edge-label-name-toggle');
  const edgeWeightToggle = document.getElementById('edge-label-weight-toggle');
  if (edgeNameToggle) edgeNameToggle.addEventListener('change', refreshRenderedGraphs);
  if (edgeWeightToggle) edgeWeightToggle.addEventListener('change', refreshRenderedGraphs);
}

function updateOperationInterface() {
  const select = document.getElementById('operation-select');
  const graphBRow = document.getElementById('graphB-selector-row');
  const label = document.getElementById('execute-label');
  const unaryNote = document.getElementById('unary-note');
  const graphBPanel = document.getElementById('graphB-panel');
  const graphBCard = document.getElementById('graphB-card');
  const isColorCategory = window.graphInitialCategory === 'coloring';

  if (isColorCategory) {
    populateOperationOptions([
      { value: 'vertex-coloring', label: 'Coloreado de vértices' },
      { value: 'edge-coloring', label: 'Coloreado de aristas' },
      { value: 'independent-sets', label: 'Independencia' },
    ]);
  }

  const operation = select.value;
  const unaryOperation = operation === 'complement' || isColorOperation(operation);

  if (unaryOperation) {
    graphBRow.style.display = 'none';
    graphBPanel.style.display = 'none';
    if (graphBCard) graphBCard.style.display = 'none';
    unaryNote.textContent = 'Estas operaciones solo utilizan el grafo A.';
    label.textContent = 'Grafo A';
  } else {
    graphBRow.style.display = 'block';
    graphBPanel.style.display = 'block';
    graphBPanel.style.opacity = '1';
    graphBPanel.style.pointerEvents = 'auto';
    if (graphBCard) graphBCard.style.display = 'block';
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
    populateGraphIdDatalist(graphs);
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

function populateGraphIdDatalist(graphs) {
  const datalist = document.getElementById('graph-id-list');
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
}

function isColorOperation(operation) {
  return ['vertex-coloring', 'edge-coloring', 'independent-sets'].includes(operation);
}

function toggleGraphLayout() {
  const cards = document.getElementById('graph-cards');
  if (!cards) return;
  cards.classList.toggle('full-width');
}

function refreshRenderedGraphs() {
  if (graphEditState.A.graph) renderGraph(graphEditState.A.graph, 'graphA-container');
  if (graphEditState.B.graph) renderGraph(graphEditState.B.graph, 'graphB-container');
  if (graphEditState.Result.graph) renderGraph(graphEditState.Result.graph, 'graphResult-container');
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

  const isColorOp = isColorOperation(operation);
  if (!isColorOp && operation !== 'complement' && !graphBId) {
    logError('Selecciona un grafo B para ejecutar esta operación.');
    return;
  }

  try {
    if (isColorOp) {
      const endpoint = `${GRAPH_API_BASE}/${encodeURIComponent(graphAId)}/${operation}`;
      const payload = await fetchJSON(endpoint, {
        method: 'POST',
      });
      await refreshGraphSelectors();
      const updated = await loadGraphFromState(graphAId);
      if (updated) {
        setGraphState('A', updated);
        graphEditState.Result.graph = updated;
        graphEditState.Result.graphId = graphAId;
        renderGraph(updated, 'graphResult-container');
        setSummary('Result', updated);
        renderGraphInfo(operation, payload, updated);
      }
      logStatus(`Operación ${operation} ejecutada sobre ${graphAId}.`);
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

function renderGraphInfo(operation, payload, graph) {
  const container = document.getElementById('graph-info');
  if (!container) return;
  container.innerHTML = '';

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
  } else if (operation === 'independent-sets') {
    summaryRow.appendChild(createInfoCard('Número de independencia', payload.independence_number));
    summaryRow.appendChild(createInfoCard('Conjuntos máximos', (payload.maximum_independent_sets || []).length));
    summaryRow.appendChild(createInfoCard('Conjuntos maximales', (payload.maximal_independent_sets || []).length));
    container.appendChild(summaryRow);
    container.appendChild(createClassList('Máximos conjuntos independientes', payload.maximum_independent_sets, true));
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
    const nameCell = document.createElement('td');
    nameCell.textContent = vertex.name;
    const edgesCell = document.createElement('td');
    edgesCell.textContent = (adjacency[vertex.name] || []).join(', ') || '-';
    row.appendChild(nameCell);
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
  const infoContainer = document.getElementById('graph-info');
  if (infoContainer) infoContainer.innerHTML = '';
  graphEditState.Result.graphId = null;
  graphEditState.Result.graph = null;
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

  const showEdgeNames = document.getElementById('edge-label-name-toggle')?.checked;
  const showEdgeWeights = document.getElementById('edge-label-weight-toggle')?.checked;
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
          label: 'data(label)',
          'font-size': 10,
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
      name: 'cose',
      animate: true,
      randomize: false,
      idealEdgeLength: 100,
      nodeOverlap: 20,
      gravity: 0.15,
      edgeElasticity: 0.9,
      nestingFactor: 0.8,
      componentSpacing: 80,
      refresh: 20,
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
  logStatus(`ERROR: ${message}`);
  if (typeof window.notifyError === 'function') {
    window.notifyError(message);
  }
}
