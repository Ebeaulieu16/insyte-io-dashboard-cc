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

// Line chart options and data
export const lineChartData = [
  {
    name: "Total Clicks",
    data: [210, 180, 260, 290, 270, 310, 240, 220, 320, 290, 350, 380],
  },
  {
    name: "Booked Calls",
    data: [80, 60, 90, 85, 75, 100, 70, 65, 95, 85, 110, 130],
  },
];

export const lineChartOptions = {
  chart: {
    toolbar: {
      show: false,
    },
  },
  tooltip: {
    theme: "dark",
  },
  dataLabels: {
    enabled: false,
  },
  stroke: {
    curve: "smooth",
  },
  xaxis: {
    type: "datetime",
    categories: [
      "Jan",
      "Feb",
      "Mar",
      "Apr",
      "May",
      "Jun",
      "Jul",
      "Aug",
      "Sep",
      "Oct",
      "Nov",
      "Dec",
    ],
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
    },
  },
  legend: {
    show: true,
    position: 'top',
    horizontalAlign: 'right',
    labels: {
      colors: "#c8cfca",
    },
  },
  grid: {
    strokeDashArray: 5,
    borderColor: "#56577A",
  },
  fill: {
    type: "gradient",
    gradient: {
      shade: "dark",
      type: "vertical",
      shadeIntensity: 0,
      gradientToColors: undefined,
      inverseColors: true,
      opacityFrom: 0.8,
      opacityTo: 0,
      stops: [],
    },
    colors: ["#0075FF", "#2CD9FF"],
  },
  colors: ["#0075FF", "#2CD9FF"],
};

// Revenue per YouTube video bar chart data
export const revenueBarChartData = [
  {
    name: "Revenue",
    data: [4200, 3800, 3200, 2800, 2400, 1900, 1500, 1200, 900],
  },
];

export const revenueBarChartOptions = {
  chart: {
    toolbar: {
      show: false,
    },
  },
  tooltip: {
    style: {
      fontSize: "10px",
      fontFamily: "Plus Jakarta Display",
    },
    onDatasetHover: {
      style: {
        fontSize: "10px",
        fontFamily: "Plus Jakarta Display",
      },
    },
    theme: "dark",
  },
  xaxis: {
    categories: [
      "Scale Your Agency", 
      "Content Secrets", 
      "LinkedIn Mastery", 
      "SEO Tips", 
      "Email Marketing", 
      "Client Attraction", 
      "Viral Reels", 
      "YouTube Strategy",
      "Facebook Ads"
    ],
    show: true,
    labels: {
      show: true,
      style: {
        colors: "#fff",
        fontSize: "10px",
      },
      rotate: -45,
      trim: true,
      maxHeight: 120,
    },
    axisBorder: {
      show: false,
    },
    axisTicks: {
      show: false,
    },
  },
  yaxis: {
    show: true,
    color: "#fff",
    labels: {
      show: true,
      style: {
        colors: "#fff",
        fontSize: "10px",
        fontFamily: "Plus Jakarta Display",
      },
      formatter: (value) => `$${value}`
    },
  },
  grid: {
    show: false,
  },
  fill: {
    colors: "#fff",
  },
  dataLabels: {
    enabled: false,
  },
  plotOptions: {
    bar: {
      borderRadius: 8,
      columnWidth: "12px",
    },
  },
  responsive: [
    {
      breakpoint: 768,
      options: {
        plotOptions: {
          bar: {
            borderRadius: 0,
          },
        },
      },
    },
  ],
}; 