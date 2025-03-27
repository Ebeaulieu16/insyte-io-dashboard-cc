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
import { Switch } from "@mui/material";
import Box from "@mui/material/Box";
import Divider from "@mui/material/Divider";

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
import { FaCreditCard, FaYoutube, FaCalendarAlt, FaLink } from "react-icons/fa";
import { IoCheckmarkCircle, IoCloseCircle } from "react-icons/io5";

// React Router
import { Link } from "react-router-dom";

function Integrations() {
  const { gradients } = colors;
  const { cardContent } = gradients;

  // Integration connections status (this would come from an API in a real app)
  const integrations = [
    {
      id: "stripe",
      name: "Stripe",
      description: "Payment processing for your courses and services",
      connected: true,
      connectedSince: "2023-05-15",
      icon: <FaCreditCard size="30px" color="white" />,
      status: "Active",
      color: "success"
    },
    {
      id: "youtube",
      name: "YouTube",
      description: "Connect your channel to track video performance",
      connected: true,
      connectedSince: "2023-06-22",
      icon: <FaYoutube size="30px" color="white" />,
      status: "Active",
      color: "success"
    },
    {
      id: "calendly",
      name: "Calendly",
      description: "Schedule calls and appointments automatically",
      connected: false,
      connectedSince: null,
      icon: <FaCalendarAlt size="30px" color="white" />,
      status: "Not Connected",
      color: "error"
    },
    {
      id: "calcom",
      name: "Cal.com",
      description: "Open-source alternative for scheduling meetings",
      connected: true,
      connectedSince: "2023-09-10",
      icon: <FaCalendarAlt size="30px" color="white" />,
      status: "Active",
      color: "success"
    }
  ];

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
        </VuiBox>

        {/* Integration Cards */}
        <Grid container spacing={3}>
          {integrations.map((integration) => (
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
                  
                  <VuiTypography variant="h5" color="white" fontWeight="bold" mb={1}>
                    {integration.name}
                  </VuiTypography>
                  
                  <VuiTypography variant="button" color="text" fontWeight="regular" mb="auto">
                    {integration.description}
                  </VuiTypography>
                  
                  <VuiBox mt={3} display="flex" alignItems="center">
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
                  
                  <VuiBox mt={2}>
                    <VuiButton
                      color={integration.connected ? "error" : "success"}
                      variant="contained"
                      fullWidth
                    >
                      {integration.connected ? "Disconnect" : "Connect"}
                    </VuiButton>
                  </VuiBox>
                </VuiBox>
              </Card>
            </Grid>
          ))}
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
      </VuiBox>
      <Footer />
    </DashboardLayout>
  );
}

export default Integrations; 