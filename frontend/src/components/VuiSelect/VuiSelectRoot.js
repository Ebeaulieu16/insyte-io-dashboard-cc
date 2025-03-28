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
import { Select } from "@mui/material";
import { styled } from "@mui/material/styles";

export default styled(Select)(({ theme }) => ({
  display: "flex",
  alignItems: "center",
  width: "100%",
  height: "auto",
  padding: "0.75rem 0",
  backgroundColor: theme.palette.background.card,
  border: "1px solid rgba(226, 232, 240, 0.3)",
  borderRadius: "15px",
  color: theme.palette.white.main,
  "& .MuiSelect-select": {
    padding: "0 1rem",
  },
  "& .MuiOutlinedInput-notchedOutline": {
    border: "none",
  },
  "& .MuiSelect-icon": {
    color: theme.palette.white.main,
  },
  "&:hover": {
    backgroundColor: "rgba(26, 31, 55, 0.5)",
  },
  "&:focus": {
    boxShadow: `0 0 0 2px ${theme.palette.primary.main}`,
  },
})); 