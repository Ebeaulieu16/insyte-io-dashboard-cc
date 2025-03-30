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
  const { info, success, primary, warning, dark } = colors;
  
  // Calculate conversion rates
  const viewToClickRate = data.views > 0 && data.clicks > 0 
    ? ((data.clicks / data.views) * 100).toFixed(2)
    : 0;
    
  const clickToBookRate = data.calls.booked > 0 && data.clicks > 0 
    ? ((data.calls.booked / data.clicks) * 100).toFixed(2)
    : 0;
    
  const bookToCompleteRate = data.calls.completed > 0 && data.calls.booked > 0
    ? ((data.calls.completed / data.calls.booked) * 100).toFixed(2)
    : 0;
    
  const completeToClosedRate = data.deals.closed > 0 && data.calls.completed > 0
    ? ((data.deals.closed / data.calls.completed) * 100).toFixed(2)
    : 0;
    
  const overallConversionRate = data.deals.closed > 0 && data.views > 0
    ? ((data.deals.closed / data.views) * 100).toFixed(2)
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
          data.views || 0,
          data.clicks || 0,
          data.calls.booked || 0,
          data.calls.completed || 0,
          data.deals.closed || 0
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
      dark.main,
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
      categories: ['Views', 'Link Clicks', 'Calls Booked', 'Calls Completed', 'Deals Closed'],
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
            Conversion flow from views to closed deals
          </VuiTypography>
        </VuiBox>
        
        <Grid container spacing={3} mb={3}>
          <Grid item xs={12} md={6} xl={3}>
            <VuiBox 
              bgcolor="rgba(0, 0, 0, 0.1)" 
              borderRadius="lg" 
              p={2} 
              textAlign="center"
              border="1px solid rgba(85, 85, 85, 0.3)"
            >
              <VuiTypography variant="button" color="text" fontWeight="regular">
                View → Click
              </VuiTypography>
              <VuiTypography variant="h5" color="white" fontWeight="bold">
                {viewToClickRate}%
              </VuiTypography>
            </VuiBox>
          </Grid>
          <Grid item xs={12} md={6} xl={3}>
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
          <Grid item xs={12} md={6} xl={3}>
            <VuiBox 
              bgcolor="rgba(44, 217, 255, 0.1)" 
              borderRadius="lg" 
              p={2} 
              textAlign="center"
              border="1px solid rgba(44, 217, 255, 0.3)"
            >
              <VuiTypography variant="button" color="text" fontWeight="regular">
                Book → Complete
              </VuiTypography>
              <VuiTypography variant="h5" color="white" fontWeight="bold">
                {bookToCompleteRate}%
              </VuiTypography>
            </VuiBox>
          </Grid>
          <Grid item xs={12} md={6} xl={3}>
            <VuiBox 
              bgcolor="rgba(255, 178, 0, 0.1)" 
              borderRadius="lg" 
              p={2} 
              textAlign="center"
              border="1px solid rgba(255, 178, 0, 0.3)"
            >
              <VuiTypography variant="button" color="text" fontWeight="regular">
                Complete → Close
              </VuiTypography>
              <VuiTypography variant="h5" color="white" fontWeight="bold">
                {completeToClosedRate}%
              </VuiTypography>
            </VuiBox>
          </Grid>
        </Grid>
        
        <VuiBox mt={2} mb={2} textAlign="center">
          <VuiBox 
            bgcolor="rgba(22, 249, 170, 0.1)" 
            borderRadius="lg" 
            p={2}
            display="inline-block" 
            minWidth="200px"
            border="1px solid rgba(22, 249, 170, 0.3)"
          >
            <VuiTypography variant="button" color="text" fontWeight="regular">
              Overall Conversion (View → Close)
            </VuiTypography>
            <VuiTypography variant="h5" color="success" fontWeight="bold">
              {overallConversionRate}%
            </VuiTypography>
          </VuiBox>
        </VuiBox>
        
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
    views: PropTypes.number,
    clicks: PropTypes.number.isRequired,
    calls: PropTypes.shape({
      booked: PropTypes.number.isRequired,
      completed: PropTypes.number,
      no_show: PropTypes.number,
    }).isRequired,
    deals: PropTypes.shape({
      closed: PropTypes.number.isRequired,
      revenue: PropTypes.number.isRequired,
    }).isRequired,
  }).isRequired,
};

export default FunnelAnalysis; 