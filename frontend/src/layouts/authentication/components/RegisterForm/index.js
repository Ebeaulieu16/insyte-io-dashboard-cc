import { useState, useEffect } from "react";
import { Link, useHistory } from "react-router-dom";
import { Card, Checkbox, FormControlLabel } from "@mui/material";
import VuiBox from "components/VuiBox";
import VuiTypography from "components/VuiTypography";
import VuiInput from "components/VuiInput";
import VuiButton from "components/VuiButton";
import axios from "axios";
import { toast } from "react-toastify";
import { useAuth } from "context/auth";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

function RegisterForm() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [agreement, setAgreement] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const history = useHistory();
  const { register, isAuthenticated } = useAuth();

  // Redirect if already authenticated
  useEffect(() => {
    console.log("Register component useEffect, isAuthenticated:", isAuthenticated);
    if (isAuthenticated) {
      console.log("User is authenticated, redirecting to dashboard");
      history.push("/dashboard");
    }
  }, [isAuthenticated, history]);

  const handleSetAgreement = () => setAgreement(!agreement);

  const handleRegister = async (e) => {
    e.preventDefault();
    console.log("Register attempt with email:", email);
    
    // Validate form
    if (!agreement) {
      toast.warning("Please agree to the terms and conditions.");
      return;
    }
    
    if (password !== confirmPassword) {
      toast.error("Passwords do not match!");
      return;
    }
    
    setIsLoading(true);

    try {
      // Call the register function from auth context
      const success = await register(email, password);
      console.log("Registration success:", success);

      if (success) {
        console.log("Redirecting to dashboard after registration");
        history.push("/dashboard");
      }
    } catch (error) {
      console.error("Registration error:", error);
      toast.error(
        error.response?.data?.detail || "Registration failed. Please try again."
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card>
      <VuiBox p={3} mb="22px">
        <VuiBox component="form" role="form" onSubmit={handleRegister}>
          <VuiBox mb={2}>
            <VuiBox mb={1} ml={0.5}>
              <VuiTypography
                component="label"
                variant="button"
                color="primary"
                fontWeight="medium"
              >
                Email
              </VuiTypography>
            </VuiBox>
            <VuiInput
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </VuiBox>
          <VuiBox mb={2}>
            <VuiBox mb={1} ml={0.5}>
              <VuiTypography
                component="label"
                variant="button"
                color="primary"
                fontWeight="medium"
              >
                Password
              </VuiTypography>
            </VuiBox>
            <VuiInput
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </VuiBox>
          <VuiBox mb={2}>
            <VuiBox mb={1} ml={0.5}>
              <VuiTypography
                component="label"
                variant="button"
                color="primary"
                fontWeight="medium"
              >
                Confirm Password
              </VuiTypography>
            </VuiBox>
            <VuiInput
              type="password"
              placeholder="Confirm Password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
            />
          </VuiBox>
          <VuiBox display="flex" alignItems="center">
            <FormControlLabel
              control={
                <Checkbox
                  checked={agreement}
                  onChange={handleSetAgreement}
                  sx={{
                    color: "info.main",
                    "&.Mui-checked": {
                      color: "info.main",
                    },
                  }}
                />
              }
              label={
                <VuiTypography
                  variant="button"
                  color="text"
                  fontWeight="regular"
                >
                  I agree to the{" "}
                  <VuiTypography
                    component={Link}
                    to="#"
                    variant="button"
                    color="info"
                    fontWeight="medium"
                  >
                    Terms and Conditions
                  </VuiTypography>
                </VuiTypography>
              }
            />
          </VuiBox>
          <VuiBox mt={4} mb={1}>
            <VuiButton
              color="info"
              fullWidth
              type="submit"
              disabled={isLoading}
            >
              {isLoading ? "Registering..." : "SIGN UP"}
            </VuiButton>
          </VuiBox>
          <VuiBox mt={3} textAlign="center">
            <VuiTypography variant="button" color="text" fontWeight="regular">
              Already have an account?{" "}
              <VuiTypography
                component={Link}
                to="/authentication/login"
                variant="button"
                color="info"
                fontWeight="medium"
              >
                Sign in
              </VuiTypography>
            </VuiTypography>
          </VuiBox>
        </VuiBox>
      </VuiBox>
    </Card>
  );
}

export default RegisterForm; 