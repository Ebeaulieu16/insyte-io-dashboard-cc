/*!

=========================================================
* Vision UI Free React - Integrations Page
=========================================================

*/

import { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";

// @mui material components
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import Icon from "@mui/material/Icon";
import Divider from "@mui/material/Divider";
import Tooltip from "@mui/material/Tooltip";
import Snackbar from "@mui/material/Snackbar";
import Alert from "@mui/material/Alert";
import TextField from "@mui/material/TextField";

// Vision UI Dashboard React components
import VuiBox from "components/VuiBox";
import VuiTypography from "components/VuiTypography";
import VuiButton from "components/VuiButton";

// Vision UI Dashboard React example components
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";

// Vision UI Dashboard React base styles
import typography from "assets/theme/base/typography";
import colors from "assets/theme/base/colors";

// React icons
import { FaCreditCard, FaYoutube, FaCalendarAlt, FaSync, FaLink, FaCalendarCheck } from "react-icons/fa";
import { IoCheckmarkCircle, IoCloseCircle, IoInformationCircle } from "react-icons/io5";

// React Router
import { Link } from "react-router-dom";

// API utility
import api, { isBackendAvailable } from "utils/api";

// Integration context
import { useIntegration } from "../../context/IntegrationContext";

function Integrations() {
  const { gradients } = colors;
  const { cardContent } = gradients;
  const location = useLocation();
  
  // Get integration status from context
  const { integrations: contextIntegrations, loading: contextLoading, refreshIntegrations } = useIntegration();

  // Local state for UI
  const [integrations, setIntegrations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [alert, setAlert] = useState({ show: false, message: "", severity: "info" });
  const [isDemo, setIsDemo] = useState(false);
  const [calcomApiKey, setCalcomApiKey] = useState("");
  const [youtubeApiKey, setYoutubeApiKey] = useState("");
  const [youtubeChannelId, setYoutubeChannelId] = useState("");
  const [stripeApiKey, setStripeApiKey] = useState("");
  const [calendlyApiKey, setCalendlyApiKey] = useState("");

  // When the integration context updates, update our local state
  useEffect(() => {
    if (contextIntegrations.length > 0) {
      // Map API response to integrations with UI properties
      const formattedIntegrations = contextIntegrations.map(integration => ({
        id: integration.platform,
        name: getPlatformName(integration.platform),
        description: getPlatformDescription(integration.platform),
        connected: integration.status === "connected" || integration.is_connected === true,
        connectedSince: integration.last_sync,
        accountName: integration.account_name,
        icon: getPlatformIcon(integration.platform),
        status: (integration.status === "connected" || integration.is_connected === true) ? "Active" : "Not Connected",
        color: (integration.status === "connected" || integration.is_connected === true) ? "success" : "error",
        scopes: getPlatformScopes(integration.platform)
      }));
      
      setIntegrations(formattedIntegrations);
      setLoading(contextLoading);
    }
  }, [contextIntegrations, contextLoading]);

  // Display URL parameters as alerts (for OAuth redirects)
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    
    if (params.has("success") && params.get("platform")) {
      setAlert({
        show: true,
        message: `Successfully connected ${params.get("platform")}!`,
        severity: "success"
      });
      
      // Refresh the integrations list when we get a success parameter
      refreshIntegrations();
    } else if (params.has("error") && params.get("platform")) {
      setAlert({
        show: true,
        message: `Error connecting ${params.get("platform")}: ${params.get("error")}`,
        severity: "error"
      });
    }
    
    // Clear URL parameters after displaying alerts
    if (params.toString()) {
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, [location]);

  // Helper functions for platform metadata
  const getPlatformName = (platform) => {
    const names = {
      youtube: "YouTube",
      stripe: "Stripe",
      calendly: "Calendly",
      calcom: "Cal.com"
    };
    return names[platform] || platform;
  };

  const getPlatformDescription = (platform) => {
    const descriptions = {
      youtube: "Connect your channel to track video performance metrics",
      stripe: "Connect your payment account to track revenue and transactions",
      calendly: "Schedule and track calls and appointments automatically",
      calcom: "Open-source alternative for scheduling meetings"
    };
    return descriptions[platform] || "";
  };

  const getPlatformIcon = (platform) => {
    switch (platform) {
      case "youtube":
        return <FaYoutube size="30px" color="white" />;
      case "stripe":
        return <FaCreditCard size="30px" color="white" />;
      case "calendly":
        return <FaCalendarAlt size="30px" color="white" />;
      case "calcom":
        return <FaCalendarCheck size="30px" color="white" />;
      default:
        return <Icon>link</Icon>;
    }
  };

  const getPlatformScopes = (platform) => {
    const scopes = {
      youtube: ["Channel Statistics", "Video Metrics", "Engagement Data"],
      stripe: ["Payment Records", "Customer Information", "Transaction History"],
      calendly: ["Bookings", "Appointment Status", "Calendar Events"],
      calcom: ["Bookings", "Scheduling Data", "User Profile"]
    };
    return scopes[platform] || [];
  };

  // Handle connect/disconnect actions
  const handleConnect = (platform) => {
    // All platforms now use API key forms, so we don't need to redirect
    console.log(`Connect button clicked for ${platform} - using API key form instead of OAuth`);
    
    // Show a helpful message to the user
    setAlert({
      show: true,
      message: `Please use the API key form to connect ${getPlatformName(platform)}`,
      severity: "info"
    });
    
    return;
    
    // Redirect code is kept but commented out in case OAuth is re-enabled in the future
    // window.location.href = `${process.env.REACT_APP_API_URL}/auth/${platform}`;
  };

  const handleDisconnect = async (platform) => {
    try {
      await api.delete(`/api/integrations/${platform}`);
      
      // Update the integration status in the UI
      setIntegrations(prev => 
        prev.map(integration => 
          integration.id === platform
            ? { ...integration, connected: false, status: "Not Connected", color: "error" }
            : integration
        )
      );
      
      setAlert({
        show: true,
        message: `Successfully disconnected ${getPlatformName(platform)}`,
        severity: "success"
      });
      
      // Refresh global integration state
      refreshIntegrations();
    } catch (error) {
      console.error(`Failed to disconnect ${platform}:`, error);
      setAlert({
        show: true,
        message: `Failed to disconnect ${getPlatformName(platform)}`,
        severity: "error"
      });
    }
  };

  // Handle alert close
  const handleCloseAlert = () => {
    setAlert(prev => ({ ...prev, show: false }));
  };

  const handleYoutubeApiKeySubmit = async (e) => {
    e.preventDefault();
    
    if (!youtubeApiKey.trim()) {
      setAlert({
        show: true,
        message: "Please enter your YouTube API key",
        severity: "error"
      });
      return;
    }

    if (!youtubeChannelId.trim()) {
      setAlert({
        show: true,
        message: "Please enter your YouTube channel ID",
        severity: "error"
      });
      return;
    }

    try {
      setLoading(true);
      const payload = {
        api_key: youtubeApiKey,
        channel_id: youtubeChannelId
      };
      
      const response = await api.post("/api/integrations/youtube/api-key", payload);
      console.log("YouTube API key submitted:", response.data);
      
      if (response.data && response.data.status === "success") {
        // Update the UI to reflect the new integration
        const updatedIntegrations = integrations.map(integration => {
          if (integration.id === "youtube") {
            return {
              ...integration,
              connected: true,
              accountName: response.data.account_name,
              status: "Active",
              color: "success"
            };
          }
          return integration;
        });
        
        setIntegrations(updatedIntegrations);
        setYoutubeApiKey("");
        setYoutubeChannelId("");
        setAlert({
          show: true,
          message: `Successfully connected YouTube channel: ${response.data.account_name}`,
          severity: "success"
        });
        
        // Refresh global integration state
        refreshIntegrations();
      }
    } catch (error) {
      console.error("Error submitting YouTube API key:", error);
      setAlert({
        show: true,
        message: `Error connecting YouTube: ${error.response?.data?.detail || error.message}`,
        severity: "error"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleStripeApiKeySubmit = async (e) => {
    e.preventDefault();
    
    try {
      if (!stripeApiKey || stripeApiKey.trim() === "") {
        setAlert({
          show: true,
          message: "Please enter a valid Stripe secret key",
          severity: "warning"
        });
        return;
      }
      
      // Submit API key to backend
      const response = await api.post("/api/integrations/stripe/api-key", {
        api_key: stripeApiKey
      });
      
      // Update UI with new integration status
      setIntegrations(prev => 
        prev.map(integration => 
          integration.id === "stripe"
            ? { 
                ...integration, 
                connected: true, 
                status: "Active", 
                color: "success",
                accountName: response.data.account_name || "Stripe Account"
              }
            : integration
        )
      );
      
      setAlert({
        show: true,
        message: "Successfully connected Stripe",
        severity: "success"
      });
      
      // Clear input
      setStripeApiKey("");
      
      // Refresh global integration state
      refreshIntegrations();
    } catch (error) {
      console.error("Failed to connect Stripe:", error);
      setAlert({
        show: true,
        message: error.response?.data?.detail || "Failed to connect Stripe. Please check your API key.",
        severity: "error"
      });
    }
  };

  const handleCalendlyApiKeySubmit = async (e) => {
    e.preventDefault();
    
    try {
      if (!calendlyApiKey || calendlyApiKey.trim() === "") {
        setAlert({
          show: true,
          message: "Please enter a valid Calendly API key",
          severity: "warning"
        });
        return;
      }
      
      // Submit API key to backend
      const response = await api.post("/api/integrations/calendly/api-key", {
        api_key: calendlyApiKey
      });
      
      // Update UI with new integration status
      setIntegrations(prev => 
        prev.map(integration => 
          integration.id === "calendly"
            ? { 
                ...integration, 
                connected: true, 
                status: "Active", 
                color: "success",
                accountName: response.data.account_name || "Calendly Account"
              }
            : integration
        )
      );
      
      setAlert({
        show: true,
        message: "Successfully connected Calendly",
        severity: "success"
      });
      
      // Clear input
      setCalendlyApiKey("");
      
      // Refresh global integration state
      refreshIntegrations();
    } catch (error) {
      console.error("Failed to connect Calendly:", error);
      setAlert({
        show: true,
        message: error.response?.data?.detail || "Failed to connect Calendly. Please check your API key.",
        severity: "error"
      });
    }
  };

  const handleCalcomApiKeySubmit = async (e) => {
    e.preventDefault();
    
    try {
      if (!calcomApiKey || calcomApiKey.trim() === "") {
        setAlert({
          show: true,
          message: "Please enter a valid Cal.com API key",
          severity: "warning"
        });
        return;
      }
      
      // Submit API key to backend
      const response = await api.post("/api/integrations/calcom/api-key", {
        api_key: calcomApiKey
      });
      
      // Update UI with new integration status
      setIntegrations(prev => 
        prev.map(integration => 
          integration.id === "calcom"
            ? { 
                ...integration, 
                connected: true, 
                status: "Active", 
                color: "success",
                accountName: response.data.account_name || "Cal.com Account"
              }
            : integration
        )
      );
      
      setAlert({
        show: true,
        message: "Successfully connected Cal.com",
        severity: "success"
      });
      
      // Clear input
      setCalcomApiKey("");
      
      // Refresh global integration state
      refreshIntegrations();
    } catch (error) {
      console.error("Failed to connect Cal.com:", error);
      setAlert({
        show: true,
        message: error.response?.data?.detail || "Failed to connect Cal.com. Please check your API key.",
        severity: "error"
      });
    }
  };

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <VuiBox py={3}>
        <VuiBox mb={3}>
          <VuiTypography variant="h4" color="white" fontWeight="bold">
            Platform Integrations
          </VuiTypography>
          <VuiTypography variant="button" color="text" fontWeight="regular">
            Connect your accounts to enhance tracking and automation
          </VuiTypography>
          
          {isDemo && (
            <VuiBox mt={2} p={2} borderRadius="lg" bgColor="info">
              <VuiTypography variant="button" color="white" fontWeight="medium">
                Demo Mode - Backend server is not running. Showing sample integration data.
              </VuiTypography>
            </VuiBox>
          )}
        </VuiBox>

        {/* Debug Info */}
        {process.env.NODE_ENV === 'development' && (
          <Card sx={{ mb: 3 }}>
            <VuiBox p={3}>
              <VuiTypography variant="button" color="white" fontWeight="bold">
                Debug Info: 
              </VuiTypography>
              <VuiTypography variant="caption" color="text" fontWeight="regular" component="pre">
                loading: {loading.toString()}<br/>
                integrations count: {integrations.length}<br/>
                {JSON.stringify(integrations, null, 2)}
              </VuiTypography>
            </VuiBox>
          </Card>
        )}

        {/* Loading State */}
        {loading ? (
          <Card>
            <VuiBox p={3} display="flex" justifyContent="center" alignItems="center" height="200px">
              <VuiTypography variant="button" color="text" fontWeight="regular">
                Loading integrations...
              </VuiTypography>
            </VuiBox>
          </Card>
        ) : (
          <>
            {/* Integration Cards */}
            <Grid container spacing={3}>
              {integrations.length > 0 ? (
                integrations.map((integration) => (
                  <Grid item xs={12} md={6} xl={3} key={integration.id}>
                    <Card sx={{ height: "100%" }}>
                      <VuiBox display="flex" flexDirection="column" p={3} height="100%">
                        <VuiBox 
                          display="flex" 
                          justifyContent="center" 
                          alignItems="center" 
                          bgColor={integration.connected ? "success" : "error"} 
                          width="60px" 
                          height="60px" 
                          borderRadius="lg" 
                          shadow="md" 
                          mb={3}
                        >
                          {integration.icon}
                        </VuiBox>
                        
                        <VuiBox display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                          <VuiTypography variant="h5" color="white" fontWeight="bold">
                            {integration.name}
                          </VuiTypography>
                          <Tooltip title={integration.connected ? "Last synced" : "Not connected"}>
                            <VuiBox>
                              {integration.connected ? (
                                <FaSync size="16px" color="#16f9aa" />
                              ) : (
                                <IoInformationCircle size="16px" color="#fff" />
                              )}
                            </VuiBox>
                          </Tooltip>
                        </VuiBox>
                        
                        <VuiTypography variant="button" color="text" fontWeight="regular" mb={2}>
                          {integration.description}
                        </VuiTypography>
                        
                        {/* Data Pulled Section */}
                        <VuiBox mb="auto">
                          <VuiTypography variant="caption" color="text" fontWeight="bold" textTransform="uppercase">
                            Data Pulled:
                          </VuiTypography>
                          
                          <VuiBox pl={1} mt={1}>
                            {integration.scopes.map((scope, index) => (
                              <VuiTypography 
                                key={index} 
                                variant="caption" 
                                color="text" 
                                fontWeight="regular"
                                display="block"
                                mb={0.5}
                              >
                                • {scope}
                              </VuiTypography>
                            ))}
                          </VuiBox>
                        </VuiBox>
                        
                        {/* Account Information (if connected) */}
                        {integration.connected && integration.accountName && (
                          <VuiBox mt={2} mb={2}>
                            <Divider />
                            <VuiBox mt={2} display="flex" alignItems="center">
                              <VuiTypography variant="button" color="text" fontWeight="regular">
                                Connected Account:
                              </VuiTypography>
                              <VuiTypography variant="button" color="white" fontWeight="medium" ml={1}>
                                {integration.accountName}
                              </VuiTypography>
                            </VuiBox>
                          </VuiBox>
                        )}
                        
                        {/* Status Indicator */}
                        <VuiBox mt={2} display="flex" alignItems="center">
                          {integration.connected ? (
                            <IoCheckmarkCircle size="18px" color="#16f9aa" />
                          ) : (
                            <IoCloseCircle size="18px" color="#f44335" />
                          )}
                          <VuiTypography 
                            variant="button" 
                            color={integration.color} 
                            fontWeight="medium" 
                            ml={1}
                          >
                            {integration.status}
                          </VuiTypography>
                        </VuiBox>
                        
                        {/* API Key forms based on platform - only shown when not connected */}
                        {!integration.connected && (
                          <>
                            {integration.id === "youtube" && (
                              <form onSubmit={handleYoutubeApiKeySubmit}>
                                <VuiBox mt={2}>
                                  <VuiTypography variant="caption" color="text" fontWeight="regular" mb={1}>
                                    Enter your YouTube API key
                                  </VuiTypography>
                                  <TextField
                                    fullWidth
                                    placeholder="AIzaSyA..."
                                    variant="outlined"
                                    value={youtubeApiKey}
                                    onChange={(e) => setYoutubeApiKey(e.target.value)}
                                    size="small"
                                    sx={{
                                      mb: 2,
                                      '& .MuiOutlinedInput-root': {
                                        '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.3)' },
                                        '&:hover fieldset': { borderColor: 'rgba(255, 255, 255, 0.5)' },
                                        '&.Mui-focused fieldset': { borderColor: '#0075ff' },
                                        color: 'white'
                                      }
                                    }}
                                  />
                                  <VuiTypography variant="caption" color="text" fontWeight="regular" mb={1}>
                                    Enter your YouTube Channel ID
                                  </VuiTypography>
                                  <TextField
                                    fullWidth
                                    placeholder="UCxxx..."
                                    variant="outlined"
                                    value={youtubeChannelId}
                                    onChange={(e) => setYoutubeChannelId(e.target.value)}
                                    size="small"
                                    sx={{
                                      mb: 2,
                                      '& .MuiOutlinedInput-root': {
                                        '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.3)' },
                                        '&:hover fieldset': { borderColor: 'rgba(255, 255, 255, 0.5)' },
                                        '&.Mui-focused fieldset': { borderColor: '#0075ff' },
                                        color: 'white'
                                      }
                                    }}
                                  />
                                  <VuiTypography variant="caption" color="info" fontWeight="regular" mb={2} display="block">
                                    Create an API key in Google Cloud Console and get your Channel ID from your YouTube URL
                                  </VuiTypography>
                                  <VuiButton
                                    color="success"
                                    variant="contained"
                                    fullWidth
                                    type="submit"
                                  >
                                    Connect
                                  </VuiButton>
                                </VuiBox>
                              </form>
                            )}
                            
                            {integration.id === "stripe" && (
                              <form onSubmit={handleStripeApiKeySubmit}>
                                <VuiBox mt={2}>
                                  <VuiTypography variant="caption" color="text" fontWeight="regular" mb={1}>
                                    Enter your Stripe Secret Key
                                  </VuiTypography>
                                  <TextField
                                    fullWidth
                                    placeholder="sk_live_..."
                                    variant="outlined"
                                    value={stripeApiKey}
                                    onChange={(e) => setStripeApiKey(e.target.value)}
                                    size="small"
                                    sx={{
                                      mb: 2,
                                      '& .MuiOutlinedInput-root': {
                                        '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.3)' },
                                        '&:hover fieldset': { borderColor: 'rgba(255, 255, 255, 0.5)' },
                                        '&.Mui-focused fieldset': { borderColor: '#0075ff' },
                                        color: 'white'
                                      }
                                    }}
                                  />
                                  <VuiTypography variant="caption" color="info" fontWeight="regular" mb={2} display="block">
                                    Find your API key in Stripe Dashboard under Developers &gt; API keys
                                  </VuiTypography>
                                  <VuiButton
                                    color="success"
                                    variant="contained"
                                    fullWidth
                                    type="submit"
                                  >
                                    Connect
                                  </VuiButton>
                                </VuiBox>
                              </form>
                            )}
                            
                            {integration.id === "calendly" && (
                              <form onSubmit={handleCalendlyApiKeySubmit}>
                                <VuiBox mt={2}>
                                  <VuiTypography variant="caption" color="text" fontWeight="regular" mb={1}>
                                    Enter your Calendly API key
                                  </VuiTypography>
                                  <TextField
                                    fullWidth
                                    placeholder="cal_live_..."
                                    variant="outlined"
                                    value={calendlyApiKey}
                                    onChange={(e) => setCalendlyApiKey(e.target.value)}
                                    size="small"
                                    sx={{
                                      mb: 2,
                                      '& .MuiOutlinedInput-root': {
                                        '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.3)' },
                                        '&:hover fieldset': { borderColor: 'rgba(255, 255, 255, 0.5)' },
                                        '&.Mui-focused fieldset': { borderColor: '#0075ff' },
                                        color: 'white'
                                      }
                                    }}
                                  />
                                  <VuiTypography variant="caption" color="info" fontWeight="regular" mb={2} display="block">
                                    Find your API key in Calendly under Integrations &gt; API &amp; Webhooks
                                  </VuiTypography>
                                  <VuiButton
                                    color="success"
                                    variant="contained"
                                    fullWidth
                                    type="submit"
                                  >
                                    Connect
                                  </VuiButton>
                                </VuiBox>
                              </form>
                            )}
                            
                            {integration.id === "calcom" && (
                              <form onSubmit={handleCalcomApiKeySubmit}>
                                <VuiBox mt={2}>
                                  <VuiTypography variant="caption" color="text" fontWeight="regular" mb={1}>
                                    Enter your Cal.com API key
                                  </VuiTypography>
                                  <TextField
                                    fullWidth
                                    placeholder="cal_live_..."
                                    variant="outlined"
                                    value={calcomApiKey}
                                    onChange={(e) => setCalcomApiKey(e.target.value)}
                                    size="small"
                                    sx={{
                                      mb: 2,
                                      '& .MuiOutlinedInput-root': {
                                        '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.3)' },
                                        '&:hover fieldset': { borderColor: 'rgba(255, 255, 255, 0.5)' },
                                        '&.Mui-focused fieldset': { borderColor: '#0075ff' },
                                        color: 'white'
                                      }
                                    }}
                                  />
                                  <VuiTypography variant="caption" color="info" fontWeight="regular" mb={2} display="block">
                                    Find your API key in Cal.com dashboard under Settings &gt; Developer &gt; API Keys
                                  </VuiTypography>
                                  <VuiButton
                                    color="success"
                                    variant="contained"
                                    fullWidth
                                    type="submit"
                                  >
                                    Connect
                                  </VuiButton>
                                </VuiBox>
                              </form>
                            )}
                          </>
                        )}
                        
                        {/* Disconnect Button - only shown when connected */}
                        {integration.connected && (
                          <VuiBox mt={2}>
                            <VuiButton
                              color="error"
                              variant="contained"
                              fullWidth
                              onClick={() => handleDisconnect(integration.id)}
                            >
                              Disconnect
                            </VuiButton>
                          </VuiBox>
                        )}
                      </VuiBox>
                    </Card>
                  </Grid>
                ))
              ) : (
                <Grid item xs={12}>
                  <Card>
                    <VuiBox p={3} display="flex" justifyContent="center">
                      <VuiTypography variant="button" color="text" fontWeight="regular">
                        No integration platforms available. Please try again later.
                      </VuiTypography>
                    </VuiBox>
                  </Card>
                </Grid>
              )}
            </Grid>

            {/* UTM Link Generator Promo */}
            <Card sx={{ mt: 3 }}>
              <VuiBox p={3}>
                <Grid container spacing={3} alignItems="center">
                  <Grid item xs={12} lg={9}>
                    <VuiBox display="flex" alignItems="center">
                      <VuiBox 
                        display="flex" 
                        justifyContent="center" 
                        alignItems="center" 
                        bgColor="info" 
                        width="40px" 
                        height="40px" 
                        borderRadius="lg" 
                        shadow="md" 
                        mr={2}
                      >
                        <FaLink color="white" size="18px" />
                      </VuiBox>
                      <VuiBox>
                        <VuiTypography variant="h5" color="white" fontWeight="bold">
                          Need to create a UTM tracking link?
                        </VuiTypography>
                        <VuiTypography variant="button" color="text" fontWeight="regular">
                          Generate UTM links that work with your integrations for better attribution
                        </VuiTypography>
                      </VuiBox>
                    </VuiBox>
                  </Grid>
                  <Grid item xs={12} lg={3}>
                    <Link to="/utm-generator" style={{ textDecoration: "none" }}>
                      <VuiButton
                        color="info"
                        variant="contained"
                        fullWidth
                      >
                        Go to UTM Generator
                      </VuiButton>
                    </Link>
                  </Grid>
                </Grid>
              </VuiBox>
            </Card>
          </>
        )}
        
        {/* Snackbar Alert */}
        <Snackbar
          open={alert.show}
          autoHideDuration={6000}
          onClose={handleCloseAlert}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        >
          <Alert 
            onClose={handleCloseAlert} 
            severity={alert.severity} 
            sx={{ 
              width: '100%', 
              backgroundColor: alert.severity === 'success' ? '#2dce89' : 
                               alert.severity === 'error' ? '#f5365c' : 
                               alert.severity === 'warning' ? '#fb6340' : '#11cdef',
              color: 'white'
            }}
          >
            {alert.message}
          </Alert>
        </Snackbar>
      </VuiBox>
      <Footer />
    </DashboardLayout>
  );
}

export default Integrations;