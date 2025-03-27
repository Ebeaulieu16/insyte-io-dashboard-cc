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

// YouTube video performance data
export const videoPerformanceData = [
  {
    id: 1,
    title: "Scale Your Agency with Systems & Automations",
    views: 32450,
    likes: 1850,
    comments: 324,
    avgViewDuration: "8:45",
    clicks: 423,
    bookedCalls: 86,
    closedDeals: 52,
    revenue: 302600,
  },
  {
    id: 2,
    title: "Content Marketing Secrets for 2023",
    views: 28750,
    likes: 1620,
    comments: 287,
    avgViewDuration: "7:32",
    clicks: 378,
    bookedCalls: 75,
    closedDeals: 43,
    revenue: 250600,
  },
  {
    id: 3,
    title: "LinkedIn Lead Gen Strategy Masterclass",
    views: 24320,
    likes: 1320,
    comments: 245,
    avgViewDuration: "9:15",
    clicks: 312,
    bookedCalls: 68,
    closedDeals: 38,
    revenue: 221400,
  },
  {
    id: 4,
    title: "SEO Tips for Digital Agencies",
    views: 21580,
    likes: 1150,
    comments: 198,
    avgViewDuration: "6:48",
    clicks: 287,
    bookedCalls: 55,
    closedDeals: 32,
    revenue: 186400,
  },
  {
    id: 5,
    title: "Email Marketing for Client Attraction",
    views: 18970,
    likes: 980,
    comments: 164,
    avgViewDuration: "8:12",
    clicks: 235,
    bookedCalls: 48,
    closedDeals: 28,
    revenue: 163100,
  },
  {
    id: 6,
    title: "How to Sign High-Ticket Clients",
    views: 15840,
    likes: 875,
    comments: 143,
    avgViewDuration: "7:55",
    clicks: 197,
    bookedCalls: 42,
    closedDeals: 25,
    revenue: 145500,
  },
  {
    id: 7,
    title: "Creating Viral Reels for Business",
    views: 12650,
    likes: 740,
    comments: 125,
    avgViewDuration: "5:35",
    clicks: 168,
    bookedCalls: 35,
    closedDeals: 18,
    revenue: 104800,
  },
  {
    id: 8,
    title: "YouTube Strategy for Service Providers",
    views: 9870,
    likes: 635,
    comments: 98,
    avgViewDuration: "8:20",
    clicks: 142,
    bookedCalls: 28,
    closedDeals: 15,
    revenue: 87300,
  },
  {
    id: 9,
    title: "Facebook Ads that Convert",
    views: 7540,
    likes: 520,
    comments: 82,
    avgViewDuration: "6:15",
    clicks: 105,
    bookedCalls: 21,
    closedDeals: 12,
    revenue: 69800,
  },
];

// Mini funnel chart options and data
export const miniFunnelChartOptions = {
  chart: {
    type: 'bar',
    sparkline: {
      enabled: true
    },
    toolbar: {
      show: false,
    },
  },
  colors: ['#0075FF', '#2CD9FF', '#16f9aa'],
  plotOptions: {
    bar: {
      horizontal: true,
      barHeight: '60%',
      borderRadius: 4,
      distributed: true,
      dataLabels: {
        position: 'top'
      }
    },
  },
  dataLabels: {
    enabled: false,
  },
  tooltip: {
    enabled: true,
    theme: "dark",
    x: {
      show: false
    },
    y: {
      formatter: function(val) {
        return val
      }
    }
  },
  grid: {
    show: false,
  },
  xaxis: {
    axisBorder: {
      show: false,
    },
    axisTicks: {
      show: false,
    },
    labels: {
      show: false
    }
  },
  yaxis: {
    labels: {
      show: false
    }
  }
};

// Function to generate mini funnel chart data for a video
export const createMiniFunnelData = (clicks, calls, deals) => {
  return {
    series: [{
      data: [deals, calls, clicks]
    }],
    labels: ['Deals', 'Calls', 'Clicks']
  };
};

// Generate a gradient color for heatmap from green to red based on normalized value (0-1)
export const getHeatmapColor = (normalizedValue) => {
  // Invert for color (0 = green, 1 = red)
  const value = 1 - normalizedValue;
  
  // Generate RGB values for a gradient from red to green
  const r = Math.floor(255 * (1 - value));
  const g = Math.floor(255 * value);
  
  return `rgba(${r}, ${g}, 50, 0.8)`;
}; 