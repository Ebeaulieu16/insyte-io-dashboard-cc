/*!

=========================================================
* Vision UI Free React - v1.0.0
=========================================================

* Product Page: https://www.creative-tim.com/product/vision-ui-free-react
* Copyright 2021 Creative Tim (https://www.creative-tim.com/)
* Licensed under MIT (https://github.com/creativetimofficial/vision-ui-free-react/blob/master LICENSE.md)

* Design and Coded by Simmmple & Creative Tim

=========================================================

* The above copyright notice and this permission notice shall be included in all copies or substantial portions of the software.

*/

// @mui material components
import { MenuItem, FormControl, InputLabel } from "@mui/material";
import { styled } from "@mui/material/styles";

// Vision UI Dashboard React components
import VuiBox from "components/VuiBox";

// Custom styles for VuiSelect
import VuiSelectRoot from "components/VuiSelect/VuiSelectRoot";

const VuiSelectLabel = styled(InputLabel)(({ theme }) => ({
  color: theme.palette.text.secondary,
  fontSize: "0.875rem",
  fontWeight: 400,
  margin: "0 0 0.25rem 0.5rem",
}));

const VuiSelect = ({ label, size, options, placeholder, value, defaultValue, onChange, ...rest }) => {
  // Handle both string arrays and object arrays
  const renderOptions = () => {
    if (!options || options.length === 0) return null;
    
    // Check if options is array of strings or array of objects
    const isStringArray = typeof options[0] === 'string';
    
    return options.map((option, index) => {
      if (isStringArray) {
        return (
          <MenuItem key={`option-${index}`} value={option}>
            {option}
          </MenuItem>
        );
      } else {
        // Handle object with value and label
        const optionValue = option.value !== undefined ? option.value : option;
        const optionLabel = option.label !== undefined ? option.label : option;
        
        return (
          <MenuItem key={`option-${index}`} value={optionValue}>
            {optionLabel}
          </MenuItem>
        );
      }
    });
  };

  return (
    <VuiBox mb={1}>
      {label && <VuiSelectLabel>{label}</VuiSelectLabel>}
      <FormControl fullWidth>
        <VuiSelectRoot
          value={value}
          defaultValue={defaultValue}
          onChange={onChange}
          displayEmpty
          {...rest}
        >
          {placeholder && (
            <MenuItem value="" disabled>
              {placeholder}
            </MenuItem>
          )}
          {renderOptions()}
        </VuiSelectRoot>
      </FormControl>
    </VuiBox>
  );
};

// Setting default values for the props of VuiSelect
VuiSelect.defaultProps = {
  label: "",
  size: "medium",
  options: [],
  placeholder: "",
  defaultValue: "",
};

export default VuiSelect; 