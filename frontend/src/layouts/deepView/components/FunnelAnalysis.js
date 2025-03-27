/*!

=========================================================
* Vision UI Free React - Funnel Analysis Component
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

function FunnelAnalysis({ data }) {
  const { info, success, primary, warning } = colors;
  
  // Calculate conversion rates
  const clickToBookRate = data.calls.booked > 0 && data.clicks > 0 
    ? ((data.calls.booked / data.clicks) * 100).toFixed(2)
    : 0;
    
  const bookToLiveRate = data.calls.live > 0 && data.calls.booked > 0
    ? ((data.calls.live / data.calls.booked) * 100).toFixed(2)
    : 0;
    
  const liveToClosedRate = data.deals.closed > 0 && data.calls.live > 0
    ? ((data.deals.closed / data.calls.live) * 100).toFixed(2)
    : 0;
    
  const overallConversionRate = data.deals.closed > 0 && data.clicks > 0
    ? ((data.deals.closed / data.clicks) * 100).toFixed(2)
    : 0;
  
  // Format currency
  const formatCurrency = (value) => {
    return `$${value.toLocaleString()}`;
  };
  
  // Format number with comma separators
  const formatNumber = (value) => {
    return value.toLocaleString();
  };
  
  // Funnel chart data
  const chartData = {
    series: [
      {
        name: "Value",
        data: [
          data.clicks,
          data.calls.booked,
          data.calls.live,
          data.deals.closed
        ]
      }
    ]
  };
  
  // Funnel chart options
  const chartOptions = {
    chart: {
      type: 'bar',
      height: 350,
      toolbar: {
        show: false,
      },
    },
    tooltip: {
      theme: "dark",
    },
    plotOptions: {
      bar: {
        borderRadius: 0,
        horizontal: true,
        distributed: true,
        barHeight: '80%',
        isFunnel: true,
      },
    },
    colors: [
      primary.main,
      info.main,
      warning.main,
      success.main,
    ],
    dataLabels: {
      enabled: true,
      formatter: function (val, opt) {
        return opt.w.globals.labels[opt.dataPointIndex] + ': ' + val.toLocaleString()
      },
      dropShadow: {
        enabled: true,
      },
      style: {
        colors: ['#fff'],
        fontSize: '14px',
        fontFamily: "'Plus Jakarta Display', sans-serif",
        fontWeight: 'bold',
      },
    },
    states: {
      hover: {
        filter: {
          type: 'darken',
          value: 0.15,
        }
      }
    },
    xaxis: {
      categories: ['Clicks', 'Booked Calls', 'Live Calls', 'Deals Closed'],
      labels: {
        style: {
          colors: "#c8cfca",
          fontSize: "12px",
        },
      },
    },
    yaxis: {
      labels: {
        style: {
          colors: "#c8cfca",
          fontSize: "12px",
        },
      },
    },
    grid: {
      borderColor: "#56577A",
    }
  };
  
  return (
    <Card>
      <VuiBox p={3}>
        <VuiBox mb={3}>
          <VuiTypography variant="h6" color="white" fontWeight="medium">
            Funnel Analysis
          </VuiTypography>
          <VuiTypography variant="button" color="text" fontWeight="regular">
            Conversion flow from clicks to closed deals
          </VuiTypography>
        </VuiBox>
        
        <Grid container spacing={3} mb={3}>
          <Grid item xs={12} md={3}>
            <VuiBox 
              bgcolor="rgba(0, 117, 255, 0.1)" 
              borderRadius="lg" 
              p={2} 
              textAlign="center"
              border="1px solid rgba(0, 117, 255, 0.3)"
            >
              <VuiTypography variant="button" color="text" fontWeight="regular">
                Click → Book
              </VuiTypography>
              <VuiTypography variant="h5" color="white" fontWeight="bold">
                {clickToBookRate}%
              </VuiTypography>
            </VuiBox>
          </Grid>
          <Grid item xs={12} md={3}>
            <VuiBox 
              bgcolor="rgba(44, 217, 255, 0.1)" 
              borderRadius="lg" 
              p={2} 
              textAlign="center"
              border="1px solid rgba(44, 217, 255, 0.3)"
            >
              <VuiTypography variant="button" color="text" fontWeight="regular">
                Book → Live
              </VuiTypography>
              <VuiTypography variant="h5" color="white" fontWeight="bold">
                {bookToLiveRate}%
              </VuiTypography>
            </VuiBox>
          </Grid>
          <Grid item xs={12} md={3}>
            <VuiBox 
              bgcolor="rgba(255, 178, 0, 0.1)" 
              borderRadius="lg" 
              p={2} 
              textAlign="center"
              border="1px solid rgba(255, 178, 0, 0.3)"
            >
              <VuiTypography variant="button" color="text" fontWeight="regular">
                Live → Closed
              </VuiTypography>
              <VuiTypography variant="h5" color="white" fontWeight="bold">
                {liveToClosedRate}%
              </VuiTypography>
            </VuiBox>
          </Grid>
          <Grid item xs={12} md={3}>
            <VuiBox 
              bgcolor="rgba(22, 249, 170, 0.1)" 
              borderRadius="lg" 
              p={2} 
              textAlign="center"
              border="1px solid rgba(22, 249, 170, 0.3)"
            >
              <VuiTypography variant="button" color="text" fontWeight="regular">
                Overall Conversion
              </VuiTypography>
              <VuiTypography variant="h5" color="success" fontWeight="bold">
                {overallConversionRate}%
              </VuiTypography>
            </VuiBox>
          </Grid>
        </Grid>
        
        <VuiBox height="350px">
          <ReactApexChart
            options={chartOptions}
            series={chartData.series}
            type="bar"
            height="100%"
            width="100%"
          />
        </VuiBox>
        
        <VuiBox mt={3} textAlign="right">
          <VuiTypography variant="button" color="success" fontWeight="bold">
            Revenue: {formatCurrency(data.deals.revenue)}
          </VuiTypography>
          <VuiTypography variant="button" color="text" fontWeight="regular" ml={1}>
            from {formatNumber(data.deals.closed)} closed deals
          </VuiTypography>
        </VuiBox>
      </VuiBox>
    </Card>
  );
}

// PropTypes validation
FunnelAnalysis.propTypes = {
  data: PropTypes.shape({
    clicks: PropTypes.number.isRequired,
    calls: PropTypes.shape({
      booked: PropTypes.number.isRequired,
      live: PropTypes.number.isRequired,
      no_show: PropTypes.number.isRequired,
      rescheduled: PropTypes.number.isRequired,
      list: PropTypes.array.isRequired,
    }).isRequired,
    deals: PropTypes.shape({
      closed: PropTypes.number.isRequired,
      revenue: PropTypes.number.isRequired,
    }).isRequired,
  }).isRequired,
};

export default FunnelAnalysis; 