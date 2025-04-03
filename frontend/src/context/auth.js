import { createContext, useContext, useState, useEffect } from "react";
import axios from "axios";
import { toast } from "react-toastify";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

// Create context
const AuthContext = createContext();

// Export the context for use in components
export const useAuth = () => useContext(AuthContext);

// Helper function to clear integration data 
// (defined here to avoid circular dependencies with IntegrationContext)
const clearIntegrationData = () => {
  // Helper function to clear all integration-related data from localStorage
  const INTEGRATIONS_STORAGE_KEY = 'insyte_integrations';
  const INTEGRATIONS_TIMESTAMP_KEY = 'insyte_integrations_timestamp';
  
  // Clear all integration-related data
  localStorage.removeItem(INTEGRATIONS_STORAGE_KEY);
  localStorage.removeItem(INTEGRATIONS_TIMESTAMP_KEY);
  
  // Clear any user-specific keys that might exist
  const allKeys = Object.keys(localStorage);
  const integrationKeys = allKeys.filter(key => 
    key.startsWith(INTEGRATIONS_STORAGE_KEY) || 
    key.startsWith(INTEGRATIONS_TIMESTAMP_KEY)
  );
  
  integrationKeys.forEach(key => localStorage.removeItem(key));
};

// Provider component
export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem("token") || null);
  const [loading, setLoading] = useState(true);

  // Set up axios interceptor for authentication
  useEffect(() => {
    // Add a request interceptor to include the auth token in all requests
    const interceptor = axios.interceptors.request.use(
      (config) => {
        // If token exists, add it to the authorization header
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Remove interceptor on cleanup
    return () => {
      axios.interceptors.request.eject(interceptor);
    };
  }, [token]);

  // Load user from storage on mount
  useEffect(() => {
    const fetchCurrentUser = async () => {
      try {
        // If we have a token, try to get the user profile
        if (token) {
          const user = JSON.parse(localStorage.getItem("user") || "null");
          
          // If we have a user in storage, use it
          if (user) {
            setCurrentUser(user);
          } else {
            // Otherwise, fetch from API
            const response = await axios.get(`${API_URL}/auth/me`);
            setCurrentUser(response.data);
            localStorage.setItem("user", JSON.stringify(response.data));
          }
        }
      } catch (error) {
        console.error("Error loading user:", error);
        logout();
      } finally {
        setLoading(false);
      }
    };

    fetchCurrentUser();
  }, [token]);

  // Login function
  const login = async (email, password) => {
    try {
      const response = await axios.post(`${API_URL}/auth/token`, {
        email,
        password,
      });

      const { access_token, user } = response.data;

      // Save to state and localStorage
      setToken(access_token);
      setCurrentUser(user);
      localStorage.setItem("token", access_token);
      localStorage.setItem("user", JSON.stringify(user));

      toast.success("Login successful!");
      return true;
    } catch (error) {
      console.error("Login error:", error);
      toast.error(
        error.response?.data?.detail || "Login failed. Please try again."
      );
      return false;
    }
  };

  // Register function
  const register = async (email, password) => {
    try {
      const response = await axios.post(`${API_URL}/auth/register`, {
        email,
        password,
      });

      const { access_token, user } = response.data;

      // Save to state and localStorage
      setToken(access_token);
      setCurrentUser(user);
      localStorage.setItem("token", access_token);
      localStorage.setItem("user", JSON.stringify(user));

      toast.success("Registration successful!");
      return true;
    } catch (error) {
      console.error("Registration error:", error);
      toast.error(
        error.response?.data?.detail || "Registration failed. Please try again."
      );
      return false;
    }
  };

  // Logout function
  const logout = () => {
    setToken(null);
    setCurrentUser(null);
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    
    // Clear all integration data when logging out to prevent data leakage
    clearIntegrationData();
    console.log("Logged out and cleared all integration data");
    
    toast.info("You have been logged out.");
  };

  // Context value
  const value = {
    currentUser,
    token,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!token,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}; 