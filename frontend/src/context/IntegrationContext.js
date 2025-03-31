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
});

// Context provider component
export const IntegrationProvider = ({ children }) => {
  const [integrations, setIntegrations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [lastRefreshTime, setLastRefreshTime] = useState(0);
  const fetchInProgressRef = useRef(false); // Track if a fetch is already in progress
  const localIntegrationsRef = useRef({}); // Keep local cache of connected integrations

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

  // Function to add a locally connected integration (used when the API call succeeds but before refresh)
  const addLocalIntegration = (platform, accountName) => {
    console.log(`Adding local integration cache for ${platform}: ${accountName}`);
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
      
      if (existingIndex >= 0) {
        // Update existing integration
        const updatedIntegrations = [...prevIntegrations];
        updatedIntegrations[existingIndex] = {
          ...updatedIntegrations[existingIndex],
          status: 'connected',
          account_name: accountName,
          is_connected: true
        };
        return updatedIntegrations;
      } else {
        // Add new integration
        return [
          ...prevIntegrations,
          {
            platform,
            status: 'connected',
            account_name: accountName,
            is_connected: true
          }
        ];
      }
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
      return prevIntegrations.map(integration => {
        if (integration.platform === platform) {
          return {
            ...integration,
            status: 'disconnected',
            is_connected: false
          };
        }
        return integration;
      });
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
        const response = await api.get('/api/integrations/status');
        console.log('Integration status response:', response.data);
        
        if (isMounted) {
          if (response.data && Array.isArray(response.data.integrations) && response.data.integrations.length > 0) {
            // Merge with our local integration cache
            const mergedIntegrations = response.data.integrations.map(integration => {
              const localIntegration = localIntegrationsRef.current[integration.platform];
              
              // If we have a local cache for this platform and it's newer than what the API returned
              // and the API is showing it as disconnected but our local cache says it's connected
              if (localIntegration && 
                  integration.status !== 'connected' && 
                  localIntegration.status === 'connected') {
                console.log(`Using cached integration for ${integration.platform} instead of API response`);
                return {
                  ...integration,
                  status: 'connected',
                  account_name: localIntegration.account_name || integration.account_name,
                  is_connected: true
                };
              }
              
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
          const localIntegrationsArray = Object.values(localIntegrationsRef.current);
          
          if (localIntegrationsArray.length > 0) {
            console.log('API error, using cached local integrations');
            setIntegrations(localIntegrationsArray);
          } else {
            // Set default empty integrations on error
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