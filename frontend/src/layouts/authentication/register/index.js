import VuiBox from "components/VuiBox";
import CoverLayout from "layouts/authentication/components/CoverLayout";
import RegisterForm from "layouts/authentication/components/RegisterForm";
import VuiTypography from "components/VuiTypography";

function Register() {
  return (
    <CoverLayout
      title={<VuiTypography color="primary">Join Insyte Dashboard</VuiTypography>}
      description="Create an account to track and analyze your performance metrics."
      button={{ color: "info", variant: "gradient" }}
    >
      <RegisterForm />
    </CoverLayout>
  );
}

export default Register; 