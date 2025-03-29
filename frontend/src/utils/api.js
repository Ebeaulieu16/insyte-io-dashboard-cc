import axios from 'axios';

// Create axios instance with default config
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 5000, // Reduced timeout for faster error response
});

// Check if backend is available
let isBackendAvailable = false;

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
  api.get('/')
    .then(() => {
      console.log("Backend is available");
      isBackendAvailable = true;
      localStorage.setItem('backendAvailable', 'true');
    })
    .catch(() => {
      console.warn("Backend is not available, running in demo mode");
      isBackendAvailable = false;
      localStorage.setItem('backendAvailable', 'false');
    })
    .finally(() => {
      localStorage.setItem('backendCheckTime', now.toString());
    });
};

// Check backend availability on startup
checkBackendAvailability();

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // You can add auth tokens or other headers here if needed
    // const token = localStorage.getItem('token');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - this is the key part that handles API failures
api.interceptors.response.use(
  (response) => {
    // Any status code within the range of 2xx
    return response;
  },
  (error) => {
    // Special handling for integration status endpoint
    if (error.config && error.config.url && error.config.url.includes('/api/integrations/status')) {
      console.warn("Integration status API error, returning fallback data");
      
      // Return mock data for integrations
      return Promise.resolve({
        data: {
          integrations: [
            {
              platform: "youtube",
              status: "disconnected",
              last_sync: null,
              account_name: null
            },
            {
              platform: "stripe", 
              status: "disconnected",
              last_sync: null,
              account_name: null
            },
            {
              platform: "calendly",
              status: "disconnected",
              last_sync: null,
              account_name: null
            },
            {
              platform: "calcom",
              status: "disconnected",
              last_sync: null,
              account_name: null
            }
          ]
        }
      });
    }
    
    // For all other API errors, just pass them through
    return Promise.reject(error);
  }
);

export default api;
export { isBackendAvailable }; 