import React, { createContext, useState, useEffect, useContext } from 'react';
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

  // Calculate if any integration is connected
  const isAnyIntegrationConnected = integrations.some(
    integration => integration.status === 'connected' || integration.is_connected === true
  );

  // Check if a specific integration is connected
  const isIntegrationConnected = (platform) => {
    const integration = integrations.find(i => i.platform === platform);
    return integration && (integration.status === 'connected' || integration.is_connected === true);
  };

  // Function to refresh integrations data
  const refreshIntegrations = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  // Fetch integrations status on mount and when refresh is triggered
  useEffect(() => {
    const fetchIntegrationStatus = async () => {
      setLoading(true);
      try {
        const response = await api.get('/api/integrations/status');
        console.log('Integration status response:', response.data);
        
        if (response.data && response.data.integrations) {
          setIntegrations(response.data.integrations);
        }
      } catch (error) {
        console.error('Failed to fetch integration status:', error);
        setIntegrations([]);
      } finally {
        setLoading(false);
      }
    };

    fetchIntegrationStatus();
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