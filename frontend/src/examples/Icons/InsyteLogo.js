import PropTypes from "prop-types";

// Import the actual Insyte logo
import logo from "assets/images/Logo Insyte.png";

function InsyteLogo({ size }) {
  return (
    <img
      src={logo}
      alt="Insyte Logo"
      style={{ 
        width: size, 
        height: "auto",
        objectFit: "contain"
      }}
    />
  );
}

// Setting default values for the props of InsyteLogo
InsyteLogo.defaultProps = {
  size: "24px",
};

// Typechecking props for the InsyteLogo
InsyteLogo.propTypes = {
  size: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
};

export default InsyteLogo; 