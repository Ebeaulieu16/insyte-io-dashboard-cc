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

// Context provider component
export const IntegrationProvider = ({ children }) => {
  // Initialize state from local storage if available
  const getInitialIntegrations = () => {
    try {
      const storedIntegrations = localStorage.getItem(INTEGRATIONS_STORAGE_KEY);
      if (storedIntegrations) {
        console.log('Loaded integrations from local storage');
        return JSON.parse(storedIntegrations);
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
        // Save to general storage
        localStorage.setItem(INTEGRATIONS_STORAGE_KEY, JSON.stringify(integrations));
        console.log('Saved integrations to local storage');
        
        // Also save to user-specific storage if a user is logged in
        const userToken = localStorage.getItem('token');
        if (userToken) {
          localStorage.setItem(`${INTEGRATIONS_STORAGE_KEY}_${userToken.substring(0, 10)}`, 
            JSON.stringify(integrations));
          console.log('Saved integrations to user-specific local storage');
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
                console.error('Failed to save user-specific integrations to local storage:', e);
              }
            }
            
            // Merge with our local integration cache
            const mergedIntegrations = response.data.integrations.map(integration => {
              const localIntegration = localIntegrationsRef.current[integration.platform];
              
              // If we have a local cache for this platform and it's newer than what the API returned
              // and the API is showing it as disconnected but our local cache says it's connected
              if (localIntegration && 
                  integration.status !== 'connected' && 
                  localIntegration.status === 'connected' &&
                  // Check if the local integration was updated in the last 5 minutes
                  // This prevents using very old local integrations
                  localIntegration.timestamp && 
                  (Date.now() - localIntegration.timestamp) < 5 * 60 * 1000) {
                console.log(`Using cached integration for ${integration.platform} instead of API response (local is newer)`);
                return {
                  ...integration,
                  status: 'connected',
                  account_name: localIntegration.account_name || integration.account_name,
                  is_connected: true
                };
              }
              
              // Otherwise, trust the server response
              console.log(`Using server data for ${integration.platform} integration`);
              return integration;
            });
            
            setIntegrations(mergedIntegrations);
          } else {
            // Check if we have any local integrations before falling back to default
            const localIntegrationsArray = Object.values(localIntegrationsRef.current);
            
            if (localIntegrationsArray.length > 0) {
              console.log('Using cached local integrations instead of API response');
              setIntegrations(localIntegrationsArray);
            } else {
              // Try user-specific integrations first (if user is logged in)
              const userToken = localStorage.getItem('token');
              if (userToken) {
                const userSpecificIntegrations = localStorage.getItem(`${INTEGRATIONS_STORAGE_KEY}_${userToken.substring(0, 10)}`);
                if (userSpecificIntegrations) {
                  try {
                    const parsedIntegrations = JSON.parse(userSpecificIntegrations);
                    if (Array.isArray(parsedIntegrations) && parsedIntegrations.length > 0) {
                      console.log('Using user-specific integrations from local storage');
                      setIntegrations(parsedIntegrations);
                      return;
                    }
                  } catch (e) {
                    console.error('Error parsing user-specific stored integrations:', e);
                  }
                }
              }
              
              // Then check generic local storage
              const storedIntegrations = localStorage.getItem(INTEGRATIONS_STORAGE_KEY);
              if (storedIntegrations) {
                try {
                  const parsedIntegrations = JSON.parse(storedIntegrations);
                  if (Array.isArray(parsedIntegrations) && parsedIntegrations.length > 0) {
                    console.log('Using integrations from local storage');
                    setIntegrations(parsedIntegrations);
                    return;
                  }
                } catch (e) {
                  console.error('Error parsing stored integrations:', e);
                }
              }
              
              // Fallback for when the API returns a successful response but with no integrations
              console.warn('API returned success but no integrations data, using defaults');
              setIntegrations([
                { platform: "youtube", status: "disconnected", account_name: null, last_sync: null },
                { platform: "stripe", status: "disconnected", account_name: null, last_sync: null },
                { platform: "calendly", status: "disconnected", account_name: null, last_sync: null },
                { platform: "calcom", status: "disconnected", account_name: null, last_sync: null }
              ]);
            }
          }
        }
      } catch (error) {
        console.error('Failed to fetch integration status:', error);
        
        // Check if we have any local integrations before setting defaults
        if (isMounted) {
          // First try user-specific integrations (if user is logged in)
          const userToken = localStorage.getItem('token');
          if (userToken) {
            const userSpecificIntegrations = localStorage.getItem(`${INTEGRATIONS_STORAGE_KEY}_${userToken.substring(0, 10)}`);
            if (userSpecificIntegrations) {
              try {
                const parsedIntegrations = JSON.parse(userSpecificIntegrations);
                if (Array.isArray(parsedIntegrations) && parsedIntegrations.length > 0) {
                  console.log('API error, using user-specific integrations from local storage');
                  setIntegrations(parsedIntegrations);
                  return;
                }
              } catch (e) {
                console.error('Error parsing user-specific stored integrations:', e);
              }
            }
          }
          
          // Then try to use our in-memory local integrations
          const localIntegrationsArray = Object.values(localIntegrationsRef.current);
          
          if (localIntegrationsArray.length > 0) {
            console.log('API error, using cached local integrations from memory');
            setIntegrations(localIntegrationsArray);
          } else {
            // Then try to use local storage
            const storedIntegrations = localStorage.getItem(INTEGRATIONS_STORAGE_KEY);
            if (storedIntegrations) {
              try {
                const parsedIntegrations = JSON.parse(storedIntegrations);
                if (Array.isArray(parsedIntegrations) && parsedIntegrations.length > 0) {
                  console.log('API error, using integrations from local storage');
                  setIntegrations(parsedIntegrations);
                  return;
                }
              } catch (e) {
                console.error('Error parsing stored integrations:', e);
              }
            }
            
            // Finally fall back to defaults
            console.log('API error, no cached integrations, using defaults');
            setIntegrations([
              { platform: "youtube", status: "disconnected", account_name: null, last_sync: null },
              { platform: "stripe", status: "disconnected", account_name: null, last_sync: null },
              { platform: "calendly", status: "disconnected", account_name: null, last_sync: null },
              { platform: "calcom", status: "disconnected", account_name: null, last_sync: null }
            ]);
          }
        }
      } finally {
        // Clear the loading timeout if it hasn't triggered yet
        clearTimeout(loadingTimeout);
        
        if (isMounted) {
          // Delay turning off loading state to prevent UI flashing
          // This ensures the loading state doesn't toggle too quickly
          loadingOffTimeout = setTimeout(() => {
            setLoading(false);
            fetchInProgressRef.current = false;
          }, 300);
        } else {
          fetchInProgressRef.current = false;
        }
      }
    };

    // Set a timeout to ensure we don't get stuck in loading state
    const stuckTimeout = setTimeout(() => {
      if (isMounted) {
        setLoading(false);
        fetchInProgressRef.current = false;
      }
    }, 5000); // 5 seconds max loading time
    
    fetchIntegrationStatus();
    
    // Cleanup function to prevent state updates after unmount
    return () => {
      isMounted = false;
      clearTimeout(loadingTimeout);
      clearTimeout(loadingOffTimeout);
      clearTimeout(stuckTimeout);
    };
  }, [refreshTrigger]);

  // Provide context value
  const contextValue = {
    integrations,
    loading,
    isAnyIntegrationConnected,
    isIntegrationConnected,
    refreshIntegrations,
    addLocalIntegration,
    removeLocalIntegration,
    debugIntegrationState,
  };

  return (
    <IntegrationContext.Provider value={contextValue}>
      {children}
    </IntegrationContext.Provider>
  );
};

// Custom hook to use the integration context
export const useIntegration = () => useContext(IntegrationContext);

export default IntegrationContext; 