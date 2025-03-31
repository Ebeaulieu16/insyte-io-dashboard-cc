/*!

=========================================================
* Vision UI Free React - v1.0.0
=========================================================

* Product Page: https://www.creative-tim.com/product/vision-ui-free-react
* Copyright 2021 Creative Tim (https://www.creative-tim.com/)
* Licensed under MIT (https://github.com/creativetimofficial/vision-ui-free-react/blob/master LICENSE.md)

* Design and Coded by Simmmple & Creative Tim

=========================================================

* The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

*/

// @mui material components
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import Icon from "@mui/material/Icon";

// Vision UI Dashboard React components
import VuiBox from "components/VuiBox";
import VuiTypography from "components/VuiTypography";
import VuiButton from "components/VuiButton";

// Vision UI Dashboard React example components
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";
import MiniStatisticsCard from "examples/Cards/StatisticsCards/MiniStatisticsCard";

// Vision UI Dashboard React base styles
import typography from "assets/theme/base/typography";
import colors from "assets/theme/base/colors";

// Custom components
import DateFilter from "components/DateFilter";
import VideoTable from "layouts/youtube/components/VideoTable";

// React icons
import { FaYoutube, FaEye, FaThumbsUp, FaComments, FaPlug } from "react-icons/fa";
import { IoStatsChart, IoTimerOutline } from "react-icons/io5";
import { Link } from "react-router-dom";
import { AiFillYoutube } from "react-icons/ai";

// Data
import { videoPerformanceData } from "layouts/youtube/data/youtubeData";

// React hooks
import { useState, useEffect } from "react";
import api from "utils/api";

// Integration context
import { useIntegration } from "../../context/IntegrationContext";

function YouTube() {
  const { gradients } = colors;
  const { cardContent } = gradients;
  
  // Get integration status from context
  const { isAnyIntegrationConnected, isIntegrationConnected } = useIntegration();
  
  // Check if YouTube is specifically connected
  const isYoutubeSpecificallyConnected = isIntegrationConnected("youtube");

  // State for video data and metrics
  const [videos, setVideos] = useState(videoPerformanceData);
  const [metrics, setMetrics] = useState({
    totalViews: 0,
    totalLikes: 0,
    totalComments: 0,
    totalClicks: 0,
    totalBookedCalls: 0,
    totalClosedDeals: 0,
    totalRevenue: 0,
    conversionRate: 0,
    bookingRate: 0,
    closingRate: 0,
    avgViewDuration: "7:42"
  });
  const [loading, setLoading] = useState(true);

  // Calculate totals from videos (used for demo mode or initial load)
  useEffect(() => {
    // Only calculate from static data if we don't have metrics from the API
    if (!metrics.totalViews) {
      const totalViews = videos.reduce((sum, video) => sum + video.views, 0);
      const totalLikes = videos.reduce((sum, video) => sum + video.likes, 0);
      const totalComments = videos.reduce((sum, video) => sum + video.comments, 0);
      const totalClicks = videos.reduce((sum, video) => sum + video.clicks, 0);
      const totalBookedCalls = videos.reduce((sum, video) => sum + video.bookedCalls, 0);
      const totalClosedDeals = videos.reduce((sum, video) => sum + video.closedDeals, 0);
      const totalRevenue = videos.reduce((sum, video) => sum + video.revenue, 0);
      
      // Calculate rates
      const conversionRate = (totalClicks / totalViews * 100).toFixed(2);
      const bookingRate = (totalBookedCalls / totalClicks * 100).toFixed(2);
      const closingRate = (totalClosedDeals / totalBookedCalls * 100).toFixed(2);
      
      setMetrics({
        totalViews,
        totalLikes,
        totalComments,
        totalClicks,
        totalBookedCalls,
        totalClosedDeals,
        totalRevenue,
        conversionRate,
        bookingRate,
        closingRate,
        avgViewDuration: "7:42"
      });
    }
  }, [videos]);

  // Fetch YouTube data from API
  const fetchYoutubeData = async () => {
    if (!isAnyIntegrationConnected) {
      console.log("No integrations connected, using demo data");
      setLoading(false);
      return;
    }
    
    setLoading(true);
    try {
      // Get real data from the API if any integration is connected
      const response = await api.get("/api/youtube/data");
      console.log("Got YouTube data:", response.data);
      
      if (response.data && response.data.videos) {
        setVideos(response.data.videos);
      }
      
      if (response.data && response.data.metrics) {
        setMetrics({
          ...response.data.metrics,
          avgViewDuration: "7:42" // Default as this isn't calculated in the backend
        });
      }
    } catch (error) {
      console.error("Failed to fetch YouTube data:", error);
      // Keep using demo data on error
    } finally {
      setLoading(false);
    }
  };
  
  // Fetch data when integration status changes
  useEffect(() => {
    fetchYoutubeData();
  }, [isAnyIntegrationConnected]);

  // Handle date filter changes
  const handleDateChange = (dateRange) => {
    console.log("Date range changed:", dateRange);
    // Refetch data with the new date range
    fetchYoutubeData();
  };

  // Format numbers with commas
  const formatNumber = (num) => {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  };

  // Format currency
  const formatCurrency = (num) => {
    return "$" + formatNumber(num);
  };

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <VuiBox py={3}>
        {/* Demo Mode Banner */}
        {!isAnyIntegrationConnected && (
          <VuiBox mb={3} p={2} borderRadius="lg" bgColor="info">
            <VuiTypography variant="button" color="white" fontWeight="medium">
              Demo Mode - No integrations connected. Showing sample YouTube data.
            </VuiTypography>
          </VuiBox>
        )}
        
        {/* Date Filter */}
        <VuiBox display="flex" justifyContent="flex-end" mb={3}>
          <DateFilter onChange={handleDateChange} />
        </VuiBox>
        
        {/* Loading indicator */}
        {loading && (
          <VuiBox mb={3} display="flex" justifyContent="center">
            <VuiTypography color="text">Loading YouTube data...</VuiTypography>
          </VuiBox>
        )}
        
        {/* YouTube Performance Metrics - Top Row */}
        <VuiBox mb={3}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6} xl={3}>
              <MiniStatisticsCard
                title={{ text: "total views", fontWeight: "regular" }}
                count={formatNumber(metrics.totalViews)}
                percentage={{ color: "success", text: "+12%" }}
                icon={{ color: "info", component: <FaEye size="20px" color="white" /> }}
              />
            </Grid>
            <Grid item xs={12} md={6} xl={3}>
              <MiniStatisticsCard
                title={{ text: "total likes" }}
                count={formatNumber(metrics.totalLikes)}
                percentage={{ color: "success", text: "+5%" }}
                icon={{ color: "info", component: <FaThumbsUp size="18px" color="white" /> }}
              />
            </Grid>
            <Grid item xs={12} md={6} xl={3}>
              <MiniStatisticsCard
                title={{ text: "total comments" }}
                count={formatNumber(metrics.totalComments)}
                percentage={{ color: "success", text: "+7%" }}
                icon={{ color: "info", component: <FaComments size="18px" color="white" /> }}
              />
            </Grid>
            <Grid item xs={12} md={6} xl={3}>
              <MiniStatisticsCard
                title={{ text: "avg. view duration" }}
                count={metrics.avgViewDuration}
                percentage={{ color: "success", text: "+3%" }}
                icon={{ color: "info", component: <IoTimerOutline size="22px" color="white" /> }}
              />
            </Grid>
          </Grid>
        </VuiBox>

        {/* YouTube Performance Metrics - Bottom Row */}
        <VuiBox mb={3}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6} xl={3}>
              <MiniStatisticsCard
                title={{ text: "conversion rate", fontWeight: "regular" }}
                count={metrics.conversionRate + "%"}
                percentage={{ color: "success", text: "+2%" }}
                icon={{ color: "info", component: <IoStatsChart size="22px" color="white" /> }}
              />
            </Grid>
            <Grid item xs={12} md={6} xl={3}>
              <MiniStatisticsCard
                title={{ text: "booking rate" }}
                count={metrics.bookingRate + "%"}
                percentage={{ color: "success", text: "+8%" }}
                icon={{ color: "info", component: <FaYoutube size="20px" color="white" /> }}
              />
            </Grid>
            <Grid item xs={12} md={6} xl={3}>
              <MiniStatisticsCard
                title={{ text: "closing rate" }}
                count={metrics.closingRate + "%"}
                percentage={{ color: "success", text: "+12%" }}
                icon={{ color: "info", component: <IoStatsChart size="22px" color="white" /> }}
              />
            </Grid>
            <Grid item xs={12} md={6} xl={3}>
              <MiniStatisticsCard
                title={{ text: "total revenue" }}
                count={formatCurrency(metrics.totalRevenue)}
                percentage={{ color: "success", text: "+18%" }}
                icon={{ color: "info", component: <FaYoutube size="20px" color="white" /> }}
              />
            </Grid>
          </Grid>
        </VuiBox>

        {/* Video Performance Table */}
        <VuiBox>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <VideoTable videos={videos} />
            </Grid>
          </Grid>
        </VuiBox>
      </VuiBox>
      <Footer />
    </DashboardLayout>
  );
}

export default YouTube; 