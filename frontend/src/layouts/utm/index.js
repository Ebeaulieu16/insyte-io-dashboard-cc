/*!

=========================================================
* Vision UI Free React - UTM Link Generator
=========================================================

*/

// @mui material components
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import Icon from "@mui/material/Icon";
import Tooltip from "@mui/material/Tooltip";
import { useState } from "react";

// Vision UI Dashboard React components
import VuiBox from "components/VuiBox";
import VuiTypography from "components/VuiTypography";
import VuiButton from "components/VuiButton";

// Vision UI Dashboard React example components
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";

// Custom components
import UTMLinkGenerator from "layouts/utm/components/UTMLinkGenerator";
import UTMLinkTable from "layouts/utm/components/UTMLinkTable";
import DateFilter from "components/DateFilter";

function UTMGenerator() {
  const [dateRange, setDateRange] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);
  
  // Handle date filter changes
  const handleDateChange = (range) => {
    setDateRange(range);
  };
  
  // Handle link creation success - trigger table refresh
  const handleLinkCreated = () => {
    setRefreshKey(prevKey => prevKey + 1);
  };

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <VuiBox py={3}>
        {/* UTM Link Generator */}
        <VuiBox mb={3}>
          <Grid container spacing={3} justifyContent="center">
            <Grid item xs={12} lg={10}>
              <Card>
                <VuiBox display="flex" flexDirection="column" height="100%">
                  <VuiBox pt={3} px={3}>
                    <VuiTypography variant="lg" color="white" fontWeight="bold" mb="5px">
                      UTM Link Generator
                    </VuiTypography>
                    <VuiTypography variant="button" color="text" fontWeight="regular">
                      Create tracking links for your YouTube videos to monitor engagement and revenue
                    </VuiTypography>
                  </VuiBox>
                  <VuiBox p={3}>
                    <UTMLinkGenerator onSuccess={handleLinkCreated} />
                  </VuiBox>
                </VuiBox>
              </Card>
            </Grid>
          </Grid>
        </VuiBox>
        
        {/* UTM Links Table */}
        <VuiBox>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Card>
                <VuiBox display="flex" flexDirection="column" height="100%">
                  <VuiBox pt={3} px={3} display="flex" justifyContent="space-between" alignItems="center">
                    <VuiBox>
                      <VuiTypography variant="lg" color="white" fontWeight="bold" mb="5px">
                        Link Performance
                      </VuiTypography>
                      <VuiTypography variant="button" color="text" fontWeight="regular">
                        Track the performance of your UTM links
                      </VuiTypography>
                    </VuiBox>
                    <DateFilter onChange={handleDateChange} />
                  </VuiBox>
                  <VuiBox p={3}>
                    <UTMLinkTable dateRange={dateRange} key={refreshKey} />
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

export default UTMGenerator; 