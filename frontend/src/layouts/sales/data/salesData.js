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

// Funnel chart data
export const funnelChartData = {
  categories: ['Leads', 'Booked Calls', 'Showed Up', 'Live Calls', 'Deals Closed'],
  series: [{
    name: 'Value',
    data: [1200, 935, 807, 782, 480]
  }]
};

export const funnelChartOptions = {
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
      borderRadius: 10,
      horizontal: true,
      distributed: true,
      barHeight: '80%',
      isFunnel: true,
    },
  },
  colors: [
    '#FF8700', // Leads (top) - lightest
    '#FF7D00', 
    '#FF7000',
    '#FF6300',
    '#FF4E00'  // Deals Closed (bottom) - darkest
  ],
  dataLabels: {
    enabled: true,
    formatter: function (val, opt) {
      return opt.w.globals.labels[opt.dataPointIndex] + ': ' + val
    },
    dropShadow: {
      enabled: true,
    },
    style: {
      colors: ['#fff'],
      fontSize: '14px',
      fontFamily: 'Plus Jakarta Display',
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
    categories: ['Leads', 'Booked Calls', 'Showed Up', 'Live Calls', 'Deals Closed'],
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

// Donut chart data
export const donutChartData = [62, 38];

export const donutChartOptions = {
  chart: {
    type: 'donut',
  },
  colors: ['#FF8700', '#FF4E00'], // Closed Deals (FF8700), Lost Opportunities (FF4E00)
  labels: ['Closed Deals', 'Lost Opportunities'],
  plotOptions: {
    pie: {
      donut: {
        size: '70%',
        labels: {
          show: true,
          name: {
            show: true,
            fontFamily: 'Plus Jakarta Display',
            fontSize: '16px',
            color: '#c8cfca',
          },
          value: {
            show: true,
            fontFamily: 'Plus Jakarta Display',
            fontSize: '20px',
            color: '#fff',
            formatter: function(val) {
              return val + '%';
            }
          },
          total: {
            show: true,
            color: '#c8cfca',
            fontSize: '14px',
            fontFamily: 'Plus Jakarta Display',
            label: 'Close Rate',
            formatter: function(w) {
              return w.globals.seriesTotals.reduce((a, b) => a + b, 0) / w.globals.series.length + '%';
            }
          }
        }
      }
    }
  },
  dataLabels: {
    enabled: false,
  },
  tooltip: {
    theme: "dark",
  },
  legend: {
    position: 'bottom',
    fontFamily: 'Plus Jakarta Display',
    fontSize: '14px',
    labels: {
      colors: "#c8cfca",
    },
  },
  responsive: [{
    breakpoint: 480,
    options: {
      chart: {
        width: 200
      },
      legend: {
        position: 'bottom'
      }
    }
  }]
}; 