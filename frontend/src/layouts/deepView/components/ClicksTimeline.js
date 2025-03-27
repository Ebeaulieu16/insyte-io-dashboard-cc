/*!

=========================================================
* Vision UI Free React - Clicks Timeline Component
=========================================================

*/

import { useState, useEffect } from "react";
import PropTypes from "prop-types";
import ReactApexChart from "react-apexcharts";

// @mui material components
import Card from "@mui/material/Card";
import Grid from "@mui/material/Grid";

// Vision UI Dashboard React components
import VuiBox from "components/VuiBox";
import VuiTypography from "components/VuiTypography";

// Vision UI Dashboard theme styles
import colors from "assets/theme/base/colors";

function ClicksTimeline({ clicksData }) {
  const { info, gradients } = colors;
  const { cardContent } = gradients;
  
  // Format date for display
  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString("en-US", { month: 'short', day: 'numeric' });
  };
  
  // Prepare chart data
  const chartData = {
    series: [
      {
        name: "Clicks",
        data: clicksData.map(item => item.count),
      },
    ],
    categories: clicksData.map(item => formatDate(item.date)),
  };
  
  // Chart options
  const chartOptions = {
    chart: {
      type: "line",
      height: 350,
      toolbar: {
        show: false,
      },
      animations: {
        enabled: true,
        easing: 'easeinout',
        speed: 800,
        animateGradually: {
          enabled: true,
          delay: 150
        },
        dynamicAnimation: {
          enabled: true,
          speed: 350
        }
      }
    },
    tooltip: {
      theme: "dark",
      y: {
        formatter: (value) => {
          return value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
        }
      }
    },
    dataLabels: {
      enabled: false,
    },
    stroke: {
      width: 3,
      curve: 'smooth',
      colors: [info.main],
    },
    grid: {
      borderColor: "#56577A",
      strokeDashArray: 5,
      xaxis: {
        lines: {
          show: true,
        },
      },
      yaxis: {
        lines: {
          show: true,
        },
      },
    },
    fill: {
      type: "gradient",
      gradient: {
        shade: "dark",
        type: "horizontal",
        shadeIntensity: 0.5,
        gradientToColors: [info.state],
        inverseColors: true,
        opacityFrom: 1,
        opacityTo: 0.75,
        stops: [0, 100]
      },
    },
    xaxis: {
      categories: chartData.categories,
      labels: {
        style: {
          colors: "#c8cfca",
          fontSize: "10px",
        },
      },
      axisBorder: {
        show: false,
      },
      axisTicks: {
        show: false,
      },
    },
    yaxis: {
      labels: {
        style: {
          colors: "#c8cfca",
          fontSize: "10px",
        },
        formatter: (value) => { 
          return value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
        }
      },
    },
    markers: {
      size: 5,
      colors: info.main,
      strokeColors: "#1A1E2D",
      strokeWidth: 2,
      hover: {
        size: 7,
      }
    },
  };
  
  // If no data, show empty state
  if (!clicksData || clicksData.length === 0) {
    return (
      <Card>
        <VuiBox p={3}>
          <VuiTypography variant="h6" color="white" fontWeight="medium" mb={2}>
            Clicks Timeline
          </VuiTypography>
          <VuiBox height="300px" display="flex" justifyContent="center" alignItems="center">
            <VuiTypography variant="button" color="text">
              No click data available for this time period
            </VuiTypography>
          </VuiBox>
        </VuiBox>
      </Card>
    );
  }
  
  return (
    <Card>
      <VuiBox p={3}>
        <VuiBox mb={3}>
          <VuiTypography variant="h6" color="white" fontWeight="medium">
            Clicks Timeline
          </VuiTypography>
          <VuiBox display="flex" alignItems="center">
            <VuiBox mr={1}>
              <VuiTypography variant="button" color="success" fontWeight="bold">
                {clicksData.reduce((sum, item) => sum + item.count, 0)} total clicks
              </VuiTypography>
            </VuiBox>
            <VuiTypography variant="button" color="text" fontWeight="regular">
              over time
            </VuiTypography>
          </VuiBox>
        </VuiBox>
        <VuiBox height="300px">
          <ReactApexChart
            options={chartOptions}
            series={chartData.series}
            type="line"
            height="100%"
            width="100%"
          />
        </VuiBox>
      </VuiBox>
    </Card>
  );
}

// PropTypes validation
ClicksTimeline.propTypes = {
  clicksData: PropTypes.arrayOf(
    PropTypes.shape({
      date: PropTypes.string.isRequired,
      count: PropTypes.number.isRequired,
    })
  ).isRequired,
};

export default ClicksTimeline; 