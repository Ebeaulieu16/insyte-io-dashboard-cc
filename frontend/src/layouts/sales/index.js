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

// React icons
import { FaChartPie, FaUserCheck, FaCalendarAlt, FaCreditCard, FaChartLine, FaUserPlus, FaMoneyBillWave, FaPlug } from "react-icons/fa";
import { IoStatsChart, IoPersonSharp } from "react-icons/io5";

// Importing ApexCharts (must be installed)
import Chart from "react-apexcharts";

// React hooks
import { useState, useEffect } from "react";
import { Link } from "react-router-dom";

// API utility
import api from "utils/api";

// Integration context
import { useIntegration } from "../../context/IntegrationContext";

// Data
import { funnelChartData, funnelChartOptions, donutChartData, donutChartOptions } from "layouts/sales/data/salesData";

function Sales() {
  const { gradients } = colors;
  const { cardContent } = gradients;
  
  // Get integration status from context
  const { isAnyIntegrationConnected, isIntegrationConnected } = useIntegration();

  // State for charts data
  const [salesData, setSalesData] = useState({
    funnel: funnelChartData,
    donut: donutChartData
  });
  
  // State for metrics
  const [metrics, setMetrics] = useState({
    leads: "1,205",
    bookedCalls: "935",
    rescheduled: "53",
    liveCalls: "782",
    showUpRate: "84.6%",
    closeRate: "62.4%",
    aov: "$5,832",
    cashCollected: "$235,486"
  });

  // Handle date filter changes
  const handleDateChange = (dateRange) => {
    console.log("Date range changed:", dateRange);
    // Fetch data based on date range
    fetchSalesData(dateRange);
  };

  // Loading state
  const [loading, setLoading] = useState(true);
  
  // Fetch real sales data from the API
  const fetchSalesData = async (dateRange) => {
    if (!isAnyIntegrationConnected) {
      console.log("No integrations connected, using demo data");
      return;
    }
    
    setLoading(true);
    try {
      // Get real data from the API if any integration is connected
      const response = await api.get("/api/sales/data", {
        params: dateRange
      });
      
      console.log("Got real sales data:", response.data);
      
      if (response.data && response.data.funnel) {
        setSalesData({
          funnel: response.data.funnel,
          donut: response.data.donut || donutChartData
        });
      }
      
      if (response.data && response.data.metrics) {
        setMetrics(response.data.metrics);
      }
    } catch (error) {
      console.error("Failed to fetch sales data:", error);
      // Keep using demo data on error
    } finally {
      setLoading(false);
    }
  };
  
  // Fetch data when integration status changes
  useEffect(() => {
    if (isAnyIntegrationConnected) {
      fetchSalesData();
    } else {
      setLoading(false);
    }
  }, [isAnyIntegrationConnected]);

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <VuiBox py={3}>
        {/* Demo Mode Banner */}
        {!isAnyIntegrationConnected && (
          <VuiBox mb={3} p={2} borderRadius="lg" bgColor="info">
            <VuiTypography variant="button" color="white" fontWeight="medium">
              Demo Mode - No integrations connected. Showing sample sales data.
            </VuiTypography>
          </VuiBox>
        )}
        
        {/* Date Filter */}
        <VuiBox display="flex" justifyContent="flex-end" mb={3}>
          <DateFilter onChange={handleDateChange} />
        </VuiBox>

        {/* Top metrics */}
        <VuiBox mb={3}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6} xl={3}>
              <MiniStatisticsCard
                title={{ text: "leads", fontWeight: "regular" }}
                count={metrics.leads}
                percentage={{ color: "success", text: "+12%" }}
                icon={{ color: "info", component: <FaUserPlus size="20px" color="white" /> }}
              />
            </Grid>
            <Grid item xs={12} md={6} xl={3}>
              <MiniStatisticsCard
                title={{ text: "booked calls" }}
                count={metrics.bookedCalls}
                percentage={{ color: "success", text: "+5%" }}
                icon={{ color: "info", component: <FaCalendarAlt size="20px" color="white" /> }}
              />
            </Grid>
            <Grid item xs={12} md={6} xl={3}>
              <MiniStatisticsCard
                title={{ text: "rescheduled" }}
                count={metrics.rescheduled}
                percentage={{ color: "error", text: "+12%" }}
                icon={{ color: "info", component: <IoStatsChart size="20px" color="white" /> }}
              />
            </Grid>
            <Grid item xs={12} md={6} xl={3}>
              <MiniStatisticsCard
                title={{ text: "live calls" }}
                count={metrics.liveCalls}
                percentage={{ color: "success", text: "+8%" }}
                icon={{ color: "info", component: <IoPersonSharp size="20px" color="white" /> }}
              />
            </Grid>
          </Grid>
        </VuiBox>

        {/* Performance Metrics */}
        <VuiBox mb={3}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6} xl={3}>
              <MiniStatisticsCard
                title={{ text: "show-up rate", fontWeight: "regular" }}
                count={metrics.showUpRate}
                percentage={{ color: "success", text: "+3%" }}
                icon={{ color: "info", component: <FaUserCheck size="20px" color="white" /> }}
              />
            </Grid>
            <Grid item xs={12} md={6} xl={3}>
              <MiniStatisticsCard
                title={{ text: "close rate" }}
                count={metrics.closeRate}
                percentage={{ color: "success", text: "+7%" }}
                icon={{ color: "info", component: <FaChartLine size="20px" color="white" /> }}
              />
            </Grid>
            <Grid item xs={12} md={6} xl={3}>
              <MiniStatisticsCard
                title={{ text: "AOV" }}
                count={metrics.aov}
                percentage={{ color: "success", text: "+12%" }}
                icon={{ color: "info", component: <FaChartPie size="20px" color="white" /> }}
              />
            </Grid>
            <Grid item xs={12} md={6} xl={3}>
              <MiniStatisticsCard
                title={{ text: "cash collected" }}
                count={metrics.cashCollected}
                percentage={{ color: "success", text: "+18%" }}
                icon={{ color: "info", component: <FaMoneyBillWave size="20px" color="white" /> }}
              />
            </Grid>
          </Grid>
        </VuiBox>

        <VuiBox mb={3}>
          <Grid container spacing={3}>
            {/* Funnel Chart */}
            <Grid item xs={12} lg={7}>
              <Card>
                <VuiBox sx={{ height: "100%" }}>
                  <VuiBox display="flex" justifyContent="space-between" alignItems="center" mb="24px" p={3}>
                    <VuiBox>
                      <VuiTypography variant="lg" color="white" fontWeight="bold">
                        Sales Funnel Performance
                      </VuiTypography>
                      <VuiTypography variant="button" color="text" fontWeight="regular">
                        Conversion metrics from lead to closed deal
                      </VuiTypography>
                    </VuiBox>
                  </VuiBox>
                  
                  <VuiBox p={3} height="400px">
                    {loading ? (
                      <VuiBox display="flex" justifyContent="center" alignItems="center" height="100%">
                        <VuiTypography color="text">Loading data...</VuiTypography>
                      </VuiBox>
                    ) : (
                      <Chart
                        options={funnelChartOptions}
                        series={salesData.funnel.series}
                        type="bar"
                        height="100%"
                        width="100%"
                      />
                    )}
                  </VuiBox>
                </VuiBox>
              </Card>
            </Grid>

            {/* Donut Chart */}
            <Grid item xs={12} lg={5}>
              <Card>
                <VuiBox sx={{ height: "100%" }}>
                  <VuiBox display="flex" justifyContent="space-between" alignItems="center" mb="24px" p={3}>
                    <VuiBox>
                      <VuiTypography variant="lg" color="white" fontWeight="bold">
                        Closing Rate
                      </VuiTypography>
                      <VuiTypography variant="button" color="text" fontWeight="regular">
                        Percentage of deals closed vs. lost
                      </VuiTypography>
                    </VuiBox>
                  </VuiBox>
                  
                  <VuiBox p={3} height="400px">
                    {loading ? (
                      <VuiBox display="flex" justifyContent="center" alignItems="center" height="100%">
                        <VuiTypography color="text">Loading data...</VuiTypography>
                      </VuiBox>
                    ) : (
                      <Chart
                        options={donutChartOptions}
                        series={salesData.donut}
                        type="donut"
                        height="100%"
                        width="100%"
                      />
                    )}
                  </VuiBox>
                </VuiBox>
              </Card>
            </Grid>
          </Grid>
        </VuiBox>
      </VuiBox>
      <Footer />
    </DashboardLayout>
  );
}

export default Sales; 