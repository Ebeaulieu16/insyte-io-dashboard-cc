import React, { createContext, useState, useEffect, useContext, useRef } from 'react';
import api from 'utils/api';

// Create context
const IntegrationContext = createContext({
  integrations: [],
  loading: true,
  isAnyIntegrationConnected: false,
  isIntegrationConnected: () => false,
  refreshIntegrations: () => {},
  addLocalIntegration: () => {},
  removeLocalIntegration: () => {},
  debugIntegrationState: () => {},
});

// Persistence key for local storage
const INTEGRATIONS_STORAGE_KEY = 'insyte_integrations';
const INTEGRATIONS_TIMESTAMP_KEY = 'insyte_integrations_timestamp';

// Helper to get user-specific storage key
const getUserSpecificKey = (baseKey) => {
  const token = localStorage.getItem('token');
  return token ? `${baseKey}_${token.substring(0, 10)}` : baseKey;
};

// Helper to clear integration data
const clearIntegrationData = () => {
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

// Context provider component
export const IntegrationProvider = ({ children }) => {
  // Initialize state from local storage if available
  const getInitialIntegrations = () => {
    try {
      // Try to get user-specific integrations first
      const userSpecificKey = getUserSpecificKey(INTEGRATIONS_STORAGE_KEY);
      const storedIntegrations = localStorage.getItem(userSpecificKey);
      
      if (storedIntegrations) {
        console.log('Loaded user-specific integrations from local storage');
        return JSON.parse(storedIntegrations);
      }
      
      // Fall back to generic storage only if no user-specific data found
      // and we're not logged in (to avoid mixing data)
      if (!localStorage.getItem('token')) {
        const genericIntegrations = localStorage.getItem(INTEGRATIONS_STORAGE_KEY);
        if (genericIntegrations) {
          console.log('Loaded generic integrations from local storage (no user logged in)');
          return JSON.parse(genericIntegrations);
        }
      }
    } catch (error) {
      console.error('Failed to load integrations from local storage:', error);
    }
    return [];
  };

  const [integrations, setIntegrations] = useState(getInitialIntegrations());
  const [loading, setLoading] = useState(true);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [lastRefreshTime, setLastRefreshTime] = useState(() => {
    // Initialize from local storage if available
    const stored = localStorage.getItem(INTEGRATIONS_TIMESTAMP_KEY);
    return stored ? parseInt(stored, 10) : 0;
  });
  const fetchInProgressRef = useRef(false); // Track if a fetch is already in progress
  const localIntegrationsRef = useRef({}); // Keep local cache of connected integrations

  // Initialize localIntegrationsRef from integrations if available
  useEffect(() => {
    // Populate localIntegrationsRef with any integrations that are already connected
    if (integrations.length > 0) {
      integrations.forEach(integration => {
        if (integration.status === 'connected' || integration.is_connected === true) {
          localIntegrationsRef.current[integration.platform] = {
            platform: integration.platform,
            status: 'connected',
            account_name: integration.account_name,
            timestamp: Date.now()
          };
        }
      });
    }
  }, []);

  // Calculate if any integration is connected
  const isAnyIntegrationConnected = integrations.some(
    integration => integration.status === 'connected' || integration.is_connected === true
  );

  // Check if a specific integration is connected
  const isIntegrationConnected = (platform) => {
    // First check in our regular integrations array
    const integration = integrations.find(i => i.platform === platform);
    if (integration && (integration.status === 'connected' || integration.is_connected === true)) {
      return true;
    }
    
    // If not found in regular array, check our local cache as a fallback
    return !!localIntegrationsRef.current[platform];
  };

  // Persist integrations to local storage whenever they change
  useEffect(() => {
    try {
      // Don't save empty integrations
      if (integrations.length > 0) {
        const userSpecificKey = getUserSpecificKey(INTEGRATIONS_STORAGE_KEY);
        
        // If user is logged in, only save to user-specific storage
        // This prevents data leakage between users
        if (localStorage.getItem('token')) {
          localStorage.setItem(userSpecificKey, JSON.stringify(integrations));
          console.log('Saved integrations to user-specific local storage');
        } else {
          // If no user is logged in, save to general storage
          localStorage.setItem(INTEGRATIONS_STORAGE_KEY, JSON.stringify(integrations));
          console.log('Saved integrations to generic local storage (no user logged in)');
        }
      }
    } catch (error) {
      console.error('Failed to save integrations to local storage:', error);
    }
  }, [integrations]);
  
  // Listen for authentication changes
  useEffect(() => {
    const checkAuthAndRefresh = () => {
      const previousToken = localStorage.getItem('previous_token');
      const currentToken = localStorage.getItem('token');
      
      // If token changed (user logged in or out)
      if (previousToken !== currentToken) {
        console.log('Authentication state changed - refreshing integrations');
        localStorage.setItem('previous_token', currentToken || '');
        
        // If user logged in, try to load their specific integrations
        if (currentToken && !previousToken) {
          const userSpecificIntegrations = localStorage.getItem(`${INTEGRATIONS_STORAGE_KEY}_${currentToken.substring(0, 10)}`);
          if (userSpecificIntegrations) {
            try {
              const parsedIntegrations = JSON.parse(userSpecificIntegrations);
              if (Array.isArray(parsedIntegrations) && parsedIntegrations.length > 0) {
                console.log('Loading user-specific integrations after login');
                setIntegrations(parsedIntegrations);
              }
            } catch (e) {
              console.error('Error loading user-specific integrations:', e);
            }
          }
        }
        
        // Always trigger a refresh after auth state change
        setTimeout(() => {
          refreshIntegrations();
        }, 500);
      }
    };
    
    // Store initial token
    if (!localStorage.getItem('previous_token')) {
      localStorage.setItem('previous_token', localStorage.getItem('token') || '');
    }
    
    // Check immediately
    checkAuthAndRefresh();
    
    // Set up a storage change listener
    const handleStorageChange = (e) => {
      if (e.key === 'token') {
        checkAuthAndRefresh();
      }
    };
    
    window.addEventListener('storage', handleStorageChange);
    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  }, []);

  // Persist lastRefreshTime to local storage whenever it changes
  useEffect(() => {
    try {
      localStorage.setItem(INTEGRATIONS_TIMESTAMP_KEY, lastRefreshTime.toString());
    } catch (error) {
      console.error('Failed to save refresh timestamp to local storage:', error);
    }
  }, [lastRefreshTime]);

  // Function to add a locally connected integration (used when the API call succeeds but before refresh)
  const addLocalIntegration = (platform, accountName) => {
    console.log(`Adding local integration cache for ${platform}: ${accountName}`);
    
    // Store in our in-memory reference
    localIntegrationsRef.current[platform] = {
      platform,
      status: 'connected', 
      account_name: accountName,
      timestamp: Date.now()
    };
    
    // We'll also update our integrations array directly for immediate UI feedback
    setIntegrations(prevIntegrations => {
      // Check if we already have this integration in our array
      const existingIndex = prevIntegrations.findIndex(i => i.platform === platform);
      
      let updatedIntegrations;
      if (existingIndex >= 0) {
        // Update existing integration
        updatedIntegrations = [...prevIntegrations];
        updatedIntegrations[existingIndex] = {
          ...updatedIntegrations[existingIndex],
          status: 'connected',
          account_name: accountName,
          is_connected: true
        };
      } else {
        // Add new integration
        updatedIntegrations = [
          ...prevIntegrations,
          {
            platform,
            status: 'connected',
            account_name: accountName,
            is_connected: true
          }
        ];
      }
      
      // Store in user-specific storage if user is authenticated
      const userToken = localStorage.getItem('token');
      if (userToken) {
        try {
          console.log('User is authenticated - storing updated integrations with user context');
          localStorage.setItem(`${INTEGRATIONS_STORAGE_KEY}_${userToken.substring(0, 10)}`, 
            JSON.stringify(updatedIntegrations));
        } catch (e) {
          console.error('Failed to save user-specific integrations to local storage:', e);
        }
      }
      
      return updatedIntegrations;
    });
  };

  // Function to remove a locally connected integration (used when disconnecting)
  const removeLocalIntegration = (platform) => {
    console.log(`Removing local integration cache for ${platform}`);
    // Delete from local cache
    if (localIntegrationsRef.current[platform]) {
      delete localIntegrationsRef.current[platform];
    }
    
    // Also update our integrations array to show disconnected
    setIntegrations(prevIntegrations => {
      const updatedIntegrations = prevIntegrations.map(integration => {
        if (integration.platform === platform) {
          return {
            ...integration,
            status: 'disconnected',
            is_connected: false
          };
        }
        return integration;
      });
      
      // Update in user-specific storage if user is authenticated
      const userToken = localStorage.getItem('token');
      if (userToken) {
        try {
          console.log('User is authenticated - updating user-specific integrations after disconnection');
          localStorage.setItem(`${INTEGRATIONS_STORAGE_KEY}_${userToken.substring(0, 10)}`, 
            JSON.stringify(updatedIntegrations));
        } catch (e) {
          console.error('Failed to save user-specific integrations to local storage:', e);
        }
      }
      
      return updatedIntegrations;
    });
  };

  // Function to refresh integrations data with enhanced debouncing
  const refreshIntegrations = () => {
    const now = Date.now();
    // Only allow refresh if more than 2 seconds have passed since last refresh
    // AND no fetch is currently in progress
    if (now - lastRefreshTime > 2000 && !fetchInProgressRef.current) {
      console.log('Refreshing integrations...');
      setLastRefreshTime(now);
      setRefreshTrigger(prev => prev + 1);
    } else {
      console.log('Refresh requested too soon or fetch in progress, ignoring');
    }
  };

  // Debug function to help troubleshoot integration state
  const debugIntegrationState = () => {
    console.log("===== INTEGRATION DEBUG INFO =====");
    console.log("Current integrations state:", integrations);
    console.log("isAnyIntegrationConnected:", isAnyIntegrationConnected);
    console.log("localIntegrationsRef:", localIntegrationsRef.current);
    
    // Log individual integration statuses
    if (integrations.length > 0) {
      integrations.forEach(integration => {
        console.log(`${integration.platform}: connected=${integration.status === 'connected' || integration.is_connected === true}`);
      });
    } else {
      console.log("No integrations in state");
    }
    
    // Log what's in local storage
    console.log("localStorage.token:", localStorage.getItem('token'));
    console.log("localStorage.integrations:", localStorage.getItem(INTEGRATIONS_STORAGE_KEY));
    console.log("backendAvailable:", localStorage.getItem('backendAvailable'));
    
    // Force a refresh
    console.log("Forcing refresh of integration state...");
    setRefreshTrigger(prev => prev + 1);
    
    console.log("================================");
    return "Debug info logged to console";
  };

  // Fetch integrations status on mount and when refresh is triggered
  useEffect(() => {
    // Define state variables to track loading state changes
    let isMounted = true;
    let loadingTimeout = null;
    let loadingOffTimeout = null;
    
    const fetchIntegrationStatus = async () => {
      if (fetchInProgressRef.current) {
        console.log('A fetch is already in progress, skipping');
        return;
      }
      
      fetchInProgressRef.current = true;
      
      // Don't set loading to true immediately to prevent flashing
      // Only set loading after a short delay if the request is still ongoing
      loadingTimeout = setTimeout(() => {
        if (isMounted) {
          setLoading(true);
        }
      }, 500); // Increased delay to 500ms to prevent quick flashes
      
      try {
        // Log user information if available (to help with debugging cross-device issues)
        const userToken = localStorage.getItem('token');
        console.log(`Fetching integration status. Auth token present: ${!!userToken}`);
        
        const response = await api.get('/api/integrations/status', {
          // Add cache busting parameter to avoid getting cached results
          params: { _t: Date.now() },
          // Increase timeout for this specific call
          timeout: 15000
        });
        
        console.log('Integration status response:', response.data);
        
        if (isMounted) {
          if (response.data && Array.isArray(response.data.integrations) && response.data.integrations.length > 0) {
            // First, check if we have a user token 
            if (userToken) {
              console.log('User is authenticated - storing integrations with user context');
              // Store these integrations with a user-specific key
              try {
                localStorage.setItem(`${INTEGRATIONS_STORAGE_KEY}_${userToken.substring(0, 10)}`, 
                  JSON.stringify(response.data.integrations));
              } catch (e) {
                console.error('Failed to save integrations to user-specific local storage:', e);
              }
            }
          }
        }
      } catch (error) {
        console.error('Error fetching integration status:', error);
      } finally {
        if (isMounted) {
          fetchInProgressRef.current = false;
          if (loadingTimeout) {
            clearTimeout(loadingTimeout);
          }
          if (loadingOffTimeout) {
            clearTimeout(loadingOffTimeout);
          }
          setLoading(false);
        }
      }
    };
    
    fetchIntegrationStatus();
  }, []);

  return (
    <IntegrationContext.Provider
      value={{
        integrations,
        loading,
        isAnyIntegrationConnected,
        isIntegrationConnected,
        refreshIntegrations,
        addLocalIntegration,
        removeLocalIntegration,
        debugIntegrationState,
      }}
    >
      {children}
    </IntegrationContext.Provider>
  );
};

export const useIntegration = () => {
  const context = useContext(IntegrationContext);
  if (context === undefined) {
    throw new Error('useIntegration must be used within an IntegrationProvider');
  }
  return context;
};