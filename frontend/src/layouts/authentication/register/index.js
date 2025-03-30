import VuiBox from "components/VuiBox";
import CoverLayout from "layouts/authentication/components/CoverLayout";
import RegisterForm from "layouts/authentication/components/RegisterForm";

// Images
import bgSignUp from "assets/images/signUpImage.png";

function Register() {
  return (
    <CoverLayout
      title="Join Insyte Dashboard"
      description="Create an account to track and analyze your performance metrics."
      image={bgSignUp}
      button={{ color: "info", variant: "gradient" }}
    >
      <RegisterForm />
    </CoverLayout>
  );
}

export default Register; 