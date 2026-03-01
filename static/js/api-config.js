// static/js/api-config.js
const API_CONFIG = {
  BASE_URL: "http://127.0.0.1:8000",
  ENDPOINTS: {
    LINEAR_SEARCH: "/linear-search",
    BINARY_SEARCH: "/binary-search",
    HASH: "/hash",
    DIGITAL_TREE: "/digital",
    SIMPLE_RESIDUE: "/simple-residue",
    MULTIPLE_RESIDUE: "/multiple-residue"
  },
  TIMEOUT: 5000,
  ANIMATION_SPEED: {
    FAST: 200,
    NORMAL: 350,
    SLOW: 500
  }
};

// Helper para fetch con timeout
async function fetchWithTimeout(url, options = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), API_CONFIG.TIMEOUT);
  
  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal
    });
    clearTimeout(timeout);
    return response;
  } catch (error) {
    clearTimeout(timeout);
    if (error.name === 'AbortError') {
      throw new Error('Tiempo de espera agotado');
    }
    throw error;
  }
}

// Helper para obtener URL completa
function getApiUrl(endpoint) {
  return API_CONFIG.BASE_URL + endpoint;
}