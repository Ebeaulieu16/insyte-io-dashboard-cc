/*!

=========================================================
* Vision UI Free React - DeepView Analytics Layout
=========================================================

*/

import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";

// @mui material components
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import IconButton from "@mui/material/IconButton";
import Icon from "@mui/material/Icon";

// Vision UI Dashboard React components
import VuiBox from "components/VuiBox";
import VuiTypography from "components/VuiTypography";

// Vision UI Dashboard React example components
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";

// Deep View analytics components
import ClicksTimeline from "layouts/deepView/components/ClicksTimeline";
import FunnelAnalysis from "layouts/deepView/components/FunnelAnalysis";
import CallsList from "layouts/deepView/components/CallsList";
import VideoMetrics from "layouts/deepView/components/VideoMetrics";

// API
import api from "utils/api";

// Toast notifications
import { toast } from "react-toastify";

function DeepView() {
  const { slug } = useParams();
  const navigate = useNavigate();
  
  // State
  const [isLoading, setIsLoading] = useState(true);
  const [analyticsData, setAnalyticsData] = useState(null);
  const [error, setError] = useState(null);
  
  // Fetch data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        const response = await api.get(`/api/links/deep-view/${slug}`);
        setAnalyticsData(response.data);
      } catch (err) {
        console.error("Error fetching deep view data:", err);
        setError(err.response?.data?.detail || "Failed to load analytics data");
        toast.error("Failed to load analytics data");
      } finally {
        setIsLoading(false);
      }
    };
    
    if (slug) {
      fetchData();
    }
  }, [slug]);
  
  // Handle back button click
  const handleBack = () => {
    navigate("/utm-generator");
  };
  
  return (
    <DashboardLayout>
      <DashboardNavbar />
      <VuiBox py={3}>
        <VuiBox mb={3}>
          <Card>
            <VuiBox display="flex" justifyContent="space-between" alignItems="center" p={3}>
              <VuiBox>
                <VuiBox display="flex" alignItems="center">
                  <IconButton 
                    color="white" 
                    onClick={handleBack}
                    sx={{ mr: 1 }}
                  >
                    <Icon>arrow_back</Icon>
                  </IconButton>
                  <VuiTypography variant="h6" fontWeight="medium" color="white">
                    Deep View Analytics
                  </VuiTypography>
                </VuiBox>
                
                {analyticsData && (
                  <VuiBox mt={1}>
                    <VuiTypography variant="subtitle2" fontWeight="regular" color="text">
                      Campaign: {analyticsData.title}
                    </VuiTypography>
                    <VuiTypography variant="caption" fontWeight="regular" color="text">
                      UTM Link: {analyticsData.short_url}
                    </VuiTypography>
                  </VuiBox>
                )}
              </VuiBox>
              
              {analyticsData && (
                <VuiBox
                  bgcolor="info.main"
                  borderRadius="lg"
                  p={1}
                  px={2}
                  display="flex"
                  alignItems="center"
                >
                  <Icon fontSize="small" sx={{ mr: 1 }}>link</Icon>
                  <VuiTypography variant="button" color="white" fontWeight="medium">
                    {analyticsData.clicks} Clicks
                  </VuiTypography>
                </VuiBox>
              )}
            </VuiBox>
          </Card>
        </VuiBox>
        
        {isLoading ? (
          <VuiBox
            display="flex"
            justifyContent="center"
            alignItems="center"
            height="50vh"
          >
            <VuiTypography variant="button" color="text" fontWeight="regular">
              Loading analytics data...
            </VuiTypography>
          </VuiBox>
        ) : error ? (
          <VuiBox
            display="flex"
            justifyContent="center"
            alignItems="center"
            height="50vh"
          >
            <VuiTypography variant="button" color="error" fontWeight="regular">
              {error}
            </VuiTypography>
          </VuiBox>
        ) : analyticsData && (
          <Grid container spacing={3}>
            {/* Clicks Timeline */}
            <Grid item xs={12} lg={7}>
              <ClicksTimeline clicksData={analyticsData.clicks_data} />
            </Grid>
            
            {/* Funnel Analysis */}
            <Grid item xs={12} lg={5}>
              <FunnelAnalysis data={analyticsData} />
            </Grid>
            
            {/* Call List */}
            <Grid item xs={12}>
              <CallsList calls={analyticsData.calls.list} />
            </Grid>
            
            {/* Video Metrics */}
            {analyticsData.video_data && (
              <Grid item xs={12}>
                <VideoMetrics videoData={analyticsData.video_data} />
              </Grid>
            )}
          </Grid>
        )}
      </VuiBox>
      <Footer />
    </DashboardLayout>
  );
}

export default DeepView; 