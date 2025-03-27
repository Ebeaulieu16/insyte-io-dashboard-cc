/*!

=========================================================
* Vision UI Free React - v1.0.0
=========================================================

* Product Page: https://www.creative-tim.com/product/vision-ui-free-react
* Copyright 2021 Creative Tim (https://www.creative-tim.com/)
* Licensed under MIT (https://github.com/creativetimofficial/vision-ui-free-react/blob/master LICENSE.md)

* Design and Coded by Simmmple & Creative Tim

=========================================================

* The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

*/

/** 
  All of the routes for the Vision UI Dashboard React are added here,
  You can add a new route, customize the routes and delete the routes here.

  Once you add a new route on this file it will be visible automatically on
  the Sidenav.

  For adding a new route you can follow the existing routes in the routes array.
  1. The `type` key with the `collapse` value is used for a route.
  2. The `type` key with the `title` value is used for a title inside the Sidenav. 
  3. The `type` key with the `divider` value is used for a divider between Sidenav items.
  4. The `name` key is used for the name of the route on the Sidenav.
  5. The `key` key is used for the key of the route (It will help you with the key prop inside a loop).
  6. The `icon` key is used for the icon of the route on the Sidenav, you have to add a node.
  7. The `collapse` key is used for making a collapsible item on the Sidenav that has other routes
  inside (nested routes), you need to pass the nested routes inside an array as a value for the `collapse` key.
  8. The `route` key is used to store the route location which is used for the react router.
  9. The `href` key is used to store the external links location.
  10. The `title` key is only for the item with the type of `title` and its used for the title text on the Sidenav.
  10. The `component` key is used to store the component of its route.
*/

// Vision UI Dashboard React layouts
import Dashboard from "layouts/dashboard";
import Sales from "layouts/sales";
import YouTube from "layouts/youtube";
import UTMGenerator from "layouts/utm";
import Integrations from "layouts/integrations";
import Recommendations from "layouts/recommendations";
import DeepView from "layouts/deepView";

// No longer using these template views
// import Tables from "layouts/tables";
// import Billing from "layouts/billing";
// import RTL from "layouts/rtl";
// import Profile from "layouts/profile";
// import SignIn from "layouts/authentication/sign-in";
// import SignUp from "layouts/authentication/sign-up";

// Vision UI Dashboard React icons
import { IoStatsChart } from "react-icons/io5";
import { FaChartLine, FaYoutube, FaLink, FaPlug, FaLightbulb } from "react-icons/fa";
import { IoHome } from "react-icons/io5";

const routes = [
  {
    type: "collapse",
    name: "Dashboard",
    key: "dashboard",
    route: "/dashboard",
    icon: <IoHome size="15px" color="inherit" />,
    component: Dashboard,
    noCollapse: true,
  },
  {
    type: "collapse",
    name: "Sales",
    key: "sales",
    route: "/sales",
    icon: <FaChartLine size="15px" color="inherit" />,
    component: Sales,
    noCollapse: true,
  },
  {
    type: "collapse",
    name: "YouTube",
    key: "youtube",
    route: "/youtube",
    icon: <FaYoutube size="15px" color="inherit" />,
    component: YouTube,
    noCollapse: true,
  },
  {
    type: "collapse",
    name: "UTM Generator",
    key: "utm-generator",
    route: "/utm-generator",
    icon: <FaLink size="15px" color="inherit" />,
    component: UTMGenerator,
    noCollapse: true,
  },
  {
    type: "collapse",
    name: "Integrations",
    key: "integrations",
    route: "/integrations",
    icon: <FaPlug size="15px" color="inherit" />,
    component: Integrations,
    noCollapse: true,
  },
  {
    type: "collapse",
    name: "Recommendations",
    key: "recommendations",
    route: "/recommendations",
    icon: <FaLightbulb size="15px" color="inherit" />,
    component: Recommendations,
    noCollapse: true,
  },
  // Hidden route - not shown in Sidenav
  {
    type: "collapse",
    name: "Deep View",
    key: "deep-view",
    route: "/deep-view/:slug",
    component: DeepView,
    noCollapse: true,
    display: "none", // Custom property to hide from Sidenav
  },
];

export default routes;
