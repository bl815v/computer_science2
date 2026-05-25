/**
 * Save/Export utilities for search structures.
 * 
 * Provides reusable functions for exporting structures to JSON
 * and downloading them as files. Integrates with notification system.
 */

(function() {
  "use strict";

  /**
   * Export structure state via API endpoint.
   * @param {string} endpoint - API endpoint (e.g., '/binary-search/export')
   * @param {object} config - Optional configuration (size, digits, etc.)
   * @returns {Promise<object>} Exported state snapshot
   */
  async function exportStructure(endpoint, config = null) {
    try {
      const options = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      };
      
      if (config) {
        options.body = JSON.stringify(config);
      }

      const response = await fetch(`http://127.0.0.1:8000${endpoint}`, options);
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Error exporting structure');
      }

      return await response.json();
    } catch (error) {
      console.error('Export error:', error);
      throw error;
    }
  }

  /**
   * Download JSON as file.
   * @param {object} data - Data to download
   * @param {string} filename - Output filename
   */
  function downloadJSON(data, filename) {
    const jsonString = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  /**
   * Save structure to file (direct, no dialog).
   * @param {string} endpoint - API endpoint for export
   * @param {string} filename - Output filename
   * @param {object} config - Optional configuration
   * @returns {Promise<void>}
   */
  async function saveStructure(endpoint, filename, config = null) {
    try {
      const data = await exportStructure(endpoint, config);
      downloadJSON(data, filename);
      
      if (window.notifySuccess) {
        window.notifySuccess(`Estructura guardada como ${filename}`);
      }
    } catch (error) {
      if (window.notifyError) {
        window.notifyError(error.message || 'Error al guardar');
      }
      throw error;
    }
  }

  /**
   * Load JSON file from input.
   * @returns {Promise<object>} Parsed JSON data
   */
  function loadJSONFile() {
    return new Promise((resolve, reject) => {
      const input = document.createElement('input');
      input.type = 'file';
      input.accept = 'application/json';
      
      input.onchange = async (e) => {
        try {
          const file = e.target.files[0];
          if (!file) throw new Error('No file selected');
          
          const text = await file.text();
          const data = JSON.parse(text);
          resolve(data);
        } catch (error) {
          reject(error);
        }
      };
      
      input.oncancel = () => reject(new Error('File selection cancelled'));
      input.click();
    });
  }

  /**
   * Show save dialog (File System Access API with fallback).
   * @param {string} defaultFilename - Suggested filename
   * @returns {Promise<string>} Final filename to save
   */
  async function showSaveDialog(defaultFilename = 'estructura.json') {
    // Check if File System Access API is supported
    if ('showSaveFilePicker' in window) {
      try {
        const handle = await window.showSaveFilePicker({
          suggestedName: defaultFilename,
          types: [
            {
              description: 'JSON Files',
              accept: { 'application/json': ['.json'] },
            },
          ],
        });
        return handle.name;
      } catch (error) {
        if (error.name !== 'AbortError') {
          console.error('File System API error:', error);
        }
        // Fall through to modal dialog
      }
    }

    // Fallback: modal dialog for filename input
    return new Promise((resolve, reject) => {
      const overlay = document.createElement('div');
      overlay.className = 'modal-overlay';
      overlay.style.zIndex = '10000';

      const box = document.createElement('div');
      box.className = 'modal-box info';
      box.style.minWidth = '400px';

      const title = document.createElement('h3');
      title.textContent = 'Guardar estructura';
      title.style.margin = '0 0 16px 0';
      title.style.fontSize = '18px';
      title.style.fontWeight = '600';

      const label = document.createElement('label');
      label.textContent = 'Nombre del archivo:';
      label.style.display = 'block';
      label.style.marginBottom = '8px';
      label.style.fontSize = '14px';

      const input = document.createElement('input');
      input.type = 'text';
      input.value = defaultFilename.replace('.json', '');
      input.style.width = '100%';
      input.style.padding = '8px';
      input.style.marginBottom = '16px';
      input.style.border = '1px solid #d0d0d0';
      input.style.borderRadius = '2px';
      input.style.fontSize = '14px';
      input.style.boxSizing = 'border-box';
      input.focus();

      const hint = document.createElement('small');
      hint.textContent = 'Se agregará automáticamente la extensión .json';
      hint.style.color = '#666';
      hint.style.display = 'block';
      hint.style.marginBottom = '24px';

      const btnGroup = document.createElement('div');
      btnGroup.style.display = 'flex';
      btnGroup.style.gap = '8px';
      btnGroup.style.justifyContent = 'flex-end';

      const btnSave = document.createElement('button');
      btnSave.textContent = 'Guardar';
      btnSave.className = 'modal-btn';
      btnSave.style.background = 'var(--ms-blue)';
      btnSave.style.color = 'white';
      btnSave.style.border = 'none';
      btnSave.style.cursor = 'pointer';

      const btnCancel = document.createElement('button');
      btnCancel.textContent = 'Cancelar';
      btnCancel.className = 'modal-btn';
      btnCancel.style.background = 'white';
      btnCancel.style.color = 'var(--ms-error)';
      btnCancel.style.border = '1px solid var(--ms-error)';
      btnCancel.style.cursor = 'pointer';

      btnSave.addEventListener('click', () => {
        const name = input.value.trim();
        if (!name) {
          input.style.borderColor = 'var(--ms-error)';
          return;
        }
        overlay.remove();
        resolve(name.endsWith('.json') ? name : `${name}.json`);
      });

      btnCancel.addEventListener('click', () => {
        overlay.remove();
        reject(new Error('Save cancelled'));
      });

      input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') btnSave.click();
        if (e.key === 'Escape') btnCancel.click();
      });

      overlay.addEventListener('click', (e) => {
        if (e.target === overlay) btnCancel.click();
      });

      btnGroup.appendChild(btnCancel);
      btnGroup.appendChild(btnSave);

      box.appendChild(title);
      box.appendChild(label);
      box.appendChild(input);
      box.appendChild(hint);
      box.appendChild(btnGroup);
      overlay.appendChild(box);
      document.body.appendChild(overlay);
    });
  }

  /**
   * Save structure with dialog (guardar como).
   * @param {string} endpoint - API endpoint for export
   * @param {string} suggestedFilename - Suggested filename
   * @param {object} config - Optional configuration
   * @returns {Promise<void>}
   */
  async function saveStructureAs(endpoint, suggestedFilename, config = null) {
    try {
      const filename = await showSaveDialog(suggestedFilename);
      const data = await exportStructure(endpoint, config);
      downloadJSON(data, filename);
      
      if (window.notifySuccess) {
        window.notifySuccess(`Estructura guardada como ${filename}`);
      }
    } catch (error) {
      if (error.message !== 'Save cancelled') {
        if (window.notifyError) {
          window.notifyError(error.message || 'Error al guardar');
        }
      }
      throw error;
    }
  }

  /**
   * Load structure from file via API endpoint.
   * @param {string} endpoint - API endpoint for import
   * @returns {Promise<object>} Restored state snapshot
   */
  async function loadStructure(endpoint) {
    try {
      const snapshot = await loadJSONFile();
      
      const response = await fetch(`http://127.0.0.1:8000${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ snapshot }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Error loading structure');
      }

      return await response.json();
    } catch (error) {
      console.error('Load error:', error);
      throw error;
    }
  }

  // Export to window for use in other scripts
  window.saveUtils = {
    exportStructure,
    downloadJSON,
    saveStructure,
    saveStructureAs,
    showSaveDialog,
    loadJSONFile,
    loadStructure,
  };
})();
