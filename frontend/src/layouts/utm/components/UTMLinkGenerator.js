import { useState, useEffect } from "react";
import { CopyToClipboard } from "react-copy-to-clipboard";
import PropTypes from "prop-types";

// API utility
import api from "utils/api";

// @mui material components
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import FormControl from "@mui/material/FormControl";
import FormHelperText from "@mui/material/FormHelperText";
import OutlinedInput from "@mui/material/OutlinedInput";
import Alert from "@mui/material/Alert";
import Snackbar from "@mui/material/Snackbar";
import CircularProgress from "@mui/material/CircularProgress";

// Vision UI Dashboard React components
import VuiBox from "components/VuiBox";
import VuiTypography from "components/VuiTypography";
import VuiButton from "components/VuiButton";
import VuiInput from "components/VuiInput";

// React icons
import { IoLinkSharp, IoCheckmarkCircle, IoClose, IoCopy } from "react-icons/io5";

function UTMLinkGenerator({ onSuccess }) {
  // State variables
  const [title, setTitle] = useState("");
  const [slug, setSlug] = useState("");
  const [destinationUrl, setDestinationUrl] = useState("");
  const [utmSource, setUtmSource] = useState("youtube");
  const [utmMedium, setUtmMedium] = useState("video");
  const [utmCampaign, setUtmCampaign] = useState("");
  const [utmContent, setUtmContent] = useState("");
  const [customParam, setCustomParam] = useState({ name: "", value: "" });
  const [generatedLink, setGeneratedLink] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [apiError, setApiError] = useState("");
  const [showCopyToast, setShowCopyToast] = useState(false);
  
  // Source options
  const sourceOptions = [
    { value: "youtube", label: "YouTube" },
    { value: "facebook", label: "Facebook" },
    { value: "instagram", label: "Instagram" },
    { value: "linkedin", label: "LinkedIn" },
    { value: "twitter", label: "Twitter" },
    { value: "tiktok", label: "TikTok" },
    { value: "email", label: "Email" },
    { value: "direct", label: "Direct" },
  ];
  
  // Medium options
  const mediumOptions = [
    { value: "video", label: "Video" },
    { value: "social", label: "Social" },
    { value: "email", label: "Email" },
    { value: "cpc", label: "CPC" },
    { value: "organic", label: "Organic" },
    { value: "referral", label: "Referral" },
  ];

  // Auto-generate slug from title
  useEffect(() => {
    if (title && !slug) {
      const generatedSlug = title
        .toLowerCase()
        .replace(/[^a-z0-9\s-]/g, "")
        .replace(/\s+/g, "-");
      setSlug(generatedSlug);
    }
  }, [title, slug]);

  // Validation functions
  const validateTitle = (value) => {
    if (!value.trim()) {
      return "Title is required";
    }
    return "";
  };

  const validateSlug = (value) => {
    if (!value.trim()) {
      return "Slug is required";
    }
    if (!/^[a-z0-9-]+$/.test(value)) {
      return "Slug must contain only lowercase letters, numbers, and hyphens";
    }
    if (value.length < 3) {
      return "Slug must be at least 3 characters long";
    }
    return "";
  };

  const validateUrl = (value) => {
    if (!value.trim()) {
      return "Destination URL is required";
    }
    try {
      new URL(value);
      return "";
    } catch (e) {
      return "Please enter a valid URL (including http:// or https://)";
    }
  };

  // Form validation
  const validateForm = () => {
    const titleError = validateTitle(title);
    const slugError = validateSlug(slug);
    const urlError = validateUrl(destinationUrl);

    const newErrors = {
      title: titleError,
      slug: slugError,
      destinationUrl: urlError,
    };

    setErrors(newErrors);
    return !titleError && !slugError && !urlError;
  };

  // Handle input changes
  const handleTitleChange = (e) => {
    setTitle(e.target.value);
    if (errors.title) {
      setErrors({ ...errors, title: validateTitle(e.target.value) });
    }
  };

  const handleSlugChange = (e) => {
    const value = e.target.value.toLowerCase();
    setSlug(value);
    if (errors.slug) {
      setErrors({ ...errors, slug: validateSlug(value) });
    }
  };

  const handleDestinationUrlChange = (e) => {
    setDestinationUrl(e.target.value);
    if (errors.destinationUrl) {
      setErrors({ ...errors, destinationUrl: validateUrl(e.target.value) });
    }
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);
    setApiError("");

    try {
      const response = await api.post("/api/links/create", {
        title,
        slug,
        destination_url: destinationUrl,
        utm_source: utmSource,
        utm_medium: utmMedium,
        utm_campaign: utmCampaign || undefined,
      });

      // Construct the full UTM link for display
      const baseLink = response.data.link;
      let displayLink = baseLink;
      
      // Add utm_content if provided (this is handled client-side for display purposes)
      if (utmContent) {
        displayLink = `${displayLink}&utm_content=${encodeURIComponent(utmContent)}`;
      }
      
      // Add custom parameter if both name and value are provided
      if (customParam.name && customParam.value) {
        displayLink = `${displayLink}&${encodeURIComponent(customParam.name)}=${encodeURIComponent(customParam.value)}`;
      }
      
      setGeneratedLink(displayLink);
      setIsLoading(false);
      
      // Call the onSuccess callback if provided
      if (onSuccess && typeof onSuccess === 'function') {
        onSuccess();
      }
    } catch (error) {
      setIsLoading(false);
      
      if (error.response && error.response.status === 409) {
        setApiError("This slug already exists. Please try a different one.");
      } else if (error.response && error.response.status === 400) {
        setApiError(error.response.data.detail || "Invalid input. Please check your entries.");
      } else {
        setApiError("An error occurred. Please try again later.");
      }
    }
  };

  // Handle copy to clipboard
  const handleCopy = () => {
    setShowCopyToast(true);
    setTimeout(() => setShowCopyToast(false), 3000);
  };

  return (
    <VuiBox>
      <VuiTypography variant="h5" color="white" mb={1}>
        Create Links with UTM Parameters
      </VuiTypography>
      <VuiTypography variant="caption" color="text" fontWeight="regular" mb={3}>
        Generate links with UTM parameters to track your marketing campaigns
      </VuiTypography>
      
      {apiError && (
        <Alert severity="error" sx={{ mb: 3, backgroundColor: "rgba(244, 67, 53, 0.1)", color: "#f44335" }}>
          {apiError}
        </Alert>
      )}
      
      <form onSubmit={handleSubmit}>
        <Grid container spacing={3}>
          {/* Left Column */}
          <Grid item xs={12} md={6}>
            {/* Base URL field */}
            <VuiBox mb={2}>
              <VuiTypography component="label" variant="button" color="white" fontWeight="medium" mb={1} display="block">
                Base URL
              </VuiTypography>
              <VuiInput
                type="url"
                placeholder="https://insyte.io/webinar"
                value={destinationUrl}
                onChange={handleDestinationUrlChange}
                error={!!errors.destinationUrl}
                success={destinationUrl && !errors.destinationUrl}
                sx={{
                  backgroundColor: "#2B2B2B !important",
                  border: "none !important",
                  "& input": {
                    color: "#FFFFFF !important",
                    backgroundColor: "#2B2B2B !important"
                  },
                  "& ::placeholder": {
                    color: "#656565 !important",
                    fontSize: "14px !important",
                    opacity: "1 !important"
                  },
                  "& .MuiInputBase-input": {
                    backgroundColor: "#2B2B2B !important"
                  },
                  "& fieldset": {
                    border: "none !important"
                  },
                  "&.Mui-focused": {
                    boxShadow: "none !important",
                    border: "none !important"
                  }
                }}
              />
              {errors.destinationUrl && (
                <VuiTypography component="div" variant="button" color="error" fontWeight="regular" mt={0.5}>
                  {errors.destinationUrl}
                </VuiTypography>
              )}
            </VuiBox>
            
            {/* Video Title field */}
            <VuiBox mb={2}>
              <VuiTypography component="label" variant="button" color="white" fontWeight="medium" mb={1} display="block">
                Video Title
              </VuiTypography>
              <VuiInput
                type="text"
                placeholder="e.g., How to Scale Your YouTube Channel"
                value={title}
                onChange={handleTitleChange}
                error={!!errors.title}
                success={title && !errors.title}
                sx={{
                  backgroundColor: "#2B2B2B !important",
                  border: "none !important",
                  "& input": {
                    color: "#FFFFFF !important",
                    backgroundColor: "#2B2B2B !important"
                  },
                  "& ::placeholder": {
                    color: "#656565 !important",
                    fontSize: "14px !important",
                    opacity: "1 !important"
                  },
                  "& .MuiInputBase-input": {
                    backgroundColor: "#2B2B2B !important"
                  },
                  "& fieldset": {
                    border: "none !important"
                  },
                  "&.Mui-focused": {
                    boxShadow: "none !important",
                    border: "none !important"
                  }
                }}
              />
              {errors.title && (
                <VuiTypography component="div" variant="button" color="error" fontWeight="regular" mt={0.5}>
                  {errors.title}
                </VuiTypography>
              )}
            </VuiBox>
            
            {/* Slug field */}
            <VuiBox mb={2}>
              <VuiTypography component="label" variant="button" color="white" fontWeight="medium" mb={1} display="block">
                Slug (appears in the URL)
              </VuiTypography>
              <VuiInput
                type="text"
                placeholder="e.g., scale-your-content"
                value={slug}
                onChange={handleSlugChange}
                error={!!errors.slug}
                success={slug && !errors.slug}
                sx={{
                  backgroundColor: "#2B2B2B !important",
                  border: "none !important",
                  "& input": {
                    color: "#FFFFFF !important",
                    backgroundColor: "#2B2B2B !important"
                  },
                  "& ::placeholder": {
                    color: "#656565 !important",
                    fontSize: "14px !important",
                    opacity: "1 !important"
                  },
                  "& .MuiInputBase-input": {
                    backgroundColor: "#2B2B2B !important"
                  },
                  "& fieldset": {
                    border: "none !important"
                  },
                  "&.Mui-focused": {
                    boxShadow: "none !important",
                    border: "none !important"
                  }
                }}
              />
              {errors.slug ? (
                <VuiTypography component="div" variant="button" color="error" fontWeight="regular" mt={0.5}>
                  {errors.slug}
                </VuiTypography>
              ) : (
                <VuiTypography component="div" variant="button" color="text" fontWeight="regular" mt={0.5}>
                  Lowercase letters, numbers, and hyphens only
                </VuiTypography>
              )}
            </VuiBox>
          </Grid>
          
          {/* Right Column */}
          <Grid item xs={12} md={6}>
            {/* UTM Source field */}
            <VuiBox mb={2}>
              <VuiTypography component="label" variant="button" color="white" fontWeight="medium" mb={1} display="block">
                Source (required)
              </VuiTypography>
              <select
                value={utmSource}
                onChange={(e) => setUtmSource(e.target.value)}
                style={{
                  backgroundColor: "#2B2B2B",
                  color: "white",
                  padding: "12px",
                  border: "none",
                  borderRadius: "10px",
                  width: "100%",
                  outline: "none",
                  appearance: "menulist-button",
                  fontSize: "14px"
                }}
              >
                {sourceOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </VuiBox>
            
            {/* UTM Medium field */}
            <VuiBox mb={2}>
              <VuiTypography component="label" variant="button" color="white" fontWeight="medium" mb={1} display="block">
                Medium (required)
              </VuiTypography>
              <select
                value={utmMedium}
                onChange={(e) => setUtmMedium(e.target.value)}
                style={{
                  backgroundColor: "#2B2B2B",
                  color: "white",
                  padding: "12px",
                  border: "none",
                  borderRadius: "10px",
                  width: "100%",
                  outline: "none",
                  appearance: "menulist-button",
                  fontSize: "14px"
                }}
              >
                {mediumOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </VuiBox>
            
            {/* UTM Campaign field */}
            <VuiBox mb={2}>
              <VuiTypography component="label" variant="button" color="white" fontWeight="medium" mb={1} display="block">
                Campaign Name
              </VuiTypography>
              <VuiInput
                type="text"
                placeholder="e.g., webinar-sales"
                value={utmCampaign}
                onChange={(e) => setUtmCampaign(e.target.value)}
                sx={{
                  backgroundColor: "#2B2B2B !important",
                  border: "none !important",
                  "& input": {
                    color: "#FFFFFF !important",
                    backgroundColor: "#2B2B2B !important"
                  },
                  "& ::placeholder": {
                    color: "#656565 !important",
                    fontSize: "14px !important",
                    opacity: "1 !important"
                  },
                  "& .MuiInputBase-input": {
                    backgroundColor: "#2B2B2B !important"
                  },
                  "& fieldset": {
                    border: "none !important"
                  },
                  "&.Mui-focused": {
                    boxShadow: "none !important",
                    border: "none !important"
                  }
                }}
              />
              <VuiTypography component="div" variant="caption" color="text" fontWeight="regular" mt={0.5}>
                Used for paid campaigns (keywords)
              </VuiTypography>
            </VuiBox>
            
            {/* UTM Content field */}
            <VuiBox mb={2}>
              <VuiTypography component="label" variant="button" color="white" fontWeight="medium" mb={1} display="block">
                Content (optional)
              </VuiTypography>
              <VuiInput
                type="text"
                placeholder="content-description"
                value={utmContent}
                onChange={(e) => setUtmContent(e.target.value)}
                sx={{
                  backgroundColor: "#2B2B2B !important",
                  border: "none !important",
                  "& input": {
                    color: "#FFFFFF !important",
                    backgroundColor: "#2B2B2B !important"
                  },
                  "& ::placeholder": {
                    color: "#656565 !important",
                    fontSize: "14px !important",
                    opacity: "1 !important"
                  },
                  "& .MuiInputBase-input": {
                    backgroundColor: "#2B2B2B !important"
                  },
                  "& fieldset": {
                    border: "none !important"
                  },
                  "&.Mui-focused": {
                    boxShadow: "none !important",
                    border: "none !important"
                  }
                }}
              />
              <VuiTypography component="div" variant="caption" color="text" fontWeight="regular" mt={0.5}>
                Used to differentiate versions of similar content
              </VuiTypography>
            </VuiBox>
          </Grid>
          
          {/* Submit Button */}
          <Grid item xs={12}>
            <VuiButton
              type="submit"
              color="info"
              variant="contained"
              disabled={isLoading}
              fullWidth
              startIcon={isLoading ? <CircularProgress size={20} color="inherit" /> : <IoLinkSharp />}
            >
              {isLoading ? "Generating..." : "Generate UTM Link"}
            </VuiButton>
          </Grid>

          {/* Generated Link Display */}
          {generatedLink && (
            <Grid item xs={12}>
              <VuiBox mt={3}>
                <VuiTypography variant="h6" color="white" mb={2}>
                  Generated UTM Link
                </VuiTypography>
                <Card 
                  sx={{ 
                    background: "linear-gradient(127.09deg, rgba(6, 11, 40, 0.94) 19.41%, rgba(10, 14, 35, 0.49) 76.65%)",
                    border: "1px solid rgba(22, 249, 170, 0.3)",
                    borderRadius: "15px"
                  }}
                >
                  <VuiBox p={2}>
                    <VuiBox display="flex" alignItems="center" mb={1}>
                      <IoCheckmarkCircle size="18px" color="#16f9aa" />
                      <VuiTypography variant="button" color="success" fontWeight="medium" ml={1}>
                        UTM Link Generated Successfully
                      </VuiTypography>
                    </VuiBox>

                    <VuiBox
                      display="flex"
                      justifyContent="space-between"
                      alignItems="center"
                      bgcolor="rgba(22, 249, 170, 0.1)"
                      p={2}
                      borderRadius="10px"
                    >
                      <VuiTypography variant="button" color="white" fontWeight="regular" sx={{ wordBreak: "break-all" }}>
                        {generatedLink}
                      </VuiTypography>
                      <CopyToClipboard text={generatedLink} onCopy={handleCopy}>
                        <VuiButton color="primary" variant="outlined" size="small" sx={{ ml: 1, minWidth: "auto" }}>
                          <IoCopy size="18px" />
                        </VuiButton>
                      </CopyToClipboard>
                    </VuiBox>
                    <VuiTypography variant="caption" color="text" fontWeight="regular" mt={1} display="block">
                      Use this link in your YouTube videos. When viewers click it, we'll track their journey through your funnel.
                    </VuiTypography>
                  </VuiBox>
                </Card>
              </VuiBox>
            </Grid>
          )}
        </Grid>
      </form>
      
      {/* Copy toast notification */}
      <Snackbar
        open={showCopyToast}
        autoHideDuration={3000}
        onClose={() => setShowCopyToast(false)}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      >
        <Alert
          severity="success"
          sx={{
            backgroundColor: "rgba(22, 249, 170, 0.1)",
            color: "#16f9aa",
            borderRadius: "10px",
            border: "1px solid rgba(22, 249, 170, 0.3)",
          }}
          icon={<IoCheckmarkCircle size="24px" />}
          action={
            <VuiButton
              color="error"
              size="small"
              onClick={() => setShowCopyToast(false)}
              sx={{ minWidth: "auto", p: 0.5 }}
            >
              <IoClose size="18px" />
            </VuiButton>
          }
        >
          Link copied to clipboard!
        </Alert>
      </Snackbar>
    </VuiBox>
  );
}

// PropTypes validation
UTMLinkGenerator.propTypes = {
  onSuccess: PropTypes.func,
};

// Default props
UTMLinkGenerator.defaultProps = {
  onSuccess: () => {},
};

export default UTMLinkGenerator; 