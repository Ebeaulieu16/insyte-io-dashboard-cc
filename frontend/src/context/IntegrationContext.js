import React, { createContext, useState, useEffect, useContext, useRef } from 'react';
import api from 'utils/api';

// Create context
const IntegrationContext = createContext({
  integrations: [],
  loading: true,
  isAnyIntegrationConnected: false,
  isIntegrationConnected: () => false,
  refreshIntegrations: () => {},
});

// Context provider component
export const IntegrationProvider = ({ children }) => {
  const [integrations, setIntegrations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [lastRefreshTime, setLastRefreshTime] = useState(0);
  const fetchInProgressRef = useRef(false); // Track if a fetch is already in progress

  // Calculate if any integration is connected
  const isAnyIntegrationConnected = integrations.some(
    integration => integration.status === 'connected' || integration.is_connected === true
  );

  // Check if a specific integration is connected
  const isIntegrationConnected = (platform) => {
    const integration = integrations.find(i => i.platform === platform);
    return integration && (integration.status === 'connected' || integration.is_connected === true);
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
          if (response.data && response.data.integrations) {
            setIntegrations(response.data.integrations);
          } else {
            // Fallback for when the API returns a successful response but with no integrations
            console.warn('API returned success but no integrations data');
            setIntegrations([
              { platform: "youtube", status: "disconnected", account_name: null, last_sync: null },
              { platform: "stripe", status: "disconnected", account_name: null, last_sync: null },
              { platform: "calendly", status: "disconnected", account_name: null, last_sync: null },
              { platform: "calcom", status: "disconnected", account_name: null, last_sync: null }
            ]);
          }
        }
      } catch (error) {
        console.error('Failed to fetch integration status:', error);
        // Set default empty integrations on error
        if (isMounted) {
          setIntegrations([
            { platform: "youtube", status: "disconnected", account_name: null, last_sync: null },
            { platform: "stripe", status: "disconnected", account_name: null, last_sync: null },
            { platform: "calendly", status: "disconnected", account_name: null, last_sync: null },
            { platform: "calcom", status: "disconnected", account_name: null, last_sync: null }
          ]);
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