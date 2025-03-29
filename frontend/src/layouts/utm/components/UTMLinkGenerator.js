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
  const [generatedLink, setGeneratedLink] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [apiError, setApiError] = useState("");
  const [showCopyToast, setShowCopyToast] = useState(false);

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
      });

      setGeneratedLink(response.data.link);
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
      <form onSubmit={handleSubmit}>
        <Grid container spacing={3}>
          {/* Video Title Input */}
          <Grid item xs={12}>
            <VuiBox mb={1} ml={0.5}>
              <VuiTypography component="label" variant="button" color="white" fontWeight="medium">
                Video Title
              </VuiTypography>
            </VuiBox>
            <VuiInput
              type="text"
              placeholder="e.g., How to Scale Your YouTube Channel"
              value={title}
              onChange={handleTitleChange}
              error={!!errors.title}
              success={title && !errors.title}
            />
            {errors.title && (
              <VuiTypography component="div" variant="button" color="error" fontWeight="regular" mt={0.5}>
                {errors.title}
              </VuiTypography>
            )}
          </Grid>

          {/* Slug Input */}
          <Grid item xs={12}>
            <VuiBox mb={1} ml={0.5}>
              <VuiTypography component="label" variant="button" color="white" fontWeight="medium">
                Slug (appears in the URL)
              </VuiTypography>
            </VuiBox>
            <VuiInput
              type="text"
              placeholder="e.g., scale-your-content"
              value={slug}
              onChange={handleSlugChange}
              error={!!errors.slug}
              success={slug && !errors.slug}
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
          </Grid>

          {/* Destination URL Input */}
          <Grid item xs={12}>
            <VuiBox mb={1} ml={0.5}>
              <VuiTypography component="label" variant="button" color="white" fontWeight="medium">
                Destination URL
              </VuiTypography>
            </VuiBox>
            <VuiInput
              type="url"
              placeholder="https://calendly.com/yourusername/call"
              value={destinationUrl}
              onChange={handleDestinationUrlChange}
              error={!!errors.destinationUrl}
              success={destinationUrl && !errors.destinationUrl}
            />
            {errors.destinationUrl && (
              <VuiTypography component="div" variant="button" color="error" fontWeight="regular" mt={0.5}>
                {errors.destinationUrl}
              </VuiTypography>
            )}
          </Grid>

          {/* Submit Button */}
          <Grid item xs={12}>
            <VuiButton
              type="submit"
              color="info"
              variant="contained"
              disabled={isLoading}
              fullWidth
            >
              {isLoading ? "Generating..." : "Generate UTM Link"}
            </VuiButton>
          </Grid>

          {/* API Error Display */}
          {apiError && (
            <Grid item xs={12}>
              <Alert
                severity="error"
                sx={{
                  backgroundColor: "rgba(244, 67, 53, 0.1)",
                  color: "#f44335",
                  borderRadius: "10px",
                  border: "1px solid rgba(244, 67, 53, 0.3)",
                }}
              >
                {apiError}
              </Alert>
            </Grid>
          )}

          {/* Generated Link Display */}
          {generatedLink && (
            <Grid item xs={12}>
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
                </VuiBox>
              </Card>
            </Grid>
          )}
        </Grid>
      </form>

      {/* Copy Success Toast */}
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