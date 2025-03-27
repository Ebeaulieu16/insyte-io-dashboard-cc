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

import { useState, useEffect } from "react";
import PropTypes from "prop-types";

// @mui material components
import Card from "@mui/material/Card";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableContainer from "@mui/material/TableContainer";
import TableRow from "@mui/material/TableRow";
import TableCell from "@mui/material/TableCell";
import Tooltip from "@mui/material/Tooltip";
import Icon from "@mui/material/Icon";

// Vision UI Dashboard React components
import VuiBox from "components/VuiBox";
import VuiTypography from "components/VuiTypography";
import VuiAvatar from "components/VuiAvatar";

// Third party components
import Chart from "react-apexcharts";

// Utilities
import { createMiniFunnelData, miniFunnelChartOptions, getHeatmapColor } from "layouts/youtube/data/youtubeData";

// React icons
import { FaYoutube } from "react-icons/fa";

function VideoTable({ videos }) {
  const [maxValues, setMaxValues] = useState({
    views: 0,
    likes: 0,
    comments: 0,
    clicks: 0,
    bookedCalls: 0,
    closedDeals: 0,
    revenue: 0
  });

  // Calculate maximum values for normalization
  useEffect(() => {
    if (videos && videos.length > 0) {
      const max = {
        views: Math.max(...videos.map(v => v.views)),
        likes: Math.max(...videos.map(v => v.likes)),
        comments: Math.max(...videos.map(v => v.comments)),
        clicks: Math.max(...videos.map(v => v.clicks)),
        bookedCalls: Math.max(...videos.map(v => v.bookedCalls)),
        closedDeals: Math.max(...videos.map(v => v.closedDeals)),
        revenue: Math.max(...videos.map(v => v.revenue))
      };
      setMaxValues(max);
    }
  }, [videos]);

  // Get normalized value for heatmap coloring (0-1 scale)
  const getNormalizedValue = (value, key) => {
    if (maxValues[key] === 0) return 0;
    return value / maxValues[key];
  };

  // Format numbers with commas
  const formatNumber = (num) => {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  };

  // Format currency
  const formatCurrency = (num) => {
    return "$" + formatNumber(num);
  };

  return (
    <Card>
      <VuiBox display="flex" justifyContent="space-between" alignItems="center" mb="22px" p={3}>
        <VuiBox>
          <VuiTypography variant="lg" color="white" fontWeight="bold">
            YouTube Video Performance
          </VuiTypography>
          <VuiTypography variant="button" color="text" fontWeight="regular">
            Heatmap shows relative performance across videos
          </VuiTypography>
        </VuiBox>
      </VuiBox>

      <VuiBox sx={{ height: "fit-content" }}>
        <TableContainer>
          <Table>
            <VuiBox component="thead">
              <TableRow>
                <TableCell style={{ padding: "0 16px" }}>
                  <VuiTypography color="text" variant="caption" fontWeight="medium">
                    VIDEO
                  </VuiTypography>
                </TableCell>
                <TableCell align="center">
                  <VuiTypography color="text" variant="caption" fontWeight="medium">
                    VIEWS
                  </VuiTypography>
                </TableCell>
                <TableCell align="center">
                  <VuiTypography color="text" variant="caption" fontWeight="medium">
                    LIKES
                  </VuiTypography>
                </TableCell>
                <TableCell align="center">
                  <VuiTypography color="text" variant="caption" fontWeight="medium">
                    COMMENTS
                  </VuiTypography>
                </TableCell>
                <TableCell align="center">
                  <VuiTypography color="text" variant="caption" fontWeight="medium">
                    AVG. VIEW TIME
                  </VuiTypography>
                </TableCell>
                <TableCell align="center">
                  <VuiTypography color="text" variant="caption" fontWeight="medium">
                    CLICKS
                  </VuiTypography>
                </TableCell>
                <TableCell align="center">
                  <VuiTypography color="text" variant="caption" fontWeight="medium">
                    BOOKED CALLS
                  </VuiTypography>
                </TableCell>
                <TableCell align="center">
                  <VuiTypography color="text" variant="caption" fontWeight="medium">
                    CLOSED DEALS
                  </VuiTypography>
                </TableCell>
                <TableCell align="center">
                  <VuiTypography color="text" variant="caption" fontWeight="medium">
                    REVENUE
                  </VuiTypography>
                </TableCell>
                <TableCell align="center">
                  <VuiTypography color="text" variant="caption" fontWeight="medium">
                    FUNNEL
                  </VuiTypography>
                </TableCell>
              </TableRow>
            </VuiBox>
            <TableBody>
              {videos.map((video) => {
                // Generate mini funnel data for this video
                const miniFunnelData = createMiniFunnelData(
                  video.clicks, 
                  video.bookedCalls, 
                  video.closedDeals
                );

                return (
                  <TableRow key={video.id}>
                    <TableCell>
                      <VuiBox display="flex" alignItems="center">
                        <VuiBox
                          bgColor="info"
                          width="40px"
                          height="40px"
                          borderRadius="10px"
                          display="flex"
                          justifyContent="center"
                          alignItems="center"
                          shadow="md"
                          mr={2}
                        >
                          <FaYoutube color="white" size="18px" />
                        </VuiBox>
                        <VuiTypography 
                          variant="button" 
                          color="white" 
                          fontWeight="medium" 
                          sx={{ 
                            maxWidth: "200px", 
                            overflow: "hidden", 
                            textOverflow: "ellipsis", 
                            whiteSpace: "nowrap" 
                          }}
                        >
                          {video.title}
                        </VuiTypography>
                      </VuiBox>
                    </TableCell>
                    <TableCell align="center">
                      <VuiBox 
                        py={1} 
                        px={2} 
                        borderRadius="10px" 
                        bgColor={getHeatmapColor(getNormalizedValue(video.views, "views"))}
                      >
                        <VuiTypography variant="button" color="white" fontWeight="medium">
                          {formatNumber(video.views)}
                        </VuiTypography>
                      </VuiBox>
                    </TableCell>
                    <TableCell align="center">
                      <VuiBox 
                        py={1} 
                        px={2} 
                        borderRadius="10px" 
                        bgColor={getHeatmapColor(getNormalizedValue(video.likes, "likes"))}
                      >
                        <VuiTypography variant="button" color="white" fontWeight="medium">
                          {formatNumber(video.likes)}
                        </VuiTypography>
                      </VuiBox>
                    </TableCell>
                    <TableCell align="center">
                      <VuiBox 
                        py={1} 
                        px={2} 
                        borderRadius="10px" 
                        bgColor={getHeatmapColor(getNormalizedValue(video.comments, "comments"))}
                      >
                        <VuiTypography variant="button" color="white" fontWeight="medium">
                          {formatNumber(video.comments)}
                        </VuiTypography>
                      </VuiBox>
                    </TableCell>
                    <TableCell align="center">
                      <VuiTypography variant="button" color="white" fontWeight="medium">
                        {video.avgViewDuration}
                      </VuiTypography>
                    </TableCell>
                    <TableCell align="center">
                      <VuiBox 
                        py={1} 
                        px={2} 
                        borderRadius="10px" 
                        bgColor={getHeatmapColor(getNormalizedValue(video.clicks, "clicks"))}
                      >
                        <VuiTypography variant="button" color="white" fontWeight="medium">
                          {formatNumber(video.clicks)}
                        </VuiTypography>
                      </VuiBox>
                    </TableCell>
                    <TableCell align="center">
                      <VuiBox 
                        py={1} 
                        px={2} 
                        borderRadius="10px" 
                        bgColor={getHeatmapColor(getNormalizedValue(video.bookedCalls, "bookedCalls"))}
                      >
                        <VuiTypography variant="button" color="white" fontWeight="medium">
                          {formatNumber(video.bookedCalls)}
                        </VuiTypography>
                      </VuiBox>
                    </TableCell>
                    <TableCell align="center">
                      <VuiBox 
                        py={1} 
                        px={2} 
                        borderRadius="10px" 
                        bgColor={getHeatmapColor(getNormalizedValue(video.closedDeals, "closedDeals"))}
                      >
                        <VuiTypography variant="button" color="white" fontWeight="medium">
                          {formatNumber(video.closedDeals)}
                        </VuiTypography>
                      </VuiBox>
                    </TableCell>
                    <TableCell align="center">
                      <VuiBox 
                        py={1} 
                        px={2} 
                        borderRadius="10px" 
                        bgColor={getHeatmapColor(getNormalizedValue(video.revenue, "revenue"))}
                      >
                        <VuiTypography variant="button" color="white" fontWeight="medium">
                          {formatCurrency(video.revenue)}
                        </VuiTypography>
                      </VuiBox>
                    </TableCell>
                    <TableCell align="center">
                      <VuiBox width="80px" height="50px">
                        <Chart
                          options={miniFunnelChartOptions}
                          series={miniFunnelData.series}
                          type="bar"
                          height="100%"
                          width="100%"
                        />
                      </VuiBox>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>
      </VuiBox>
    </Card>
  );
}

// Typechecking props for the VideoTable
VideoTable.propTypes = {
  videos: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.number.isRequired,
      title: PropTypes.string.isRequired,
      views: PropTypes.number.isRequired,
      likes: PropTypes.number.isRequired,
      comments: PropTypes.number.isRequired,
      avgViewDuration: PropTypes.string.isRequired,
      clicks: PropTypes.number.isRequired,
      bookedCalls: PropTypes.number.isRequired,
      closedDeals: PropTypes.number.isRequired,
      revenue: PropTypes.number.isRequired,
    })
  ).isRequired,
};

export default VideoTable; 