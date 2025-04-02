import axios from 'axios';

// Create axios instance with default config
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // Increased timeout for slower connections, especially for YouTube API
});

// Store API connection status
const API_STATUS_KEY = 'insyte_api_status';

// Check if backend is available
let isBackendAvailable = localStorage.getItem('backendAvailable') === 'true';

// Try to ping backend once at startup
const checkBackendAvailability = () => {
  console.log("Checking backend availability...");
  
  // Set a flag in localStorage to avoid showing too many errors
  const lastCheckTime = localStorage.getItem('backendCheckTime');
  const now = Date.now();
  
  // Only check once every 5 minutes
  if (lastCheckTime && (now - parseInt(lastCheckTime, 10)) < 5 * 60 * 1000) {
    console.log("Using cached backend availability status");
    isBackendAvailable = localStorage.getItem('backendAvailable') === 'true';
    return;
  }
  
  // Ping the backend
  api.get('/api/health')
    .then(() => {
      console.log("Backend is available");
      isBackendAvailable = true;
      localStorage.setItem('backendAvailable', 'true');
      localStorage.setItem('backendCheckTime', now.toString());
      localStorage.setItem(API_STATUS_KEY, JSON.stringify({
        available: true,
        lastConnected: now,
        errorCount: 0
      }));
    })
    .catch(() => {
      // Try a fallback endpoint
      api.get('/api/integrations/status')
        .then(() => {
          console.log("Backend is available (fallback check)");
          isBackendAvailable = true;
          localStorage.setItem('backendAvailable', 'true');
          localStorage.setItem('backendCheckTime', now.toString());
          localStorage.setItem(API_STATUS_KEY, JSON.stringify({
            available: true,
            lastConnected: now,
            errorCount: 0
          }));
        })
        .catch(() => {
          console.warn("Backend is not available, running in demo mode");
          isBackendAvailable = false;
          localStorage.setItem('backendAvailable', 'false');
          localStorage.setItem('backendCheckTime', now.toString());
          
          // Update API status
          const status = JSON.parse(localStorage.getItem(API_STATUS_KEY) || '{"errorCount":0}');
          localStorage.setItem(API_STATUS_KEY, JSON.stringify({
            available: false,
            lastError: now,
            errorCount: status.errorCount + 1
          }));
        });
    });
};

// Check backend availability on startup
checkBackendAvailability();

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add authentication token to all requests
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Add detailed logging for all requests
    console.log(`[API Request] ${config.method.toUpperCase()} ${config.url}`, config.params || {});
    
    // Special handling for integration endpoints
    if (config.url && config.url.includes('/api/integrations')) {
      console.log('[API] Requesting integration data with auth token:', token ? 'Present' : 'Not present');
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - for all API responses
api.interceptors.response.use(
  // Success handler - runs on any 2XX response
  (response) => {
    // Log all successful responses
    console.log(`[API Response] ${response.status} ${response.config.method.toUpperCase()} ${response.config.url}`, 
      response.data ? typeof response.data : 'No data');
    
    // Record successful API connection
    const now = Date.now();
    const status = JSON.parse(localStorage.getItem(API_STATUS_KEY) || '{"errorCount":0}');
    localStorage.setItem(API_STATUS_KEY, JSON.stringify({
      ...status,
      available: true,
      lastConnected: now
    }));
    
    // Special handling for integration status endpoint
    if (response.config.url && response.config.url.includes("/api/integrations/status")) {
      // Check if the response has the expected format
      if (!response.data || !response.data.integrations || !Array.isArray(response.data.integrations)) {
        console.warn("[API Interceptor] Invalid response format for integration status, providing fallback data");
        
        // Try to get integrations from localStorage first
        const storedIntegrations = localStorage.getItem('insyte_integrations');
        if (storedIntegrations) {
          try {
            const parsedIntegrations = JSON.parse(storedIntegrations);
            console.log('[API] Using stored integrations as fallback');
            return {
              ...response,
              data: {
                integrations: parsedIntegrations
              }
            };
          } catch (e) {
            console.error('[API] Error parsing stored integrations:', e);
          }
        }
        
        // Return a structured response with default data
        return {
          ...response,
          data: {
            integrations: [
              { platform: "youtube", status: "disconnected", account_name: null, last_sync: null, is_connected: false },
              { platform: "stripe", status: "disconnected", account_name: null, last_sync: null, is_connected: false },
              { platform: "calendly", status: "disconnected", account_name: null, last_sync: null, is_connected: false },
              { platform: "calcom", status: "disconnected", account_name: null, last_sync: null, is_connected: false }
            ]
          }
        };
      }
      
      // Store the valid response in localStorage for offline use
      localStorage.setItem('insyte_integrations_api', JSON.stringify(response.data.integrations));
      console.log('[API] Stored integration response in localStorage');
    }
    
    // Special logging for sales data
    if (response.config.url && response.config.url.includes("/api/sales/data")) {
      console.log("[API] Sales data response:", response.data);
      
      // Verify that the response contains the expected data structure
      const hasFunnel = response.data && response.data.funnel;
      const hasMetrics = response.data && response.data.metrics;
      
      console.log(`[API] Sales data structure check - Has funnel: ${hasFunnel}, Has metrics: ${hasMetrics}`);
      
      if (!hasFunnel || !hasMetrics) {
        console.warn("[API] Sales data is missing expected fields");
      }
    }
    
    return response;
  },
  
  // Error handler - runs on any non-2XX response
  (error) => {
    // Log all errors
    if (error.response) {
      console.error(`[API Error] ${error.response.status} ${error.config.method.toUpperCase()} ${error.config.url}`, 
        error.response.data);
    } else if (error.request) {
      console.error(`[API Error] No response received for ${error.config.method.toUpperCase()} ${error.config.url}`);
    } else {
      console.error(`[API Error] Request failed: ${error.message}`);
    }
    
    // Record API error
    const now = Date.now();
    const status = JSON.parse(localStorage.getItem(API_STATUS_KEY) || '{"errorCount":0}');
    localStorage.setItem(API_STATUS_KEY, JSON.stringify({
      ...status,
      available: false,
      lastError: now,
      errorCount: status.errorCount + 1
    }));
    
    // Special handling for certain status codes
    if (error.response) {
      const status = error.response.status;
      
      // Special handling for sales data endpoint
      if (error.config && error.config.url && error.config.url.includes("/api/sales/data")) {
        console.warn("[API Interceptor] Sales data API error, check backend connectivity");
      }
      
      // Special handling for integration status endpoint
      if (error.config && error.config.url && error.config.url.includes("/api/integrations/status")) {
        console.log("[API Interceptor] Integration status API error, returning stored data");
        
        // Try to get integrations from localStorage first
        const storedIntegrations = localStorage.getItem('insyte_integrations');
        if (storedIntegrations) {
          try {
            const parsedIntegrations = JSON.parse(storedIntegrations);
            if (Array.isArray(parsedIntegrations) && parsedIntegrations.length > 0) {
              console.log('[API] Using stored integrations for API error fallback');
              return Promise.resolve({
                data: {
                  integrations: parsedIntegrations
                }
              });
            }
          } catch (e) {
            console.error('[API] Error parsing stored integrations:', e);
          }
        }
        
        // Fall back to API cached value
        const apiStoredIntegrations = localStorage.getItem('insyte_integrations_api');
        if (apiStoredIntegrations) {
          try {
            const parsedIntegrations = JSON.parse(apiStoredIntegrations);
            if (Array.isArray(parsedIntegrations) && parsedIntegrations.length > 0) {
              console.log('[API] Using API-cached integrations');
              return Promise.resolve({
                data: {
                  integrations: parsedIntegrations
                }
              });
            }
          } catch (e) {
            console.error('[API] Error parsing API cached integrations:', e);
          }
        }
        
        // Return mock data as last resort
        return Promise.resolve({
          data: {
            integrations: [
              { platform: "youtube", status: "disconnected", account_name: null, last_sync: null, is_connected: false },
              { platform: "stripe", status: "disconnected", account_name: null, last_sync: null, is_connected: false },
              { platform: "calendly", status: "disconnected", account_name: null, last_sync: null, is_connected: false },
              { platform: "calcom", status: "disconnected", account_name: null, last_sync: null, is_connected: false }
            ]
          }
        });
      }
      
      // Handle unauthorized errors (401)
      if (status === 401) {
        // Redirect to login if unauthorized but don't clear integrations data
        console.log("Unauthorized API request, redirecting to login");
        // You could dispatch a logout action here or redirect to login
      }
    }
    
    // Return the error for further processing
    return Promise.reject(error);
  }
);

export default api;
export { isBackendAvailable }; 