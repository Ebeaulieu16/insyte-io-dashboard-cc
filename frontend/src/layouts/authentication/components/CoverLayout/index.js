import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import PropTypes from "prop-types";
import { Card, Grid } from "@mui/material";
import VuiBox from "components/VuiBox";
import VuiTypography from "components/VuiTypography";
import VuiButton from "components/VuiButton";
import DefaultNavbar from "examples/Navbars/DefaultNavbar";
import PageLayout from "examples/LayoutContainers/PageLayout";

function CoverLayout({ color, header, title, description, image, button, children }) {
  const [windowWidth, setWindowWidth] = useState(window.innerWidth);

  useEffect(() => {
    const handleResize = () => setWindowWidth(window.innerWidth);
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  return (
    <PageLayout>
      <VuiBox
        width="100%"
        height="100vh"
        display="flex"
        justifyContent="center"
        alignItems="center"
        sx={{
          backgroundColor: "#0f1535",
          backgroundImage: "linear-gradient(310deg, #141727 0%, #3a416f 100%)",
        }}
      >
        <Grid 
          container 
          spacing={3} 
          justifyContent="center" 
          alignItems="center" 
          sx={{ height: "100%" }}
        >
          <Grid item xs={11} sm={9} md={7} lg={5} xl={4}>
            <Card>
              <VuiBox
                display="flex"
                flexDirection="column"
                justifyContent="center"
                alignItems="center"
                pt={4}
                pb={4}
                px={4}
              >
                {header}
                <VuiBox mt={2} mb={2} textAlign="center">
                  <VuiTypography variant="h2" fontWeight="bold" color="white" textGradient>
                    {title}
                  </VuiTypography>
                  <VuiTypography variant="body2" color="text" mb={2}>
                    {description}
                  </VuiTypography>
                </VuiBox>
                {children}
              </VuiBox>
            </Card>
          </Grid>
        </Grid>
      </VuiBox>
    </PageLayout>
  );
}

// Setting default values for the props of CoverLayout
CoverLayout.defaultProps = {
  header: "",
  title: "",
  description: "",
  color: "info",
  button: { color: "info" },
};

// Typechecking props for the CoverLayout
CoverLayout.propTypes = {
  color: PropTypes.oneOf([
    "primary",
    "secondary",
    "info",
    "success",
    "warning",
    "error",
    "dark",
    "light",
  ]),
  header: PropTypes.node,
  title: PropTypes.string,
  description: PropTypes.string,
  image: PropTypes.string,
  button: PropTypes.object,
  children: PropTypes.node.isRequired,
};

export default CoverLayout; 