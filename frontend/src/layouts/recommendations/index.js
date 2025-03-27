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

// Vision UI Dashboard React base styles
import typography from "assets/theme/base/typography";
import colors from "assets/theme/base/colors";

// React icons
import { IoRocketSharp, IoSparkles, IoStar } from "react-icons/io5";

function Recommendations() {
  const { gradients } = colors;
  const { cardContent } = gradients;

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <VuiBox py={3}>
        <VuiBox mb={3}>
          <VuiTypography variant="h4" color="white" fontWeight="bold">
            AI Recommendations & Insights
          </VuiTypography>
          <VuiTypography variant="button" color="text" fontWeight="regular">
            Data-driven insights to optimize your marketing and sales
          </VuiTypography>
        </VuiBox>

        {/* Coming Soon Card */}
        <Card sx={{ overflow: "hidden" }}>
          <VuiBox p={5} textAlign="center">
            <VuiBox 
              display="flex" 
              justifyContent="center" 
              alignItems="center" 
              bgColor="info" 
              width="80px" 
              height="80px" 
              borderRadius="lg" 
              shadow="md" 
              mb={3}
              mx="auto"
            >
              <IoRocketSharp color="white" size="36px" />
            </VuiBox>
            
            <VuiTypography variant="h3" color="white" fontWeight="bold" mb={2}>
              Coming Soon
            </VuiTypography>
            
            <VuiTypography variant="button" color="text" fontWeight="regular" mb={4} px={8} mx="auto" sx={{ maxWidth: "700px" }}>
              Our AI recommendation engine is in development. Soon, you'll receive personalized insights to boost your content, optimize your funnel, and increase your revenue.
            </VuiTypography>
            
            <Grid container spacing={3} justifyContent="center">
              <Grid item xs={12} md={4}>
                <Card sx={{ height: "100%", background: "linear-gradient(127.09deg, rgba(6, 11, 40, 0.94) 19.41%, rgba(10, 14, 35, 0.49) 76.65%)" }}>
                  <VuiBox p={3} textAlign="center">
                    <VuiBox
                      display="flex"
                      justifyContent="center"
                      alignItems="center"
                      bgColor="success"
                      width="50px"
                      height="50px"
                      borderRadius="lg"
                      shadow="md"
                      mb={3}
                      mx="auto"
                    >
                      <IoSparkles color="white" size="24px" />
                    </VuiBox>
                    
                    <VuiTypography variant="h5" color="white" fontWeight="bold" mb={1}>
                      Content Optimization
                    </VuiTypography>
                    
                    <VuiTypography variant="button" color="text" fontWeight="regular">
                      AI-powered suggestions to improve your YouTube content and maximize engagement
                    </VuiTypography>
                  </VuiBox>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={4}>
                <Card sx={{ height: "100%", background: "linear-gradient(127.09deg, rgba(6, 11, 40, 0.94) 19.41%, rgba(10, 14, 35, 0.49) 76.65%)" }}>
                  <VuiBox p={3} textAlign="center">
                    <VuiBox
                      display="flex"
                      justifyContent="center"
                      alignItems="center"
                      bgColor="info"
                      width="50px"
                      height="50px"
                      borderRadius="lg"
                      shadow="md"
                      mb={3}
                      mx="auto"
                    >
                      <IoStar color="white" size="24px" />
                    </VuiBox>
                    
                    <VuiTypography variant="h5" color="white" fontWeight="bold" mb={1}>
                      Funnel Optimization
                    </VuiTypography>
                    
                    <VuiTypography variant="button" color="text" fontWeight="regular">
                      Smart suggestions to improve conversion rates at each stage of your sales funnel
                    </VuiTypography>
                  </VuiBox>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={4}>
                <Card sx={{ height: "100%", background: "linear-gradient(127.09deg, rgba(6, 11, 40, 0.94) 19.41%, rgba(10, 14, 35, 0.49) 76.65%)" }}>
                  <VuiBox p={3} textAlign="center">
                    <VuiBox
                      display="flex"
                      justifyContent="center"
                      alignItems="center"
                      bgColor="warning"
                      width="50px"
                      height="50px"
                      borderRadius="lg"
                      shadow="md"
                      mb={3}
                      mx="auto"
                    >
                      <IoRocketSharp color="white" size="24px" />
                    </VuiBox>
                    
                    <VuiTypography variant="h5" color="white" fontWeight="bold" mb={1}>
                      Growth Opportunities
                    </VuiTypography>
                    
                    <VuiTypography variant="button" color="text" fontWeight="regular">
                      Personalized recommendations to scale your business based on your performance data
                    </VuiTypography>
                  </VuiBox>
                </Card>
              </Grid>
            </Grid>
            
            <VuiBox mt={5}>
              <VuiButton
                color="primary"
                variant="contained"
                sx={{ px: 4 }}
              >
                Join Waitlist
              </VuiButton>
            </VuiBox>
          </VuiBox>
        </Card>
      </VuiBox>
      <Footer />
    </DashboardLayout>
  );
}

export default Recommendations;