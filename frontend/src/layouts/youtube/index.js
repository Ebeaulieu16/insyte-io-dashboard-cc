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

function YouTube() {
  const { gradients } = colors;
  const { cardContent } = gradients;

  // Aggregate data calculations
  const totalViews = videoPerformanceData.reduce((sum, video) => sum + video.views, 0);
  const totalLikes = videoPerformanceData.reduce((sum, video) => sum + video.likes, 0);
  const totalComments = videoPerformanceData.reduce((sum, video) => sum + video.comments, 0);
  const totalClicks = videoPerformanceData.reduce((sum, video) => sum + video.clicks, 0);
  const totalBookedCalls = videoPerformanceData.reduce((sum, video) => sum + video.bookedCalls, 0);
  const totalClosedDeals = videoPerformanceData.reduce((sum, video) => sum + video.closedDeals, 0);
  const totalRevenue = videoPerformanceData.reduce((sum, video) => sum + video.revenue, 0);
  
  // Calculate averages and rates
  const avgViewDuration = "7:42";  // This would be calculated from actual data
  const conversionRate = (totalClicks / totalViews * 100).toFixed(2);
  const callBookingRate = (totalBookedCalls / totalClicks * 100).toFixed(2);
  const dealClosingRate = (totalClosedDeals / totalBookedCalls * 100).toFixed(2);

  // Handle date filter changes
  const handleDateChange = (dateRange) => {
    console.log("Date range changed:", dateRange);
    // Here you would fetch new data based on the date range
  };

  // Format numbers with commas
  const formatNumber = (num) => {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  };

  // Format currency
  const formatCurrency = (num) => {
    return "$" + formatNumber(num);
  };

  // State for YouTube connection status
  const [isYoutubeConnected, setIsYoutubeConnected] = useState(false);
  
  // Check YouTube connection status
  useEffect(() => {
    const checkYoutubeConnection = async () => {
      try {
        const response = await api.get("/api/integrations/status");
        const youtubeIntegration = response.data.integrations.find(
          integration => integration.platform === "youtube"
        );
        setIsYoutubeConnected(youtubeIntegration && youtubeIntegration.status === "connected");
      } catch (error) {
        console.error("Failed to check YouTube connection status:", error);
        setIsYoutubeConnected(false);
      }
    };
    
    checkYoutubeConnection();
  }, []);

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <VuiBox py={3}>
        {/* Date Filter */}
        <VuiBox display="flex" justifyContent="flex-end" mb={3}>
          <DateFilter onChange={handleDateChange} />
        </VuiBox>
        
        {/* YouTube Connection Prompt - Only show if not connected */}
        {!isYoutubeConnected && (
          <VuiBox mb={3}>
            <Card>
              <VuiBox p={3}>
                <Grid container spacing={3} alignItems="center">
                  <Grid item xs={12} lg={9}>
                    <VuiBox display="flex" alignItems="center">
                      <VuiBox 
                        display="flex" 
                        justifyContent="center" 
                        alignItems="center" 
                        bgColor="error" 
                        width="50px" 
                        height="50px" 
                        borderRadius="lg" 
                        shadow="md" 
                        mr={2}
                      >
                        <FaPlug color="white" size="22px" />
                      </VuiBox>
                      <VuiBox>
                        <VuiTypography variant="h5" color="white" fontWeight="bold">
                          Connect Your YouTube Channel
                        </VuiTypography>
                        <VuiTypography variant="button" color="text" fontWeight="regular">
                          Connect your YouTube channel to see real video performance data, track revenue, and get advanced analytics
                        </VuiTypography>
                      </VuiBox>
                    </VuiBox>
                  </Grid>
                  <Grid item xs={12} lg={3}>
                    <Link to="/integrations" style={{ textDecoration: "none" }}>
                      <VuiButton
                        color="error"
                        variant="contained"
                        fullWidth
                      >
                        Go to Integrations
                      </VuiButton>
                    </Link>
                  </Grid>
                </Grid>
              </VuiBox>
            </Card>
          </VuiBox>
        )}

        {/* YouTube Performance Metrics - Top Row */}
        <VuiBox mb={3}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6} xl={3}>
              <MiniStatisticsCard
                title={{ text: "total views", fontWeight: "regular" }}
                count={formatNumber(totalViews)}
                percentage={{ color: "success", text: "+12%" }}
                icon={{ color: "info", component: <FaEye size="20px" color="white" /> }}
              />
            </Grid>
            <Grid item xs={12} md={6} xl={3}>
              <MiniStatisticsCard
                title={{ text: "total likes" }}
                count={formatNumber(totalLikes)}
                percentage={{ color: "success", text: "+5%" }}
                icon={{ color: "info", component: <FaThumbsUp size="18px" color="white" /> }}
              />
            </Grid>
            <Grid item xs={12} md={6} xl={3}>
              <MiniStatisticsCard
                title={{ text: "total comments" }}
                count={formatNumber(totalComments)}
                percentage={{ color: "success", text: "+7%" }}
                icon={{ color: "info", component: <FaComments size="18px" color="white" /> }}
              />
            </Grid>
            <Grid item xs={12} md={6} xl={3}>
              <MiniStatisticsCard
                title={{ text: "avg. view duration" }}
                count={avgViewDuration}
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
                count={conversionRate + "%"}
                percentage={{ color: "success", text: "+2%" }}
                icon={{ color: "info", component: <IoStatsChart size="22px" color="white" /> }}
              />
            </Grid>
            <Grid item xs={12} md={6} xl={3}>
              <MiniStatisticsCard
                title={{ text: "booking rate" }}
                count={callBookingRate + "%"}
                percentage={{ color: "success", text: "+8%" }}
                icon={{ color: "info", component: <FaYoutube size="20px" color="white" /> }}
              />
            </Grid>
            <Grid item xs={12} md={6} xl={3}>
              <MiniStatisticsCard
                title={{ text: "closing rate" }}
                count={dealClosingRate + "%"}
                percentage={{ color: "success", text: "+12%" }}
                icon={{ color: "info", component: <IoStatsChart size="22px" color="white" /> }}
              />
            </Grid>
            <Grid item xs={12} md={6} xl={3}>
              <MiniStatisticsCard
                title={{ text: "total revenue" }}
                count={formatCurrency(totalRevenue)}
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
              <VideoTable videos={videoPerformanceData} />
            </Grid>
          </Grid>
        </VuiBox>
      </VuiBox>
      <Footer />
    </DashboardLayout>
  );
}

export default YouTube; 