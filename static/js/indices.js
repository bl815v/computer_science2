/* eslint-disable no-console */
(() => {
  "use strict";
  const API_BASE = "http://127.0.0.1:8000/search/index";
  let currentIndexType = "primary";

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
    currentIndexType = indexType;

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
      window.markStructureDirty?.();
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

    const statsHtml = `<div class="stats-summary" style="text-align: center; display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;">
      <div class="stat-item">Datos: ${formatNumber(b)} bloques (${bfr} reg/bloque)</div>
      <div class="stat-item">Índice: ${formatNumber(b_i)} bloques (${bfr_i} entradas/bloque)</div>
      <div class="stat-item">Accesos: ${accesses}</div>
    </div>`;

    let structuresHtml = `<div class="structures-container" style="display: flex; justify-content: center; gap: 3rem; flex-wrap: wrap; margin-top: 1rem;">`;

    if (type === "primary" || type === "secondary") {
      const blocksPerIndex = Math.ceil(b / b_i);
      const indexBlocksToShow = getIndexBlocksToShow(b_i);
      let dataBlocksToShow;
      if (type === "secondary") {
        // For secondary index: calculate which data blocks contain the referenced entries
        const dataBlocksSet = new Set();
        const entriesPerIndexBlock = Math.ceil(r / b_i);
        for (const idxBlock of indexBlocksToShow) {
          const firstEntry = (idxBlock - 1) * entriesPerIndexBlock + 1;
          const lastEntry = Math.min(idxBlock * entriesPerIndexBlock, r);
          // Convert entries to data blocks
          const firstDataBlock = Math.ceil(firstEntry / bfr);
          const lastDataBlock = Math.ceil(lastEntry / bfr);
          dataBlocksSet.add(firstDataBlock);
          dataBlocksSet.add(lastDataBlock);
        }
        dataBlocksToShow = Array.from(dataBlocksSet).sort((a, b) => a - b);
      } else {
        // For primary index: use existing logic
        dataBlocksToShow = getDataBlocksForIndexes(indexBlocksToShow, b_i, b, blocksPerIndex);
      }
      structuresHtml += generateIndexColumn(b_i, bfr_i, index_record_length, indexBlocksToShow, {
        totalTargetBlocks: b,
        blocksPerIndex,
        levelLabel: 'Índice',
        showFullIndexRanges: type === "secondary",
        totalEntries: r,
        recordsPerBlock: bfr,
      });
      structuresHtml += generateDataColumn(b, bfr, record_length, dataBlocksToShow, { totalRecords: r, recordsPerBlock: bfr });
    } else if (levels && levels.length > 0) {
      // Iterate in reverse order to show highest level first
      for (let i = levels.length - 1; i >= 0; i--) {
        const lvl = levels[i];
        const targetBlocks = i === 0 ? b : levels[i - 1].blocks;
        const blocksPerIndex = Math.ceil(targetBlocks / lvl.blocks);
        const indexBlocksToShow = getIndexBlocksToShow(lvl.blocks);
        const nextLevelBlocks = i > 0 ? levels[i - 1].blocks : b;
        structuresHtml += generateIndexColumn(lvl.blocks, bfr_i, index_record_length, indexBlocksToShow, {
          totalTargetBlocks: targetBlocks,
          blocksPerIndex,
          levelLabel: `Nivel ${i + 1}`,
          isMultilevel: true,
          isLastLevel: i === 0,
          nextLevelBlocks: nextLevelBlocks,
          nextLevelEntriesPerBlock: i > 0 ? Math.ceil(nextLevelBlocks / levels[i - 1].blocks) : bfr,
        });
      }
      const lastLevel = levels[0]; // Nivel 1 (el nivel más bajo en el orden inverso)
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
    const prefix = 'B';
    const title = extra.levelLabel || 'Índice';
    let cellsHtml = '';
    for (let i = 0; i < blocksToShow.length; i++) {
      const blockNum = blocksToShow[i];
      if (i > 0 && blockNum > blocksToShow[i-1] + 1) {
        cellsHtml += `<div class="cell dots">...</div>`;
      }
      const range = extra.showFullIndexRanges || extra.isMultilevel
        ? {
            start: (blockNum - 1) * entriesPerBlock + 1,
            end: blockNum * entriesPerBlock,
          }
        : {
            start: (blockNum - 1) * extra.blocksPerIndex + 1,
            end: blockNum * extra.blocksPerIndex,
          };
      // For multilevel indices (not last level): calculate range based on next level limits
      if (extra.isMultilevel && !extra.isLastLevel && extra.nextLevelBlocks && extra.nextLevelEntriesPerBlock) {
        const firstTargetBlock = (blockNum - 1) * extra.blocksPerIndex + 1;
        const lastTargetBlock = Math.min(blockNum * extra.blocksPerIndex, extra.nextLevelBlocks);
        const firstEntry = (firstTargetBlock - 1) * extra.nextLevelEntriesPerBlock + 1;
        const lastEntry = Math.min(lastTargetBlock * extra.nextLevelEntriesPerBlock, extra.totalTargetBlocks);
        range.start = firstEntry;
        range.end = lastEntry;
      }
      // Check if this is the last block shown AND the actual last block in the index
      const isLastBlockShown = blockNum === blocksToShow[blocksToShow.length - 1];
      const isActualLastBlock = blockNum === totalBlocks;
      let displayRange = { ...range };
      let remainingRange = null;
      if (isLastBlockShown && isActualLastBlock) {
        if (extra.showFullIndexRanges) {
          // For secondary indices: check if there's a remainder after the last full block
          if (extra.totalEntries) {
            const lastFullBlockEnd = Math.floor(extra.totalEntries / entriesPerBlock) * entriesPerBlock;
            if (lastFullBlockEnd > 0 && lastFullBlockEnd < extra.totalEntries) {
              // Show remainder in main cell, full capacity in partial cell below
              displayRange = {
                start: lastFullBlockEnd + 1,
                end: extra.totalEntries,
              };
              remainingRange = {
                start: range.start,
                end: range.end,
              };
            }
          }
        } else if (extra.isMultilevel && !extra.isLastLevel) {
          // For multilevel indices (not last level): check if there's a remainder
          const blockCapacity = entriesPerBlock * extra.nextLevelEntriesPerBlock;
          const lastFullBlockEnd = Math.floor(range.end / blockCapacity) * blockCapacity;
          if (lastFullBlockEnd > 0 && lastFullBlockEnd < range.end) {
            // Show remainder in main cell, full capacity in partial cell below
            displayRange = {
              start: lastFullBlockEnd + 1,
              end: range.end,
            };
            remainingRange = {
              start: range.start,
              end: lastFullBlockEnd,
            };
          }
        } else if (extra.isMultilevel) {
          // For multilevel indices (last level): check if there's a remainder after the last full block
          if (extra.totalTargetBlocks) {
            const lastFullBlockEnd = Math.floor(extra.totalTargetBlocks / entriesPerBlock) * entriesPerBlock;
            if (lastFullBlockEnd > 0 && lastFullBlockEnd < extra.totalTargetBlocks) {
              // Show remainder in main cell, full capacity in partial cell below
              displayRange = {
                start: lastFullBlockEnd + 1,
                end: extra.totalTargetBlocks,
              };
              remainingRange = {
                start: range.start,
                end: range.end,
              };
            }
          }
        } else {
          // For primary indices: check if there's a remainder after the last full block
          if (extra.totalTargetBlocks) {
            const lastFullBlockEnd = Math.floor(extra.totalTargetBlocks / extra.blocksPerIndex) * extra.blocksPerIndex;
            if (lastFullBlockEnd > 0 && lastFullBlockEnd < extra.totalTargetBlocks) {
              // Show remainder in main cell, full capacity in partial cell below
              displayRange = {
                start: lastFullBlockEnd + 1,
                end: extra.totalTargetBlocks,
              };
              remainingRange = {
                start: range.start,
                end: range.end,
              };
            }
          }
        }
      }

      cellsHtml += `<div class="cell index-cell" data-block="${blockNum}"

                    data-first-entry-block="${displayRange.start}"

                    data-last-entry-block="${displayRange.end}"

                    data-arrow-first-block="${displayRange.start}"

                    data-arrow-last-block="${displayRange.end}">

                      <div><strong>${prefix}${formatNumber(blockNum)}</strong></div>

                      <div style="font-size: 10px; color: var(--ms-muted);">${entriesPerBlock} entradas</div>

                      <span class="range-start top-right">${formatNumber(displayRange.start)}</span>

                      <span class="range-end bottom-right">${formatNumber(displayRange.end)}</span>

                    </div>`;

      // Add partial extension cell below if there's a remaining range
      if (remainingRange && remainingRange.start <= remainingRange.end) {

        cellsHtml += `<div class="cell index-cell partial-extension" data-block="${blockNum}.5" data-no-arrow="true">

                        <span class="range-end bottom-right">${formatNumber(remainingRange.end)}</span>

                      </div>`;

      }

    }

    return `<div class="structure-column" data-structure-type="${title}" data-is-secondary="${extra.showFullIndexRanges ? 'true' : 'false'}" data-records-per-block="${extra.recordsPerBlock || 10}">

      <div class="structure-title">${title}</div>

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

        const startRecord = (blockNum - 1) * recordsPerBlockFull + 1;

        const endRecord = totalRecords;

        const visibleRecords = Math.max(0, endRecord - startRecord + 1);

        cellsHtml += `<div class="cell data-cell" data-block="${blockNum}">

                        <div><strong>${prefix}${formatNumber(blockNum)}</strong></div>

                        <div style="font-size: 10px; color: var(--ms-muted);">${visibleRecords} registros</div>

                        <span class="range-start top-left">${formatNumber(startRecord)}</span>

                        <span class="range-end bottom-left">${formatNumber(endRecord)}</span>

                      </div>`;

      } else {

        const startRecord = (blockNum - 1) * recordsPerBlockFull + 1;

        const endRecord = Math.min(blockNum * recordsPerBlockFull, totalRecords);

        const visibleRecords = Math.max(0, endRecord - startRecord + 1);

        cellsHtml += `<div class="cell data-cell" data-block="${blockNum}">

                        <div><strong>${prefix}${formatNumber(blockNum)}</strong></div>

                        <div style="font-size: 10px; color: var(--ms-muted);">${visibleRecords} registros</div>

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



    for (let idx = 0; idx < indexColumns.length; idx++) {

      const idxCol = indexColumns[idx];

      const targetCol = idx < indexColumns.length - 1 ? indexColumns[idx + 1] : dataColumn;

      if (!targetCol) continue;

      const targetCells = Array.from(targetCol.querySelectorAll('.cell:not(.dots)'));

      const targetMap = new Map();

      targetCells.forEach(cell => {

        const blockNum = parseInt(cell.dataset.block, 10);

        if (!isNaN(blockNum)) targetMap.set(blockNum, cell);

      });



      const idxCells = Array.from(idxCol.querySelectorAll('.cell:not(.dots)'));

      for (const idxCell of idxCells) {

        if (idxCell.dataset.noArrow === 'true') {
          continue;
        }

        const firstBlock = parseInt(idxCell.dataset.arrowFirstBlock || idxCell.dataset.firstEntryBlock, 10);

        const lastBlock = parseInt(idxCell.dataset.arrowLastBlock || idxCell.dataset.lastEntryBlock, 10);

        // Check if this is a secondary index column
        const isSecondaryIndex = idxCol.dataset.isSecondary === 'true';

        // Check if this is a multilevel index connection (not to data)
        const isMultilevelConnection = idxCol.dataset.isSecondary !== 'true' && !targetCol.querySelector('.structure-title')?.textContent.includes('Datos');

        let firstTargetCell, lastTargetCell;

        if (isSecondaryIndex && targetCol.querySelector('.structure-title')?.textContent.includes('Datos')) {
          // For secondary indices: convert entry numbers to data block numbers
          const recordsPerBlock = parseInt(idxCol.dataset.recordsPerBlock || '10', 10);
          const firstDataBlock = Math.ceil(firstBlock / recordsPerBlock);
          const lastDataBlock = Math.ceil(lastBlock / recordsPerBlock);

          firstTargetCell = findTargetCellForBlock(targetCells, targetMap, firstDataBlock);
          lastTargetCell = findTargetCellForBlock(targetCells, targetMap, lastDataBlock);
        } else {
          // For primary indices: use block numbers directly
          firstTargetCell = findTargetCellForBlock(targetCells, targetMap, firstBlock);
          lastTargetCell = findTargetCellForBlock(targetCells, targetMap, lastBlock);
        }

        if (firstTargetCell) {

          drawArrowBetween(ctx, idxCell, firstTargetCell, container, 'top');

        }

        if (lastTargetCell && lastTargetCell !== firstTargetCell) {

          // For multilevel connections: find the last non-partial cell in target column
          let targetCellForArrow = lastTargetCell;
          if (isMultilevelConnection) {
            const nonPartialCells = Array.from(targetCells).filter(cell => cell.dataset.noArrow !== 'true');
            if (nonPartialCells.length > 0) {
              targetCellForArrow = nonPartialCells[nonPartialCells.length - 1];
            }
          }

          drawArrowBetween(ctx, idxCell, targetCellForArrow, container, 'bottom', isMultilevelConnection);

        }

      }

    }

  }



  function findTargetCellForBlock(targetCells, targetMap, blockNum) {

    if (isNaN(blockNum)) return null;

    if (targetMap.has(blockNum)) return targetMap.get(blockNum);



    let fallbackCell = null;

    let smallestSpan = Number.POSITIVE_INFINITY;



    for (const cell of targetCells) {

      const start = parseInt(cell.dataset.firstEntryBlock, 10);

      const end = parseInt(cell.dataset.lastEntryBlock, 10);

      if (isNaN(start) || isNaN(end)) continue;

      if (blockNum >= start && blockNum <= end) {

        const span = end - start;

        if (span < smallestSpan) {

          fallbackCell = cell;

          smallestSpan = span;

        }

      }

    }



    return fallbackCell;

  }



  function drawArrowBetween(ctx, fromCell, toCell, container, position = 'top', isMultilevelConnection = false) {

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

    // For multilevel connections: use top-left corner of target cell
    if (isMultilevelConnection) {
      // Already using top-left corner (endX, endY)
    }

    

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



  // ===================== EXPORTAR / IMPORTAR =====================

  window.exportIndex = async () => {

    const type = document.getElementById("index-type").value;

    let endpoint = '';

    switch (type) {

      case 'primary': endpoint = '/search/index/primary/export'; break;

      case 'secondary': endpoint = '/search/index/secondary/export'; break;

      case 'multilevel-primary': endpoint = '/search/index/multilevel-primary/export'; break;

      case 'multilevel-secondary': endpoint = '/search/index/multilevel-secondary/export'; break;

      default: return;

    }

    try {

      const response = await fetch(`http://127.0.0.1:8000${endpoint}`, {

        method: 'POST',

        headers: { 'Content-Type': 'application/json' }

      });

      if (!response.ok) throw new Error('Error al exportar');

      const data = await response.json();

      data.index = type;   // Guardar el subtipo de índice sin cambiar el snapshot.type

      const filename = `indice_${type}.json`;

      window.saveUtils.downloadJSON(data, filename);

      window.notifySuccess?.(`Índice guardado como ${filename}`);

    } catch (err) {

      window.notifyError?.('Error al guardar el índice');

    }

  };



  function getImportEndpoint(type) {

    switch (type) {

      case 'primary': return '/search/index/primary/import';

      case 'secondary': return '/search/index/secondary/import';

      case 'multilevel-primary': return '/search/index/multilevel-primary/import';

      case 'multilevel-secondary': return '/search/index/multilevel-secondary/import';

      default: return '/search/index/primary/import';

    }

  }



  window.importIndex = async () => {

    try {

      const snapshot = await window.saveUtils.loadJSONFile();

      if (!snapshot || (!snapshot.type && !snapshot.index)) {

        throw new Error('Archivo inválido: no contiene el tipo de índice');

      }

      const type = snapshot.index || snapshot.type;

      const validTypes = ['primary', 'secondary', 'multilevel-primary', 'multilevel-secondary'];

      if (!validTypes.includes(type)) {

        throw new Error(`Tipo de índice desconocido: ${type}`);

      }



      const config = snapshot.config || {};

      const totalRecordsInput = document.getElementById('total-records');

      const blockSizeInput = document.getElementById('block-size');

      const recordLengthInput = document.getElementById('record-length');

      const indexRecordLengthInput = document.getElementById('index-record-length');

      if (totalRecordsInput) totalRecordsInput.value = String(config.r || totalRecordsInput.value);

      if (blockSizeInput) blockSizeInput.value = String(config.block_size || blockSizeInput.value);

      if (recordLengthInput) recordLengthInput.value = String(config.record_length || recordLengthInput.value);

      if (indexRecordLengthInput) indexRecordLengthInput.value = String(config.index_record_length || indexRecordLengthInput.value);



      // Cambiar el select al tipo correspondiente

      const select = document.getElementById('index-type');

      if (select) select.value = type;

      currentIndexType = type;



      // El backend siempre valida snapshot.type como 'index' para las estructuras de índices.

      snapshot.type = 'index';

      snapshot.index = type;



      const importEndpoint = getImportEndpoint(type);

      const response = await fetch(`http://127.0.0.1:8000${importEndpoint}`, {

        method: 'POST',

        headers: { 'Content-Type': 'application/json' },

        body: JSON.stringify({ snapshot })

      });

      if (!response.ok) {

        const err = await response.json();

        throw new Error(err.detail || 'Error al cargar el índice');

      }

      await window.refreshStructure();

      window.notifySuccess?.('Estructura de índices cargada correctamente');

    } catch (err) {

      window.notifyError?.(err.message || 'Error al cargar el índice');

    }

  };



  window.refreshStructure = async () => {

    const type = currentIndexType;

    const endpoint = getEndpoint(type);

    const r = parseInt(document.getElementById("total-records").value, 10);

    const block_size = parseInt(document.getElementById("block-size").value, 10);

    const record_length = parseInt(document.getElementById("record-length").value, 10);

    const index_record_length = parseInt(document.getElementById("index-record-length").value, 10);

    if (isNaN(r) || isNaN(block_size) || isNaN(record_length) || isNaN(index_record_length)) {

      return;

    }

    try {

      const response = await fetch(endpoint, {

        method: "POST",

        headers: { "Content-Type": "application/json" },

        body: JSON.stringify({ r, block_size, record_length, index_record_length }),

      });

      if (!response.ok) throw new Error();

      const data = await response.json();

      drawStructures(data, type, { r, block_size, record_length, index_record_length });

      const resultsDiv = document.getElementById("results-section");

      if (resultsDiv) resultsDiv.style.display = "block";

    } catch (err) {

      console.error("Error al refrescar índices:", err);

    }

  };



  // ===================== INICIALIZACIÓN =====================

  window.initSimulator = () => {

    const btn = document.getElementById("calculate-btn");

    if (btn) btn.addEventListener("click", calculate);

    const resultsDiv = document.getElementById("results-section");

    if (resultsDiv) resultsDiv.style.display = "none";

    window.addEventListener('resize', () => {

      if (document.querySelector('.structures-container')) {

        requestAnimationFrame(() => {

          drawArrowsByTarget();

        });

      }

    });

  };

})();