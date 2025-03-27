/*!

=========================================================
* Vision UI Free React - v1.0.0
=========================================================

* Date Filter Component for consistent date filtering across pages
* Based on Vision UI Dashboard React design system

*/

import { useState, useEffect } from "react";
import PropTypes from "prop-types";

// @mui material components
import Card from "@mui/material/Card";
import Grid from "@mui/material/Grid";
import MenuItem from "@mui/material/MenuItem";
import Select from "@mui/material/Select";
import FormControl from "@mui/material/FormControl";
import Popover from "@mui/material/Popover";

// Vision UI Dashboard React components
import VuiBox from "components/VuiBox";
import VuiTypography from "components/VuiTypography";
import VuiButton from "components/VuiButton";

// React icons
import { IoCalendarOutline, IoChevronDown } from "react-icons/io5";

function DateFilter({ onChange }) {
  const [dateRange, setDateRange] = useState("30d");
  const [customRange, setCustomRange] = useState({
    startDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().substring(0, 10),
    endDate: new Date().toISOString().substring(0, 10),
  });
  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);

  // Handle date range change
  const handleDateRangeChange = (e) => {
    const newRange = e.target.value;
    setDateRange(newRange);
    
    if (newRange !== "custom") {
      // Calculate start and end dates based on selected range
      const endDate = new Date();
      let startDate;
  
      switch (newRange) {
        case "7d":
          startDate = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
          break;
        case "30d":
          startDate = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
          break;
        case "90d":
          startDate = new Date(Date.now() - 90 * 24 * 60 * 60 * 1000);
          break;
        default: // Default to 30 days
          startDate = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
      }
      
      onChange({
        range: newRange,
        startDate: startDate.toISOString().split("T")[0],
        endDate: endDate.toISOString().split("T")[0],
      });
    }
  };

  // Handle custom date range
  const handleCustomDateChange = (field, value) => {
    setCustomRange({
      ...customRange,
      [field]: value,
    });
  };

  // Apply custom date range
  const applyCustomRange = () => {
    setAnchorEl(null);
    onChange({
      range: "custom",
      startDate: customRange.startDate,
      endDate: customRange.endDate,
    });
  };

  // Toggle custom date popover
  const handleClick = (event) => {
    if (dateRange === "custom") {
      setAnchorEl(event.currentTarget);
    }
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  // Trigger initial date range
  useEffect(() => {
    onChange({
      range: dateRange,
      startDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split("T")[0], 
      endDate: new Date().toISOString().split("T")[0]
    });
  }, []);

  return (
    <VuiBox display="flex" alignItems="center">
      <IoCalendarOutline size="20px" color="white" style={{ marginRight: "10px" }} />
      <FormControl 
        variant="outlined" 
        size="small"
        sx={{
          minWidth: 120,
          "& .MuiOutlinedInput-root": {
            borderRadius: "10px",
            color: "white",
            backgroundColor: "rgba(26, 31, 55, 0.5)",
            border: "1px solid rgba(226, 232, 240, 0.3)",
            "& .MuiOutlinedInput-notchedOutline": {
              border: "none"
            },
          }
        }}
      >
        <Select
          value={dateRange}
          onChange={handleDateRangeChange}
          onClick={handleClick}
          displayEmpty
          inputProps={{ 'aria-label': 'Date range' }}
          IconComponent={() => <IoChevronDown size="18px" color="white" style={{ marginRight: "10px" }} />}
          MenuProps={{
            PaperProps: {
              sx: {
                backgroundColor: "rgba(26, 31, 55, 0.9)",
                color: "white",
                borderRadius: "10px",
                border: "1px solid rgba(226, 232, 240, 0.3)",
              }
            }
          }}
        >
          <MenuItem value="7d">Last 7 days</MenuItem>
          <MenuItem value="30d">Last 30 days</MenuItem>
          <MenuItem value="90d">Last 90 days</MenuItem>
          <MenuItem value="custom">Custom Range</MenuItem>
        </Select>
      </FormControl>
      
      <Popover
        open={open}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'left',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'left',
        }}
        PaperProps={{
          sx: {
            p: 2,
            backgroundColor: "rgba(26, 31, 55, 0.9)",
            color: "white",
            borderRadius: "10px",
            border: "1px solid rgba(226, 232, 240, 0.3)",
          }
        }}
      >
        <VuiBox p={2} width="250px">
          <VuiTypography variant="button" color="white" fontWeight="medium" mb={2}>
            Select Date Range
          </VuiTypography>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <VuiTypography variant="caption" color="text" fontWeight="regular">
                Start Date
              </VuiTypography>
              <VuiBox 
                component="input"
                type="date"
                value={customRange.startDate}
                onChange={(e) => handleCustomDateChange("startDate", e.target.value)}
                sx={{
                  width: "100%",
                  backgroundColor: "rgba(26, 31, 55, 0.5)",
                  border: "1px solid rgba(226, 232, 240, 0.3)",
                  borderRadius: "10px",
                  color: "white",
                  p: 1,
                  "&::-webkit-calendar-picker-indicator": {
                    filter: "invert(1)"
                  }
                }}
              />
            </Grid>
            <Grid item xs={12}>
              <VuiTypography variant="caption" color="text" fontWeight="regular">
                End Date
              </VuiTypography>
              <VuiBox 
                component="input"
                type="date"
                value={customRange.endDate}
                onChange={(e) => handleCustomDateChange("endDate", e.target.value)}
                sx={{
                  width: "100%",
                  backgroundColor: "rgba(26, 31, 55, 0.5)",
                  border: "1px solid rgba(226, 232, 240, 0.3)",
                  borderRadius: "10px",
                  color: "white",
                  p: 1,
                  "&::-webkit-calendar-picker-indicator": {
                    filter: "invert(1)"
                  }
                }}
              />
            </Grid>
            <Grid item xs={12}>
              <VuiButton 
                color="info" 
                variant="contained" 
                fullWidth
                onClick={applyCustomRange}
              >
                Apply
              </VuiButton>
            </Grid>
          </Grid>
        </VuiBox>
      </Popover>
    </VuiBox>
  );
}

// PropTypes validation
DateFilter.propTypes = {
  onChange: PropTypes.func.isRequired,
};

export default DateFilter; 