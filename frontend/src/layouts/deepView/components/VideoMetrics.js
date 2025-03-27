/*!

=========================================================
* Vision UI Free React - Video Metrics Component
=========================================================

*/

import PropTypes from "prop-types";

// @mui material components
import Card from "@mui/material/Card";
import Grid from "@mui/material/Grid";
import Stack from "@mui/material/Stack";
import Divider from "@mui/material/Divider";
import Icon from "@mui/material/Icon";

// Vision UI Dashboard React components
import VuiBox from "components/VuiBox";
import VuiTypography from "components/VuiTypography";

// Icons
import { BsPlayCircleFill } from "react-icons/bs";
import { IoMdTime } from "react-icons/io";
import { FaThumbsUp, FaComment, FaShare, FaUserFriends } from "react-icons/fa";
import { BiTargetLock } from "react-icons/bi";

function VideoMetrics({ videoData, isLoading }) {
  // Format numbers (e.g., 1000 to 1K)
  const formatNumber = (num) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + "M";
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + "K";
    } else {
      return num;
    }
  };
  
  // Format watch time from seconds to hours and minutes
  const formatWatchTime = (seconds) => {
    if (!seconds) return "0";
    
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (hours === 0) {
      return `${minutes} min`;
    } else {
      return `${hours} hr ${minutes} min`;
    }
  };
  
  // Format percentage
  const formatPercentage = (value) => {
    return `${(value * 100).toFixed(1)}%`;
  };
  
  // Check if video data exists
  const hasVideoData = videoData && Object.keys(videoData).length > 0;
  
  // Stat items for the YouTube metrics
  const statItems = [
    {
      icon: <BsPlayCircleFill size="20px" color="#FFF" />,
      label: "Views",
      value: hasVideoData ? formatNumber(videoData.views) : "-",
    },
    {
      icon: <IoMdTime size="20px" color="#FFF" />,
      label: "Watch Time",
      value: hasVideoData ? formatWatchTime(videoData.watch_time_seconds) : "-",
    },
    {
      icon: <FaThumbsUp size="20px" color="#FFF" />,
      label: "Likes",
      value: hasVideoData ? formatNumber(videoData.likes) : "-",
    },
    {
      icon: <FaComment size="20px" color="#FFF" />,
      label: "Comments",
      value: hasVideoData ? formatNumber(videoData.comments) : "-",
    },
    {
      icon: <FaShare size="20px" color="#FFF" />,
      label: "Shares",
      value: hasVideoData ? formatNumber(videoData.shares) : "-",
    },
    {
      icon: <FaUserFriends size="20px" color="#FFF" />,
      label: "Subscribers",
      value: hasVideoData ? formatNumber(videoData.new_subscribers) : "-",
    },
  ];
  
  // Conversion metrics
  const conversionMetrics = [
    {
      icon: <BiTargetLock size="20px" color="info" />,
      label: "Click-Through Rate",
      value: hasVideoData ? formatPercentage(videoData.ctr) : "-",
    },
    {
      icon: <Icon>call</Icon>,
      label: "Call Bookings",
      value: hasVideoData ? formatNumber(videoData.leads_generated) : "-",
    },
    {
      icon: <Icon>attach_money</Icon>,
      label: "Revenue Generated",
      value: hasVideoData ? `$${videoData.revenue.toLocaleString()}` : "-",
    },
  ];
  
  return (
    <Card>
      <VuiBox p={3}>
        <VuiBox mb={3}>
          <VuiTypography variant="h6" color="white" fontWeight="medium">
            YouTube Analytics
          </VuiTypography>
          <VuiTypography variant="button" color="text" fontWeight="regular">
            {hasVideoData ? videoData.title : "No video data available"}
          </VuiTypography>
        </VuiBox>
        
        {isLoading ? (
          <VuiBox textAlign="center" py={5}>
            <VuiTypography variant="button" color="text" fontWeight="regular">
              Loading video data...
            </VuiTypography>
          </VuiBox>
        ) : !hasVideoData ? (
          <VuiBox textAlign="center" py={5}>
            <VuiTypography variant="button" color="text" fontWeight="regular">
              No YouTube video associated with this UTM link
            </VuiTypography>
          </VuiBox>
        ) : (
          <>
            {/* Video thumbnail and embed */}
            <VuiBox mb={3}>
              <Grid container spacing={3} alignItems="center">
                <Grid item xs={12} md={4}>
                  <VuiBox
                    component="img"
                    src={videoData.thumbnail_url}
                    alt={videoData.title}
                    borderRadius="lg"
                    shadow="md"
                    width="100%"
                    height="auto"
                  />
                </Grid>
                <Grid item xs={12} md={8}>
                  <VuiBox
                    height="100%"
                    display="flex"
                    flexDirection="column"
                    justifyContent="space-between"
                  >
                    <VuiTypography
                      variant="body2"
                      color="white"
                      fontWeight="regular"
                      mb={2}
                      sx={{
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        display: "-webkit-box",
                        WebkitLineClamp: 3,
                        WebkitBoxOrient: "vertical",
                      }}
                    >
                      {videoData.description}
                    </VuiTypography>
                    <VuiBox display="flex" flexWrap="wrap" gap={2}>
                      <VuiBox
                        bgcolor="rgba(0, 117, 255, 0.1)"
                        borderRadius="lg"
                        p={1}
                        pl={2}
                        pr={2}
                        border="1px solid rgba(0, 117, 255, 0.3)"
                      >
                        <VuiTypography
                          variant="caption"
                          color="info"
                          fontWeight="medium"
                        >
                          Duration: {formatWatchTime(videoData.duration_seconds)}
                        </VuiTypography>
                      </VuiBox>
                      <VuiBox
                        bgcolor="rgba(22, 249, 170, 0.1)"
                        borderRadius="lg"
                        p={1}
                        pl={2}
                        pr={2}
                        border="1px solid rgba(22, 249, 170, 0.3)"
                      >
                        <VuiTypography
                          variant="caption"
                          color="success"
                          fontWeight="medium"
                        >
                          Published: {new Date(videoData.published_at).toLocaleDateString()}
                        </VuiTypography>
                      </VuiBox>
                    </VuiBox>
                  </VuiBox>
                </Grid>
              </Grid>
            </VuiBox>
            
            <Divider light />
            
            {/* Video Stats */}
            <VuiBox mt={3} mb={3}>
              <Grid container spacing={3}>
                {statItems.map((stat, index) => (
                  <Grid item xs={6} md={4} key={`stat-${index}`}>
                    <VuiBox
                      display="flex"
                      alignItems="center"
                      mb={index >= statItems.length - 3 ? 0 : 2}
                    >
                      <VuiBox
                        display="flex"
                        justifyContent="center"
                        alignItems="center"
                        width="45px"
                        height="45px"
                        borderRadius="lg"
                        bgcolor="rgba(0, 117, 255, 0.1)"
                        mr={2}
                      >
                        {stat.icon}
                      </VuiBox>
                      <VuiBox>
                        <VuiTypography
                          variant="button"
                          color="text"
                          fontWeight="regular"
                        >
                          {stat.label}
                        </VuiTypography>
                        <VuiTypography
                          variant="h5"
                          color="white"
                          fontWeight="bold"
                        >
                          {stat.value}
                        </VuiTypography>
                      </VuiBox>
                    </VuiBox>
                  </Grid>
                ))}
              </Grid>
            </VuiBox>
            
            <Divider light />
            
            {/* Conversion Metrics */}
            <VuiBox mt={3}>
              <VuiTypography
                variant="h6"
                color="white"
                fontWeight="medium"
                mb={2}
              >
                Conversion Metrics
              </VuiTypography>
              
              <Stack direction="row" spacing={2} sx={{ overflowX: "auto", pb: 1 }}>
                {conversionMetrics.map((metric, index) => (
                  <VuiBox
                    key={`conversion-${index}`}
                    bgcolor="#0f1535"
                    p={2}
                    borderRadius="lg"
                    minWidth="150px"
                    sx={{ flexShrink: 0 }}
                  >
                    <VuiBox
                      display="flex"
                      alignItems="center"
                      mb={1}
                    >
                      <VuiBox
                        display="flex"
                        justifyContent="center"
                        alignItems="center"
                        width="32px"
                        height="32px"
                        borderRadius="lg"
                        bgcolor={
                          index === 0
                            ? "rgba(0, 117, 255, 0.1)"
                            : index === 1
                            ? "rgba(255, 178, 0, 0.1)"
                            : "rgba(22, 249, 170, 0.1)"
                        }
                        mr={1}
                        color={
                          index === 0
                            ? "info"
                            : index === 1
                            ? "warning"
                            : "success"
                        }
                      >
                        {metric.icon}
                      </VuiBox>
                      <VuiTypography
                        variant="button"
                        color="text"
                        fontWeight="regular"
                      >
                        {metric.label}
                      </VuiTypography>
                    </VuiBox>
                    <VuiTypography
                      variant="h5"
                      color={
                        index === 0
                          ? "info"
                          : index === 1
                          ? "warning"
                          : "success"
                      }
                      fontWeight="bold"
                    >
                      {metric.value}
                    </VuiTypography>
                  </VuiBox>
                ))}
              </Stack>
            </VuiBox>
          </>
        )}
      </VuiBox>
    </Card>
  );
}

// PropTypes validation
VideoMetrics.propTypes = {
  videoData: PropTypes.shape({
    video_id: PropTypes.string,
    title: PropTypes.string,
    description: PropTypes.string,
    thumbnail_url: PropTypes.string,
    views: PropTypes.number,
    watch_time_seconds: PropTypes.number,
    likes: PropTypes.number,
    comments: PropTypes.number,
    shares: PropTypes.number,
    duration_seconds: PropTypes.number,
    published_at: PropTypes.string,
    new_subscribers: PropTypes.number,
    ctr: PropTypes.number,
    leads_generated: PropTypes.number,
    revenue: PropTypes.number,
  }),
  isLoading: PropTypes.bool,
};

// Default props
VideoMetrics.defaultProps = {
  videoData: null,
  isLoading: false,
};

export default VideoMetrics; 