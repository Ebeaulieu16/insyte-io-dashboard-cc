import { useState } from "react";
import { Link } from "react-router-dom";
import VuiBox from "components/VuiBox";
import VuiTypography from "components/VuiTypography";
import VuiInput from "components/VuiInput";
import VuiButton from "components/VuiButton";
import CoverLayout from "layouts/authentication/components/CoverLayout";
import GradientBorder from "examples/GradientBorder";
import LoginForm from "layouts/authentication/components/LoginForm";

// Images
import bgSignIn from "assets/images/signInImage.png";

function Login() {
  return (
    <CoverLayout
      title="Welcome back"
      description="Enter your email and password to sign in"
      image={bgSignIn}
      button={{ color: "info", variant: "gradient" }}
    >
      <LoginForm />
    </CoverLayout>
  );
}

export default Login; 