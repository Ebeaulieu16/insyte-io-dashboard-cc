/*!

=========================================================
* Vision UI Free React - Calls List Component
=========================================================

*/

import { useState } from "react";
import PropTypes from "prop-types";

// @mui material components
import Card from "@mui/material/Card";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import TableCell from "@mui/material/TableCell";
import Chip from "@mui/material/Chip";
import Icon from "@mui/material/Icon";
import Pagination from "@mui/material/Pagination";

// Vision UI Dashboard React components
import VuiBox from "components/VuiBox";
import VuiTypography from "components/VuiTypography";
import VuiSelect from "components/VuiSelect";

function CallsList({ calls }) {
  const [page, setPage] = useState(1);
  const [filter, setFilter] = useState("all");
  const rowsPerPage = 5;
  
  // Format date to readable string
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };
  
  // Format duration from minutes to hours and minutes
  const formatDuration = (minutes) => {
    if (!minutes) return "N/A";
    
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    
    if (hours === 0) {
      return `${mins} min`;
    } else if (mins === 0) {
      return `${hours} hr`;
    } else {
      return `${hours} hr ${mins} min`;
    }
  };
  
  // Get status color based on call status
  const getStatusColor = (status) => {
    switch (status.toLowerCase()) {
      case "booked":
        return "info";
      case "pending":
        return "secondary";
      case "confirmed":
        return "warning";
      case "completed":
        return "success";
      case "cancelled":
        return "error";
      case "no_show":
        return "error";
      case "rescheduled":
        return "primary";
      default:
        return "secondary";
    }
  };
  
  // Format status text with proper capitalization
  const formatStatus = (status) => {
    if (status === "no_show") return "No Show";
    if (status === "completed") return "Completed";
    if (status === "cancelled") return "Cancelled";
    if (status === "confirmed") return "Confirmed";
    if (status === "pending") return "Pending";
    if (status === "rescheduled") return "Rescheduled";
    return status.charAt(0).toUpperCase() + status.slice(1);
  };
  
  // Filter calls based on selected filter
  const filteredCalls = filter === "all" 
    ? calls 
    : calls.filter(call => call.status.toLowerCase() === filter.toLowerCase());
  
  // Calculate pagination
  const totalPages = Math.ceil(filteredCalls.length / rowsPerPage);
  const paginatedCalls = filteredCalls.slice(
    (page - 1) * rowsPerPage,
    page * rowsPerPage
  );
  
  // Handle pagination change
  const handlePageChange = (event, value) => {
    setPage(value);
  };
  
  // Handle filter change
  const handleFilterChange = (event) => {
    setFilter(event.target.value);
    setPage(1); // Reset to first page when filter changes
  };
  
  // Status filter options
  const filterOptions = [
    { value: "all", label: "All Calls" },
    { value: "booked", label: "Booked" },
    { value: "pending", label: "Pending" },
    { value: "confirmed", label: "Confirmed" },
    { value: "completed", label: "Completed" },
    { value: "cancelled", label: "Cancelled" },
    { value: "no_show", label: "No Show" },
    { value: "rescheduled", label: "Rescheduled" },
  ];
  
  return (
    <Card>
      <VuiBox display="flex" justifyContent="space-between" alignItems="center" p={3}>
        <VuiBox>
          <VuiTypography variant="h6" color="white" fontWeight="medium">
            Call History
          </VuiTypography>
          <VuiTypography variant="button" color="text" fontWeight="regular">
            {calls.length} calls associated with this UTM link
          </VuiTypography>
        </VuiBox>
        
        <VuiBox width="10rem">
          <VuiSelect
            defaultValue={filterOptions[0]}
            options={filterOptions}
            onChange={handleFilterChange}
          />
        </VuiBox>
      </VuiBox>
      
      <VuiBox
        sx={{
          "& th": {
            borderBottom: ({ borders: { borderWidth, borderColor } }) =>
              `${borderWidth[1]} solid ${borderColor}`,
          },
          "& .MuiTableRow-root:not(:last-child)": {
            "& td": {
              borderBottom: ({ borders: { borderWidth, borderColor } }) =>
                `${borderWidth[1]} solid ${borderColor}`,
            },
          },
        }}
      >
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>
                  <VuiTypography
                    variant="caption"
                    color="white"
                    fontWeight="medium"
                    textTransform="uppercase"
                  >
                    Date
                  </VuiTypography>
                </TableCell>
                <TableCell>
                  <VuiTypography
                    variant="caption"
                    color="white"
                    fontWeight="medium"
                    textTransform="uppercase"
                  >
                    Status
                  </VuiTypography>
                </TableCell>
                <TableCell>
                  <VuiTypography
                    variant="caption"
                    color="white"
                    fontWeight="medium"
                    textTransform="uppercase"
                  >
                    Client
                  </VuiTypography>
                </TableCell>
                <TableCell>
                  <VuiTypography
                    variant="caption"
                    color="white"
                    fontWeight="medium"
                    textTransform="uppercase"
                  >
                    Duration
                  </VuiTypography>
                </TableCell>
                <TableCell>
                  <VuiTypography
                    variant="caption"
                    color="white"
                    fontWeight="medium"
                    textTransform="uppercase"
                  >
                    Revenue
                  </VuiTypography>
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {paginatedCalls.length > 0 ? (
                paginatedCalls.map((call, index) => (
                  <TableRow key={`call-${index}`}>
                    <TableCell>
                      <VuiTypography variant="body2" color="white">
                        {formatDate(call.date)}
                      </VuiTypography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={formatStatus(call.status)}
                        color={getStatusColor(call.status)}
                        size="small"
                        sx={{
                          fontSize: "0.75rem",
                          fontWeight: "600",
                          borderRadius: "8px",
                        }}
                      />
                    </TableCell>
                    <TableCell>
                      <VuiTypography variant="body2" color="white">
                        {call.client_name || "Anonymous"}
                      </VuiTypography>
                      {call.client_email && (
                        <VuiTypography variant="caption" color="text">
                          {call.client_email}
                        </VuiTypography>
                      )}
                    </TableCell>
                    <TableCell>
                      <VuiTypography variant="body2" color="white">
                        {formatDuration(call.duration)}
                      </VuiTypography>
                    </TableCell>
                    <TableCell>
                      <VuiTypography
                        variant="body2"
                        color={call.revenue > 0 ? "success" : "text"}
                        fontWeight={call.revenue > 0 ? "medium" : "regular"}
                      >
                        {call.revenue > 0 ? `$${call.revenue.toLocaleString()}` : "-"}
                      </VuiTypography>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={5} align="center">
                    <VuiTypography variant="button" color="text">
                      No calls match the current filter
                    </VuiTypography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </VuiBox>
      
      {filteredCalls.length > rowsPerPage && (
        <VuiBox
          display="flex"
          justifyContent="flex-end"
          p={3}
        >
          <Pagination 
            count={totalPages}
            page={page}
            onChange={handlePageChange}
            color="primary"
            size="small"
            shape="rounded"
            sx={{
              "& .MuiPaginationItem-root": {
                color: "white",
              },
              "& .Mui-selected": {
                backgroundColor: "primary.main",
              },
            }}
          />
        </VuiBox>
      )}
    </Card>
  );
}

// PropTypes validation
CallsList.propTypes = {
  calls: PropTypes.arrayOf(
    PropTypes.shape({
      date: PropTypes.string.isRequired,
      status: PropTypes.string.isRequired,
      client_name: PropTypes.string,
      client_email: PropTypes.string,
      duration: PropTypes.number,
      revenue: PropTypes.number,
    })
  ).isRequired,
};

export default CallsList;