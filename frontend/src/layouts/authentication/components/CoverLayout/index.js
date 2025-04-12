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
          backgroundColor: "#0A0A0A !important",
          backgroundImage: "none !important",
          position: "relative",
          zIndex: 1,
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
            <Card sx={{ backgroundColor: "#1A1A1A" }}>
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
                  <VuiTypography 
                    variant="h2" 
                    fontWeight="bold" 
                    sx={{
                      backgroundImage: "linear-gradient(120deg, rgba(255, 135, 0, 1) 50%, rgba(255, 78, 0, 1) 100%)",
                      WebkitBackgroundClip: "text",
                      WebkitTextFillColor: "transparent",
                      display: "inline-block"
                    }}
                  >
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