import axios from 'axios';

// Create axios instance with default config
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000, // 15 seconds timeout
});

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