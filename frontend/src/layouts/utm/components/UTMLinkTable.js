/*!

=========================================================
* Vision UI Free React - UTM Link Table
=========================================================

*/

import { useState, useEffect } from "react";
import { useHistory } from "react-router-dom";
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Card,
  IconButton,
  InputBase,
  Box,
  CircularProgress,
  Typography,
  Chip,
} from "@mui/material";
import { styled, alpha } from "@mui/material/styles";
import SearchIcon from "@mui/icons-material/Search";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import InfoIcon from "@mui/icons-material/Info";
import NoDataIcon from "@mui/icons-material/InfoOutlined";
import AnalyticsIcon from "@mui/icons-material/Analytics";

// Vision UI Dashboard React components
import VuiBox from "components/VuiBox";
import VuiTypography from "components/VuiTypography";
import VuiButton from "components/VuiButton";
import colors from "assets/theme/base/colors";

// API utility
import api from "utils/api";

// Search input styling
const Search = styled('div')(({ theme }) => ({
  position: 'relative',
  borderRadius: theme.shape.borderRadius,
  backgroundColor: alpha(theme.palette.common.white, 0.15),
  '&:hover': {
    backgroundColor: alpha(theme.palette.common.white, 0.25),
  },
  marginLeft: 0,
  width: '100%',
  [theme.breakpoints.up('sm')]: {
    marginLeft: theme.spacing(1),
    width: 'auto',
  },
}));

const SearchIconWrapper = styled('div')(({ theme }) => ({
  padding: theme.spacing(0, 2),
  height: '100%',
  position: 'absolute',
  pointerEvents: 'none',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
}));

const StyledInputBase = styled(InputBase)(({ theme }) => ({
  color: 'inherit',
  '& .MuiInputBase-input': {
    padding: theme.spacing(1, 1, 1, 0),
    paddingLeft: `calc(1em + ${theme.spacing(4)})`,
    transition: theme.transitions.create('width'),
    width: '100%',
    [theme.breakpoints.up('sm')]: {
      width: '12ch',
      '&:focus': {
        width: '20ch',
      },
    },
  },
}));

function UTMLinkTable({ dateRange }) {
  const history = useHistory();
  const [links, setLinks] = useState([]);
  const [filteredLinks, setFilteredLinks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [copiedId, setCopiedId] = useState(null);

  // Format numbers and currency
  const formatNumber = (num) => {
    return num?.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",") || "0";
  };

  const formatCurrency = (num) => {
    return `$${formatNumber(num || 0)}`;
  };

  // Copy link to clipboard
  const handleCopyLink = (link, id) => {
    navigator.clipboard.writeText(link);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  // Handle search filter
  const handleSearchChange = (event) => {
    const term = event.target.value.toLowerCase();
    setSearchTerm(term);

    const filtered = links.filter(link => 
      link.title.toLowerCase().includes(term) || 
      link.slug.toLowerCase().includes(term) ||
      link.destination_url.toLowerCase().includes(term)
    );
    
    setFilteredLinks(filtered);
  };

  // Truncate long URLs
  const truncateUrl = (url, maxLength = 40) => {
    if (!url) return "";
    return url.length > maxLength ? `${url.substring(0, maxLength)}...` : url;
  };

  // Calculate base domain for UTM links
  const baseDomain = process.env.REACT_APP_BASE_URL || "https://yourdomain.com";

  // Handle row click to navigate to Deep View
  const handleRowClick = (slug) => {
    history.push(`/deep-view/${slug}`);
  };

  // Fetch UTM links data
  useEffect(() => {
    const fetchLinks = async () => {
      setLoading(true);
      setError(null);

      try {
        // Add date range params if available
        let params = {};
        if (dateRange?.startDate && dateRange?.endDate) {
          params = {
            start_date: dateRange.startDate,
            end_date: dateRange.endDate
          };
        }

        const response = await api.get('/api/links', { params });
        setLinks(response.data.links);
        setFilteredLinks(response.data.links);
      } catch (err) {
        console.error('Error fetching UTM links:', err);
        setError('Failed to load UTM links. Please try again later.');
        
        // Temporary mock data for development
        const mockData = [
          {
            id: 1,
            title: "YouTube Agency Scale",
            slug: "youtube-agency-scale",
            destination_url: "https://example.com/agency-program",
            clicks: 1253,
            booked_calls: 87,
            deals_closed: 32,
            revenue: 128000,
            created_at: "2023-12-01T12:00:00Z"
          },
          {
            id: 2,
            title: "Facebook Coaching Ad",
            slug: "facebook-coaching",
            destination_url: "https://example.com/coaching",
            clicks: 835,
            booked_calls: 62,
            deals_closed: 18,
            revenue: 63000,
            created_at: "2024-01-15T09:30:00Z"
          },
          {
            id: 3,
            title: "Summer Masterclass",
            slug: "summer-masterclass",
            destination_url: "https://example.com/masterclass?ref=summer",
            clicks: 1890,
            booked_calls: 145,
            deals_closed: 58,
            revenue: 145000,
            created_at: "2024-02-20T14:45:00Z"
          },
          {
            id: 4,
            title: "Podcast Appearance",
            slug: "podcast-growth",
            destination_url: "https://example.com/podcast-offer",
            clicks: 612,
            booked_calls: 41,
            deals_closed: 12,
            revenue: 36000,
            created_at: "2024-03-10T11:20:00Z"
          },
          {
            id: 5,
            title: "Email Newsletter",
            slug: "email-exclusive",
            destination_url: "https://example.com/newsletter-special",
            clicks: 423,
            booked_calls: 28,
            deals_closed: 9,
            revenue: 22500,
            created_at: "2024-03-18T08:15:00Z"
          }
        ];
        
        setLinks(mockData);
        setFilteredLinks(mockData);
      } finally {
        setLoading(false);
      }
    };

    fetchLinks();
  }, [dateRange]);

  if (loading) {
    return (
      <VuiBox display="flex" justifyContent="center" alignItems="center" height="200px">
        <CircularProgress color="info" />
      </VuiBox>
    );
  }

  if (error) {
    return (
      <VuiBox display="flex" justifyContent="center" alignItems="center" height="200px" flexDirection="column">
        <InfoIcon color="error" sx={{ fontSize: 40, mb: 2 }} />
        <VuiTypography color="text">{error}</VuiTypography>
      </VuiBox>
    );
  }

  if (filteredLinks.length === 0) {
    return (
      <VuiBox>
        <VuiBox mb={2} display="flex" justifyContent="flex-end">
          <Search>
            <SearchIconWrapper>
              <SearchIcon />
            </SearchIconWrapper>
            <StyledInputBase
              placeholder="Search…"
              inputProps={{ 'aria-label': 'search' }}
              value={searchTerm}
              onChange={handleSearchChange}
            />
          </Search>
        </VuiBox>
        <VuiBox display="flex" justifyContent="center" alignItems="center" height="200px" flexDirection="column">
          <NoDataIcon sx={{ fontSize: 40, mb: 2, color: colors.text.main }} />
          {searchTerm ? (
            <VuiTypography color="text">No links match your search criteria</VuiTypography>
          ) : (
            <VuiTypography color="text">No UTM links found. Create your first link using the generator above.</VuiTypography>
          )}
        </VuiBox>
      </VuiBox>
    );
  }

  return (
    <VuiBox>
      <VuiBox mb={2} display="flex" justifyContent="flex-end">
        <Search>
          <SearchIconWrapper>
            <SearchIcon />
          </SearchIconWrapper>
          <StyledInputBase
            placeholder="Search…"
            inputProps={{ 'aria-label': 'search' }}
            value={searchTerm}
            onChange={handleSearchChange}
          />
        </Search>
      </VuiBox>
      
      <TableContainer component={Paper} sx={{ backgroundColor: "transparent" }}>
        <Table sx={{ minWidth: 650 }} aria-label="UTM links table">
          <TableHead>
            <TableRow>
              <TableCell>
                <VuiTypography variant="caption" color="text" fontWeight="medium">
                  VIDEO TITLE
                </VuiTypography>
              </TableCell>
              <TableCell>
                <VuiTypography variant="caption" color="text" fontWeight="medium">
                  SHORT LINK
                </VuiTypography>
              </TableCell>
              <TableCell>
                <VuiTypography variant="caption" color="text" fontWeight="medium">
                  DESTINATION
                </VuiTypography>
              </TableCell>
              <TableCell align="right">
                <VuiTypography variant="caption" color="text" fontWeight="medium">
                  CLICKS
                </VuiTypography>
              </TableCell>
              <TableCell align="right">
                <VuiTypography variant="caption" color="text" fontWeight="medium">
                  BOOKED CALLS
                </VuiTypography>
              </TableCell>
              <TableCell align="right">
                <VuiTypography variant="caption" color="text" fontWeight="medium">
                  DEALS
                </VuiTypography>
              </TableCell>
              <TableCell align="right">
                <VuiTypography variant="caption" color="text" fontWeight="medium">
                  REVENUE
                </VuiTypography>
              </TableCell>
              <TableCell align="center">
                <VuiTypography variant="caption" color="text" fontWeight="medium">
                  ACTIONS
                </VuiTypography>
              </TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredLinks.map((link) => (
              <TableRow
                key={link.id}
                sx={{ 
                  '&:last-child td, &:last-child th': { border: 0 },
                  cursor: 'pointer',
                  transition: 'background-color 0.2s',
                  '&:hover': { 
                    backgroundColor: 'rgba(26, 31, 55, 0.7)'
                  }
                }}
                onClick={() => handleRowClick(link.slug)}
              >
                <TableCell component="th" scope="row">
                  <VuiTypography variant="button" color="white">
                    {link.title}
                  </VuiTypography>
                </TableCell>
                <TableCell>
                  <VuiBox display="flex" alignItems="center">
                    <VuiTypography variant="button" color="info" sx={{ mr: 1 }}>
                      {`${baseDomain}/go/${link.slug}`}
                    </VuiTypography>
                    <IconButton 
                      size="small" 
                      onClick={(e) => {
                        e.stopPropagation(); // Prevent row click when clicking copy button
                        handleCopyLink(`${baseDomain}/go/${link.slug}`, link.id);
                      }}
                      sx={{ color: copiedId === link.id ? colors.success.main : colors.text.main }}
                    >
                      <ContentCopyIcon fontSize="small" />
                    </IconButton>
                  </VuiBox>
                </TableCell>
                <TableCell>
                  <VuiTypography variant="button" color="text">
                    {truncateUrl(link.destination_url)}
                  </VuiTypography>
                </TableCell>
                <TableCell align="right">
                  <VuiTypography variant="button" color="white">
                    {formatNumber(link.clicks)}
                  </VuiTypography>
                </TableCell>
                <TableCell align="right">
                  <VuiTypography variant="button" color="white">
                    {formatNumber(link.booked_calls)}
                  </VuiTypography>
                </TableCell>
                <TableCell align="right">
                  <VuiTypography variant="button" color="white">
                    {formatNumber(link.deals_closed)}
                  </VuiTypography>
                </TableCell>
                <TableCell align="right">
                  <VuiTypography variant="button" color="success">
                    {formatCurrency(link.revenue)}
                  </VuiTypography>
                </TableCell>
                <TableCell align="center">
                  <IconButton
                    size="small"
                    onClick={(e) => {
                      e.stopPropagation(); // Prevent row click when clicking the analytics button
                      handleRowClick(link.slug);
                    }}
                    sx={{ color: colors.info.main }}
                    title="View Deep Analytics"
                  >
                    <AnalyticsIcon fontSize="small" />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </VuiBox>
  );
}

export default UTMLinkTable; 