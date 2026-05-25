/* eslint-disable no-console */
(() => {
  "use strict";

  const API_BASE = "http://127.0.0.1:8000/search/index";

  function getEndpoint(type) {
    switch (type) {
      case "primary": return `${API_BASE}/primary`;
      case "secondary": return `${API_BASE}/secondary`;
      case "multilevel-primary": return `${API_BASE}/multilevel-primary`;
      case "multilevel-secondary": return `${API_BASE}/multilevel-secondary`;
      default: return `${API_BASE}/primary`;
    }
  }

  function formatNumber(n) {
    return n.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  }

  async function calculate() {
    const r = parseInt(document.getElementById("total-records").value, 10);
    const block_size = parseInt(document.getElementById("block-size").value, 10);
    const record_length = parseInt(document.getElementById("record-length").value, 10);
    const index_record_length = parseInt(document.getElementById("index-record-length").value, 10);
    const indexType = document.getElementById("index-type").value;

    if (isNaN(r) || isNaN(block_size) || isNaN(record_length) || isNaN(index_record_length)) {
      window.notifyError?.("Complete todos los campos numéricos");
      return;
    }

    const resultsDiv = document.getElementById("results-section");
    const vizDiv = document.getElementById("visualization");
    resultsDiv.style.display = "block";
    vizDiv.innerHTML = '<div class="loading-overlay">🖌️ Generando estructura...</div>';

    try {
      const endpoint = getEndpoint(indexType);
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ r, block_size, record_length, index_record_length }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Error en el cálculo");
      }

      const data = await response.json();
      drawStructures(data, indexType, { r, block_size, record_length, index_record_length });
      window.notifySuccess?.("Estructura calculada correctamente");
    } catch (err) {
      window.notifyError?.(err.message);
      vizDiv.innerHTML = '<div class="error-message">No se pudo generar la visualización</div>';
    }
  }

  function drawStructures(data, type, params) {
    const container = document.getElementById("visualization");
    if (!container) return;

    const { bfr, b, bfr_i, b_i, accesses, levels } = data;
    const { r, record_length, index_record_length } = params;

    // Estadísticas centradas
    const statsHtml = `<div class="stats-summary" style="text-align: center; display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;">
      <div class="stat-item">Datos: ${formatNumber(b)} bloques (${bfr} reg/bloque)</div>
      <div class="stat-item">Índice: ${formatNumber(b_i)} bloques (${bfr_i} entradas/bloque)</div>
      <div class="stat-item">Accesos: ${accesses}</div>
    </div>`;

    let structuresHtml = `<div class="structures-container" style="display: flex; justify-content: center; gap: 3rem; flex-wrap: wrap; margin-top: 1rem;">`;
    
    if (type === "primary" || type === "secondary") {
      const blocksPerIndex = Math.ceil(b / b_i);
      const indexBlocksToShow = getIndexBlocksToShow(b_i);
      const dataBlocksToShow = getDataBlocksForIndexes(indexBlocksToShow, b_i, b, blocksPerIndex);
      structuresHtml += generateIndexColumn(b_i, bfr_i, index_record_length, indexBlocksToShow, { totalDataBlocks: b, blocksPerIndex });
      structuresHtml += generateDataColumn(b, bfr, record_length, dataBlocksToShow, { totalRecords: r, recordsPerBlock: bfr });
    } else if (levels && levels.length > 0) {
      for (let i = 0; i < levels.length; i++) {
        const lvl = levels[i];
        const blocksPerIndex = Math.ceil(b / lvl.blocks);
        const indexBlocksToShow = getIndexBlocksToShow(lvl.blocks);
        structuresHtml += generateIndexColumn(lvl.blocks, bfr_i, index_record_length, indexBlocksToShow, { totalDataBlocks: b, blocksPerIndex });
      }
      const lastLevel = levels[levels.length-1];
      const blocksPerIndexLast = Math.ceil(b / lastLevel.blocks);
      const lastIndexBlocks = getIndexBlocksToShow(lastLevel.blocks);
      const dataBlocksToShow = getDataBlocksForIndexes(lastIndexBlocks, lastLevel.blocks, b, blocksPerIndexLast);
      structuresHtml += generateDataColumn(b, bfr, record_length, dataBlocksToShow, { totalRecords: r, recordsPerBlock: bfr });
    }

    structuresHtml += `</div>`;
    container.innerHTML = statsHtml + structuresHtml;

    setTimeout(() => {
      drawArrowsByTarget();
    }, 50);
  }

  function getIndexBlocksToShow(totalIndexBlocks) {
    if (totalIndexBlocks <= 3) {
      return Array.from({ length: totalIndexBlocks }, (_, i) => i + 1);
    }
    const middle = Math.floor(totalIndexBlocks / 2);
    return [1, middle, totalIndexBlocks];
  }

  function getDataBlocksForIndexes(indexBlocks, totalIndexBlocks, totalDataBlocks, blocksPerIndex) {
    const dataBlocksSet = new Set();
    for (const idxBlock of indexBlocks) {
      const firstEntryBlock = (idxBlock - 1) * blocksPerIndex + 1;
      const lastEntryBlock = Math.min(idxBlock * blocksPerIndex, totalDataBlocks);
      dataBlocksSet.add(firstEntryBlock);
      dataBlocksSet.add(lastEntryBlock);
    }
    dataBlocksSet.add(1);
    dataBlocksSet.add(totalDataBlocks);
    return Array.from(dataBlocksSet).sort((a,b) => a-b);
  }

  function generateIndexColumn(totalBlocks, entriesPerBlock, bytes, blocksToShow, extra) {
    const prefix = 'B'; // Cambiado de 'I' a 'B'
    let cellsHtml = '';
    for (let i = 0; i < blocksToShow.length; i++) {
      const blockNum = blocksToShow[i];
      if (i > 0 && blockNum > blocksToShow[i-1] + 1) {
        cellsHtml += `<div class="cell dots">...</div>`;
      }
      const firstEntryBlock = (blockNum - 1) * extra.blocksPerIndex + 1;
      const lastEntryBlock = Math.min(blockNum * extra.blocksPerIndex, extra.totalDataBlocks);
      cellsHtml += `<div class="cell index-cell" data-block="${blockNum}" 
                    data-first-entry-block="${firstEntryBlock}" 
                    data-last-entry-block="${lastEntryBlock}">
                      <div><strong>${prefix}${formatNumber(blockNum)}</strong></div>
                      <div style="font-size: 10px; color: var(--ms-muted);">${entriesPerBlock} entradas</div>
                      <span class="range-start top-right">${formatNumber(firstEntryBlock)}</span>
                      <span class="range-end bottom-right">${formatNumber(lastEntryBlock)}</span>
                    </div>`;
    }
    return `<div class="structure-column" data-structure-type="Índice">
      <div class="structure-title">Índice</div>
      <div class="structure-size">${bytes} bytes por entrada</div>
      <div class="cell-list">${cellsHtml}</div>
    </div>`;
  }

  function generateDataColumn(totalBlocks, entriesPerBlock, bytes, blocksToShow, extra) {
    const prefix = 'B';
    let cellsHtml = '';
    const recordsPerBlockFull = extra.recordsPerBlock;
    const totalRecords = extra.totalRecords;
    const totalDataBlocks = Math.ceil(totalRecords / recordsPerBlockFull);
    for (let i = 0; i < blocksToShow.length; i++) {
      const blockNum = blocksToShow[i];
      if (i > 0 && blockNum > blocksToShow[i-1] + 1) {
        cellsHtml += `<div class="cell dots">...</div>`;
      }
      if (blockNum === totalDataBlocks) {
        // Último bloque: usar r y r - registrosPorBloque + 1
        const startRecord = totalRecords - recordsPerBlockFull + 1;
        const endRecord = totalRecords;
        cellsHtml += `<div class="cell data-cell" data-block="${blockNum}">
                        <div><strong>${prefix}${formatNumber(blockNum)}</strong></div>
                        <div style="font-size: 10px; color: var(--ms-muted);">${entriesPerBlock} registros</div>
                        <span class="range-start top-left">${formatNumber(startRecord)}</span>
                        <span class="range-end bottom-left">${formatNumber(endRecord)}</span>
                      </div>`;
      } else {
        const recordsInThisBlock = recordsPerBlockFull;
        const startRecord = (blockNum - 1) * recordsPerBlockFull + 1;
        const endRecord = startRecord + recordsInThisBlock - 1;
        cellsHtml += `<div class="cell data-cell" data-block="${blockNum}">
                        <div><strong>${prefix}${formatNumber(blockNum)}</strong></div>
                        <div style="font-size: 10px; color: var(--ms-muted);">${entriesPerBlock} registros</div>
                        <span class="range-start top-left">${formatNumber(startRecord)}</span>
                        <span class="range-end bottom-left">${formatNumber(endRecord)}</span>
                      </div>`;
      }
    }
    return `<div class="structure-column" data-structure-type="Datos">
      <div class="structure-title">Datos</div>
      <div class="structure-size">${bytes} bytes por registro</div>
      <div class="cell-list">${cellsHtml}</div>
    </div>`;
  }

  function drawArrowsByTarget() {
    const container = document.querySelector('.structures-container');
    if (!container) return;

    let canvas = document.querySelector('.arrows-canvas');
    if (!canvas) {
      canvas = document.createElement('canvas');
      canvas.className = 'arrows-canvas';
      container.style.position = 'relative';
      container.appendChild(canvas);
    }
    const rect = container.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;
    canvas.style.width = `${rect.width}px`;
    canvas.style.height = `${rect.height}px`;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const columns = document.querySelectorAll('.structure-column');
    if (columns.length < 2) return;

    const dataColumn = Array.from(columns).find(col => col.querySelector('.structure-title')?.textContent.includes('Datos'));
    const indexColumns = Array.from(columns).filter(col => col !== dataColumn);

    if (!dataColumn || indexColumns.length === 0) return;

    const dataCells = Array.from(dataColumn.querySelectorAll('.cell:not(.dots)'));
    const dataBlockMap = new Map();
    dataCells.forEach(cell => {
      const blockNum = parseInt(cell.dataset.block, 10);
      if (!isNaN(blockNum)) dataBlockMap.set(blockNum, cell);
    });

    for (const idxCol of indexColumns) {
      const idxCells = Array.from(idxCol.querySelectorAll('.cell:not(.dots)'));
      for (const idxCell of idxCells) {
        const firstBlock = parseInt(idxCell.dataset.firstEntryBlock, 10);
        const lastBlock = parseInt(idxCell.dataset.lastEntryBlock, 10);
        if (!isNaN(firstBlock) && dataBlockMap.has(firstBlock)) {
          drawArrowBetween(ctx, idxCell, dataBlockMap.get(firstBlock), container, 'top');
        }
        if (!isNaN(lastBlock) && dataBlockMap.has(lastBlock)) {
          drawArrowBetween(ctx, idxCell, dataBlockMap.get(lastBlock), container, 'bottom');
        }
      }
    }
  }

  function drawArrowBetween(ctx, fromCell, toCell, container, position = 'top') {
    const fromRect = fromCell.getBoundingClientRect();
    const toRect = toCell.getBoundingClientRect();
    const containerRect = container.getBoundingClientRect();

    let startX, startY;
    if (position === 'top') {
      startX = fromRect.right - containerRect.left - 5;
      startY = fromRect.top - containerRect.top + 8;
    } else {
      startX = fromRect.right - containerRect.left - 5;
      startY = fromRect.bottom - containerRect.top - 8;
    }
    const endX = toRect.left - containerRect.left + 5;
    const endY = toRect.top - containerRect.top + 8;
    
    drawSingleArrow(ctx, startX, startY, endX, endY);
  }

  function drawSingleArrow(ctx, fromX, fromY, toX, toY) {
    ctx.beginPath();
    ctx.moveTo(fromX, fromY);
    ctx.lineTo(toX, toY);
    ctx.strokeStyle = '#d13438';
    ctx.lineWidth = 2;
    ctx.setLineDash([5, 5]);
    ctx.stroke();
    
    const angle = Math.atan2(toY - fromY, toX - fromX);
    const arrowSize = 8;
    const arrowX = toX;
    const arrowY = toY;
    ctx.fillStyle = '#d13438';
    ctx.beginPath();
    ctx.moveTo(arrowX, arrowY);
    ctx.lineTo(arrowX - arrowSize * Math.cos(angle - Math.PI/6), arrowY - arrowSize * Math.sin(angle - Math.PI/6));
    ctx.lineTo(arrowX - arrowSize * Math.cos(angle + Math.PI/6), arrowY - arrowSize * Math.sin(angle + Math.PI/6));
    ctx.fill();
    ctx.setLineDash([]);
  }

  window.initSimulator = () => {
    const btn = document.getElementById("calculate-btn");
    if (btn) btn.addEventListener("click", calculate);
    const resultsDiv = document.getElementById("results-section");
    if (resultsDiv) resultsDiv.style.display = "none";
    window.addEventListener('resize', () => {
      if (document.querySelector('.structures-container')) {
        drawArrowsByTarget();
      }
    });
  };
})();