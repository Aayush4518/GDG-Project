import axios from 'axios';

// Base URL for the backend API
const API_BASE_URL = 'http://localhost:8000/api/v1';

// In-memory token store (cleared on page reload — use sessionStorage for persistence)
let _authToken = null;

export function setAuthToken(token) {
  _authToken = token;
  if (token) {
    sessionStorage.setItem('auth_token', token);
  } else {
    sessionStorage.removeItem('auth_token');
  }
}

export function loadStoredToken() {
  const stored = sessionStorage.getItem('auth_token');
  if (stored) _authToken = stored;
  return stored;
}

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor — attach JWT if available
apiClient.interceptors.request.use(
  (config) => {
    if (_authToken) {
      config.headers['Authorization'] = `Bearer ${_authToken}`;
    }
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      console.warn('Session expired or unauthorized. Clearing auth state.');
      setAuthToken(null);
    }
    console.error('API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

/**
 * Centralized API Service for Dashboard
 * Handles all backend communication for the authorities' web dashboard
 */
export const apiService = {
  /**
   * Authenticate a dashboard authority user (Police / Tourism officer).
   * On success, stores the JWT token for subsequent requests.
   * @param {string} username
   * @param {string} password
   * @returns {Promise<{role: string, username: string}>}
   */
  async loginAuthority(username, password) {
    const response = await apiClient.post('/auth/authority/login', { username, password });
    const { access_token, role, username: resolvedUsername } = response.data;
    setAuthToken(access_token);
    return { role, username: resolvedUsername };
  },

  /**
   * Clear the stored auth token (logout).
   */
  logout() {
    setAuthToken(null);
  },

  /**
   * Get all active tourists with their current locations
   * @returns {Promise<Array>} Array of tourist objects with location data
   */
  async getActiveTourists() {
    try {
      const response = await apiClient.get('/dashboard/active-tourists');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch active tourists:', error);
      // Fallback to massive dummy data
      try {
        const fallbackResponse = await fetch('/massive_tourists.json');
        const dummyData = await fallbackResponse.json();
        console.log('✅ Using massive dummy tourists data as fallback (500 entries)');
        return dummyData;
      } catch (fallbackError) {
        console.error('Fallback data also failed:', fallbackError);
        throw new Error('Unable to load active tourists. Please try again.');
      }
    }
  },

  /**
   * Get dashboard analytics and statistics
   * @returns {Promise<Object>} Analytics data including counts and trends
   */
  async getAnalytics() {
    try {
      const response = await apiClient.get('/dashboard/analytics');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
      // Fallback to dummy analytics
      try {
        const fallbackResponse = await fetch('/analytics.json');
        const dummyData = await fallbackResponse.json();
        console.log('✅ Using dummy analytics data as fallback');
        return dummyData;
      } catch (fallbackError) {
        console.error('Fallback analytics also failed:', fallbackError);
        throw new Error('Unable to load analytics data. Please try again.');
      }
    }
  },

  /**
   * Get detailed information about a specific tourist
   * @param {string} touristId - The tourist's unique identifier
   * @returns {Promise<Object>} Detailed tourist information including location history
   */
  async getTouristDetails(touristId) {
    try {
      const response = await apiClient.get(`/tourists/${touristId}/details`);
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch details for tourist ${touristId}:`, error);
      throw new Error('Unable to load tourist details. Please try again.');
    }
  },

  /**
   * Generate E-FIR (Electronic First Information Report) for a tourist
   * @param {string} touristId - The tourist's unique identifier
   * @returns {Promise<Blob>} PDF file as blob for download
   */
  async generateEFIR(touristId) {
    try {
      const response = await apiClient.post(`/tourists/${touristId}/generate-efir`, {}, {
        responseType: 'blob', // Important for PDF files
        headers: {
          'Accept': 'application/pdf',
        },
      });
      return response.data;
    } catch (error) {
      console.error(`Failed to generate E-FIR for tourist ${touristId}:`, error);
      throw new Error('Unable to generate E-FIR. Please try again.');
    }
  },

  /**
   * Verify blockchain ledger integrity
   * @returns {Promise<Object>} Verification result with status and details
   */
  async verifyLedger() {
    try {
      const response = await apiClient.get('/dashboard/ledger/verify');
      return response.data;
    } catch (error) {
      console.error('Failed to verify ledger:', error);
      throw new Error('Unable to verify ledger integrity. Please try again.');
    }
  },

  /**
   * Get risk zones for map display
   * @returns {Promise<Array>} Array of risk zone objects with coordinates
   */
  async getRiskZones() {
    try {
      const response = await apiClient.get('/dashboard/risk-zones');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch risk zones:', error);
      // Return empty array as fallback - risk zones are optional
      return [];
    }
  },

  /**
   * Test connection to backend
   * @returns {Promise<boolean>} True if backend is reachable
   */
  async testConnection() {
    try {
      await apiClient.get('/dashboard/analytics');
      return true;
    } catch (error) {
      console.error('Backend connection test failed:', error);
      return false;
    }
  }
};

export default apiService;
