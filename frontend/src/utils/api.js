import axios from 'axios';

// Create axios instance with default config
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 5000, // Reduced to 5 seconds to fail faster
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

// Response interceptor
api.interceptors.response.use(
  (response) => {
    // Any status code within the range of 2xx
    return response;
  },
  (error) => {
    // Handle network errors (backend not running)
    if (error.code === 'ECONNABORTED' || !error.response) {
      console.warn("Backend not responding - running in demo mode");
      isBackendAvailable = false;
      localStorage.setItem('backendAvailable', 'false');
      
      // For integrations status endpoint, provide mock data
      if (error.config && error.config.url.includes('/api/integrations/status')) {
        console.info("Returning mock data for integrations");
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
    }
    
    // Handle specific error cases
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error("API Error Response:", error.response.data);
      
      // Handle specific status codes if needed
      switch (error.response.status) {
        case 401:
          // Unauthorized - Handle auth errors
          console.error("Authentication error");
          break;
        case 403:
          // Forbidden
          console.error("Permission denied");
          break;
        case 404:
          // Not found
          console.error("Resource not found");
          break;
        case 429:
          // Too many requests
          console.error("Rate limit exceeded");
          break;
        case 500:
          // Server error
          console.error("Server error");
          break;
        default:
          // Other errors
          break;
      }
    } else if (error.request) {
      // The request was made but no response was received
      console.error("No response received:", error.request);
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error("Request setup error:", error.message);
    }
    
    // Pass the error through for the calling code to handle
    return Promise.reject(error);
  }
);

export default api;
export { isBackendAvailable }; 