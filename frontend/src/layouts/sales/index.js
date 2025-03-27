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
import { FaChartPie, FaUserCheck, FaCalendarAlt, FaCreditCard, FaChartLine, FaUserPlus, FaMoneyBillWave } from "react-icons/fa";
import { IoStatsChart, IoPersonSharp } from "react-icons/io5";

// Importing ApexCharts (must be installed)
import Chart from "react-apexcharts";

// Data
import { funnelChartData, funnelChartOptions, donutChartData, donutChartOptions } from "layouts/sales/data/salesData";

function Sales() {
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

        {/* Top metrics */}
        <VuiBox mb={3}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6} xl={3}>
              <MiniStatisticsCard
                title={{ text: "leads", fontWeight: "regular" }}
                count="1,205"
                percentage={{ color: "success", text: "+12%" }}
                icon={{ color: "info", component: <FaUserPlus size="20px" color="white" /> }}
              />
            </Grid>
            <Grid item xs={12} md={6} xl={3}>
              <MiniStatisticsCard
                title={{ text: "booked calls" }}
                count="935"
                percentage={{ color: "success", text: "+5%" }}
                icon={{ color: "info", component: <FaCalendarAlt size="20px" color="white" /> }}
              />
            </Grid>
            <Grid item xs={12} md={6} xl={3}>
              <MiniStatisticsCard
                title={{ text: "rescheduled" }}
                count="53"
                percentage={{ color: "error", text: "+12%" }}
                icon={{ color: "info", component: <IoStatsChart size="20px" color="white" /> }}
              />
            </Grid>
            <Grid item xs={12} md={6} xl={3}>
              <MiniStatisticsCard
                title={{ text: "live calls" }}
                count="782"
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
                count="84.6%"
                percentage={{ color: "success", text: "+3%" }}
                icon={{ color: "info", component: <FaUserCheck size="20px" color="white" /> }}
              />
            </Grid>
            <Grid item xs={12} md={6} xl={3}>
              <MiniStatisticsCard
                title={{ text: "close rate" }}
                count="62.4%"
                percentage={{ color: "success", text: "+7%" }}
                icon={{ color: "info", component: <FaChartLine size="20px" color="white" /> }}
              />
            </Grid>
            <Grid item xs={12} md={6} xl={3}>
              <MiniStatisticsCard
                title={{ text: "AOV" }}
                count="$5,832"
                percentage={{ color: "success", text: "+12%" }}
                icon={{ color: "info", component: <FaChartPie size="20px" color="white" /> }}
              />
            </Grid>
            <Grid item xs={12} md={6} xl={3}>
              <MiniStatisticsCard
                title={{ text: "cash collected" }}
                count="$235,486"
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
                    <Chart
                      options={funnelChartOptions}
                      series={funnelChartData.series}
                      type="bar"
                      height="100%"
                      width="100%"
                    />
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
                    <Chart
                      options={donutChartOptions}
                      series={donutChartData}
                      type="donut"
                      height="100%"
                      width="100%"
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

export default Sales; 