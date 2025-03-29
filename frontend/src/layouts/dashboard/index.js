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
import { LinearProgress, Stack } from "@mui/material";
import { Link } from "react-router-dom";

// Vision UI Dashboard React components
import VuiBox from "components/VuiBox";
import VuiTypography from "components/VuiTypography";
import VuiProgress from "components/VuiProgress";
import VuiButton from "components/VuiButton";

// Vision UI Dashboard React example components
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";
import MiniStatisticsCard from "examples/Cards/StatisticsCards/MiniStatisticsCard";
import linearGradient from "assets/theme/functions/linearGradient";

// Vision UI Dashboard React base styles
import typography from "assets/theme/base/typography";
import colors from "assets/theme/base/colors";

// Custom components
import DateFilter from "components/DateFilter";

// React icons
import { IoStatsChart, IoPersonSharp, IoCash, IoCheckmarkCircle } from "react-icons/io5";
import { FaPhone, FaUserTimes, FaVideoSlash, FaChartLine, FaPlug } from "react-icons/fa";

// Data
import LineChart from "examples/Charts/LineCharts/LineChart";
import BarChart from "examples/Charts/BarCharts/BarChart";
import { lineChartData, lineChartOptions, revenueBarChartData, revenueBarChartOptions } from "layouts/dashboard/data/dashboardData";

function Dashboard() {
  const { gradients } = colors;
  const { cardContent } = gradients;

  // Handle date filter changes
  const handleDateChange = (dateRange) => {
    console.log("Date range changed:", dateRange);
    // Here you would fetch new data based on the date range
  };

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <VuiBox py={3}>
        {/* Date Filter */}
        <VuiBox display="flex" justifyContent="flex-end" mb={3}>
          <DateFilter onChange={handleDateChange} />
        </VuiBox>

        {/* Platform Integration Prompt */}
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
                      bgColor="info" 
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
                        Connect Your Platforms
                      </VuiTypography>
                      <VuiTypography variant="button" color="text" fontWeight="regular">
                        Connect your YouTube, Stripe, Calendly and other accounts to see your real data and metrics
                      </VuiTypography>
                    </VuiBox>
                  </VuiBox>
                </Grid>
                <Grid item xs={12} lg={3}>
                  <Link to="/integrations" style={{ textDecoration: "none" }}>
                    <VuiButton
                      color="info"
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

        {/* KPI Statistics */}
        <VuiBox mb={3}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6} xl={3}>
              <MiniStatisticsCard
                title={{ text: "total clicks", fontWeight: "regular" }}
                count="4,350"
                percentage={{ color: "success", text: "+15%" }}
                icon={{ color: "info", component: <IoStatsChart size="22px" color="white" /> }}
              />
            </Grid>
            <Grid item xs={12} md={6} xl={3}>
              <MiniStatisticsCard
                title={{ text: "booked calls" }}
                count="935"
                percentage={{ color: "success", text: "+12%" }}
                icon={{ color: "info", component: <FaPhone size="20px" color="white" /> }}
              />
            </Grid>
            <Grid item xs={12} md={6} xl={3}>
              <MiniStatisticsCard
                title={{ text: "no-shows" }}
                count="128"
                percentage={{ color: "error", text: "+5%" }}
                icon={{ color: "info", component: <FaUserTimes size="20px" color="white" /> }}
              />
            </Grid>
            <Grid item xs={12} md={6} xl={3}>
              <MiniStatisticsCard
                title={{ text: "live calls" }}
                count="807"
                percentage={{ color: "success", text: "+8%" }}
                icon={{ color: "info", component: <FaVideoSlash size="20px" color="white" /> }}
              />
            </Grid>
          </Grid>
        </VuiBox>

        <VuiBox mb={3}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6} xl={3}>
              <MiniStatisticsCard
                title={{ text: "revenue", fontWeight: "regular" }}
                count="$284,500"
                percentage={{ color: "success", text: "+23%" }}
                icon={{ color: "info", component: <IoCash size="22px" color="white" /> }}
              />
            </Grid>
            <Grid item xs={12} md={6} xl={3}>
              <MiniStatisticsCard
                title={{ text: "closing rate" }}
                count="62.4%"
                percentage={{ color: "success", text: "+3%" }}
                icon={{ color: "info", component: <FaChartLine size="20px" color="white" /> }}
              />
            </Grid>
            <Grid item xs={12} md={6} xl={3}>
              <MiniStatisticsCard
                title={{ text: "avg. deal value" }}
                count="$5,832"
                percentage={{ color: "success", text: "+7%" }}
                icon={{ color: "info", component: <IoCheckmarkCircle size="22px" color="white" /> }}
              />
            </Grid>
            <Grid item xs={12} md={6} xl={3}>
              <MiniStatisticsCard
                title={{ text: "clients acquired" }}
                count="48"
                percentage={{ color: "success", text: "+10%" }}
                icon={{ color: "info", component: <IoPersonSharp size="22px" color="white" /> }}
              />
            </Grid>
          </Grid>
        </VuiBox>

        <VuiBox mb={3}>
          <Grid container spacing={3}>
            {/* Traffic & Conversion */}
            <Grid item xs={12} lg={6}>
              <Card>
                <VuiBox sx={{ height: "100%" }}>
                  <VuiTypography variant="lg" color="white" fontWeight="bold" mb="5px" p={2}>
                    Traffic & Conversion
                  </VuiTypography>
                  <VuiBox p={2} mt={3} height="365px">
                    <LineChart 
                      lineChartData={lineChartData} 
                      lineChartOptions={lineChartOptions} 
                    />
                  </VuiBox>
                </VuiBox>
              </Card>
            </Grid>

            {/* Revenue Per YouTube Video */}
            <Grid item xs={12} lg={6}>
              <Card>
                <VuiBox sx={{ height: "100%" }}>
                  <VuiTypography variant="lg" color="white" fontWeight="bold" mb="5px" p={2}>
                    Revenue Per YouTube Video
                  </VuiTypography>
                  <VuiBox p={2} mt={3} height="365px">
                    <BarChart 
                      barChartData={revenueBarChartData} 
                      barChartOptions={revenueBarChartOptions} 
                    />
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

export default Dashboard;
