import React, { useState } from "react";
import { Box, TextField, Button, Typography, CircularProgress } from "@mui/material";
import { FaYoutube } from "react-icons/fa";
import VuiBox from "components/VuiBox";
import VuiTypography from "components/VuiTypography";
import VuiButton from "components/VuiButton";
import { useIntegration } from "../../../context/IntegrationContext";
import api from '../../../utils/api';

function YouTubeConnectForm({ onConnectionSuccess, onConnectionError }) {
  const [apiKey, setApiKey] = useState("");
  const [channelId, setChannelId] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const { addLocalIntegration, refreshIntegrations } = useIntegration();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validation
    if (!apiKey.trim()) {
      setErrorMessage("Please enter your YouTube API key");
      return;
    }

    if (!channelId.trim()) {
      setErrorMessage("Please enter your YouTube channel ID");
      return;
    }

    setLoading(true);
    setErrorMessage("");
    
    // Show optimistic UI feedback immediately
    const accountName = `YouTube Channel: ${channelId}`;
    
    // Add integration to local cache first for instant feedback
    addLocalIntegration("youtube", accountName);
    
    // Trigger connection success callback for UI updates
    onConnectionSuccess && onConnectionSuccess("youtube", accountName);
    
    try {
      // Set a longer timeout specifically for this request
      const connectPromise = api.post("/api/integrations/youtube/api-key", {
        api_key: apiKey,
        channel_id: channelId
      }, {
        timeout: 60000 // 60 second timeout specifically for YouTube
      });
      
      // Create a timeout promise
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => {
          reject(new Error("Connection is taking longer than expected, but your channel might still be connected."));
        }, 15000); // 15 second UI timeout
      });
      
      // Race between the actual connection and the timeout
      const response = await Promise.race([connectPromise, timeoutPromise]);
      
      console.log("YouTube API key submitted:", response.data);
      
      // Clear form fields on success
      setApiKey("");
      setChannelId("");
      
      // Refresh integrations after successful connection
      setTimeout(() => {
        refreshIntegrations();
      }, 500);
      
    } catch (error) {
      console.error("Error submitting YouTube API key:", error);
      
      // Don't revert the UI state - keep optimistic update to reduce confusion
      // Just show error message
      setErrorMessage(error.response?.data?.detail || error.message || 
        "Connection timeout - but your channel might still be connected. Please refresh the page in a few seconds.");
      
      // Notify parent component about the error but don't revert UI
      onConnectionError && onConnectionError("youtube", "warning", error.message, false);
      
      // Still trigger a refresh to check if connection was actually successful despite the error
      setTimeout(() => {
        refreshIntegrations();
      }, 2000);
    } finally {
      setLoading(false);
    }
  };

  return (
    <VuiBox component="form" onSubmit={handleSubmit}>
      <VuiBox mb={2}>
        <VuiTypography variant="button" color="text" fontWeight="medium">
          Connect YouTube Channel
        </VuiTypography>
      </VuiBox>
      
      {errorMessage && (
        <VuiBox mb={2}>
          <VuiTypography variant="button" color="error" fontWeight="regular">
            {errorMessage}
          </VuiTypography>
        </VuiBox>
      )}
      
      <VuiBox mb={2}>
        <TextField
          fullWidth
          label="YouTube API Key"
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
          placeholder="AIza..."
          variant="outlined"
          required
          sx={{ mb: 2 }}
        />
        
        <TextField
          fullWidth
          label="YouTube Channel ID"
          value={channelId}
          onChange={(e) => setChannelId(e.target.value)}
          placeholder="UC..."
          variant="outlined"
          required
        />
      </VuiBox>
      
      <VuiBox mt={3} mb={1} textAlign="center">
        <VuiButton
          type="submit"
          color="info"
          fullWidth
          disabled={loading}
          startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <FaYoutube />}
        >
          {loading ? "Connecting..." : "Connect YouTube"}
        </VuiButton>
      </VuiBox>
      
      {loading && (
        <VuiBox mt={2} textAlign="center">
          <VuiTypography variant="caption" color="text">
            This may take a moment. If it times out, your connection might still be processed in the background.
          </VuiTypography>
        </VuiBox>
      )}
    </VuiBox>
  );
}

export default YouTubeConnectForm; 