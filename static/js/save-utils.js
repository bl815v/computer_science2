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
   * Save structure using File System Access API if available,
   * otherwise use simple download.
   * @param {string} endpoint - API endpoint for export
   * @param {string} suggestedFilename - Suggested filename
   * @param {object} config - Optional configuration
   * @returns {Promise<void>}
   */
  async function saveStructureAs(endpoint, suggestedFilename, config = null) {
    try {
      const data = await exportStructure(endpoint, config);
      
      // Validate that data is not empty
      if (!data || Object.keys(data).length === 0) {
        throw new Error('La estructura está vacía. Por favor, crea o carga una estructura antes de guardar.');
      }

      const jsonString = JSON.stringify(data, null, 2);
      
      // Double-check JSON is not empty
      if (!jsonString || jsonString.length < 3) {
        throw new Error('No se pudo serializar la estructura correctamente.');
      }

      console.debug('Saving:', jsonString.length, 'bytes');

      // Try File System Access API first
      if ('showSaveFilePicker' in window) {
        try {
          const handle = await window.showSaveFilePicker({
            suggestedName: suggestedFilename,
            types: [
              {
                description: 'JSON Files',
                accept: { 'application/json': ['.json'] },
              },
            ],
          });

          // Write file using File System Access API
          const writable = await handle.createWritable();
          await writable.write(jsonString);
          await writable.close();

          if (window.notifySuccess) {
            window.notifySuccess(`Estructura guardada como ${handle.name}`);
          }
          return;
        } catch (error) {
          if (error.name === 'AbortError') {
            // User cancelled - don't show error
            return;
          }
          console.error('File System API error:', error);
          // Fall through to simple download
        }
      }

      // Fallback: simple download (native browser behavior)
      downloadJSON(data, suggestedFilename);
      if (window.notifySuccess) {
        window.notifySuccess(`Estructura guardada como ${suggestedFilename}`);
      }
    } catch (error) {
      if (window.notifyError) {
        window.notifyError(error.message || 'Error al guardar');
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
    loadJSONFile,
    loadStructure,
  };
})();
