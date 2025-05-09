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

import { useState, useEffect, useMemo, useRef } from "react";

// react-router components
import { Route, Switch, Navigate, useLocation, Redirect } from "react-router-dom";

// @mui material components
import { ThemeProvider } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import Icon from "@mui/material/Icon";

// Vision UI Dashboard React components
import VuiBox from "components/VuiBox";

// Vision UI Dashboard React example components
import Sidenav from "examples/Sidenav";
import Configurator from "examples/Configurator";

// Vision UI Dashboard React themes
import theme from "assets/theme";
import themeRTL from "assets/theme/theme-rtl";

// RTL plugins
import rtlPlugin from "stylis-plugin-rtl";
import { CacheProvider } from "@emotion/react";
import createCache from "@emotion/cache";

// Vision UI Dashboard React routes
import routes from "routes";

// Vision UI Dashboard React contexts
import { useVisionUIController, setMiniSidenav, setOpenConfigurator } from "context";
import { AuthProvider } from "./context/auth";
import { IntegrationProvider, useIntegration } from "./context/IntegrationContext";

import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Protected Route component
import ProtectedRoute from "components/ProtectedRoute";

// Authentication pages
import Login from "layouts/authentication/login";
import Register from "layouts/authentication/register";

// Route change handler component to refresh integrations on navigation
function RouteChangeHandler() {
  const { refreshIntegrations } = useIntegration();
  const hasInitializedRef = useRef(false);
  
  // Only refresh once when the application initially loads
  useEffect(() => {
    if (!hasInitializedRef.current) {
      console.log("Initial integration refresh on app startup");
      setTimeout(() => {
        refreshIntegrations();
        hasInitializedRef.current = true;
      }, 500); // Small delay to ensure components are mounted
    }
  }, [refreshIntegrations]);
  
  return null; // This component doesn't render anything
}

export default function App() {
  const [controller, dispatch] = useVisionUIController();
  const { miniSidenav, direction, layout, openConfigurator, sidenavColor } = controller;
  const [onMouseEnter, setOnMouseEnter] = useState(false);
  const [rtlCache, setRtlCache] = useState(null);
  const { pathname } = useLocation();
  
  // Cache for the rtl
  useMemo(() => {
    const cacheRtl = createCache({
      key: "rtl",
      stylisPlugins: [rtlPlugin],
    });

    setRtlCache(cacheRtl);
  }, []);

  // Open sidenav when mouse enter on mini sidenav
  const handleOnMouseEnter = () => {
    if (miniSidenav && !onMouseEnter) {
      setMiniSidenav(dispatch, false);
      setOnMouseEnter(true);
    }
  };

  // Close sidenav when mouse leave mini sidenav
  const handleOnMouseLeave = () => {
    if (onMouseEnter) {
      setMiniSidenav(dispatch, true);
      setOnMouseEnter(false);
    }
  };

  // Change the openConfigurator state
  const handleConfiguratorOpen = () => setOpenConfigurator(dispatch, !openConfigurator);

  // Setting the dir attribute for the body element
  useEffect(() => {
    document.body.setAttribute("dir", direction);
  }, [direction]);

  // Setting page scroll to 0 when changing the route
  useEffect(() => {
    document.documentElement.scrollTop = 0;
    document.scrollingElement.scrollTop = 0;
  }, [pathname]);

  // Filter routes to separate authentication routes from the rest
  const authRoutes = routes.filter(route => route.route?.startsWith("/authentication"));
  const appRoutes = routes.filter(route => !route.route?.startsWith("/authentication"));

  const getProtectedRoutes = (allRoutes) =>
    allRoutes.map((route) => {
      if (route.collapse) {
        return getProtectedRoutes(route.collapse);
      }

      if (route.route) {
        return <ProtectedRoute exact path={route.route} component={route.component} key={route.key} />;
      }

      return null;
    });

  const getAuthRoutes = (allRoutes) =>
    allRoutes.map((route) => {
      if (route.collapse) {
        return getAuthRoutes(route.collapse);
      }

      if (route.route) {
        return <Route exact path={route.route} component={route.component} key={route.key} />;
      }

      return null;
    });

  const configsButton = (
    <VuiBox
      display="flex"
      justifyContent="center"
      alignItems="center"
      width="3.5rem"
      height="3.5rem"
      bgColor="info"
      shadow="sm"
      borderRadius="50%"
      position="fixed"
      right="2rem"
      bottom="2rem"
      zIndex={99}
      color="white"
      sx={{ cursor: "pointer" }}
      onClick={handleConfiguratorOpen}
    >
      <Icon fontSize="default" color="inherit">
        settings
      </Icon>
    </VuiBox>
  );

  return (
    <AuthProvider>
      <IntegrationProvider>
        {/* Route change handler to refresh integrations on navigation */}
        <RouteChangeHandler />
        
        {direction === "rtl" ? (
          <CacheProvider value={rtlCache}>
            <ThemeProvider theme={themeRTL}>
              <CssBaseline />
              {layout === "dashboard" && (
                <>
                  <Sidenav
                    color={sidenavColor}
                    brand=""
                    brandName="Insyte Dashboard"
                    routes={routes}
                    onMouseEnter={handleOnMouseEnter}
                    onMouseLeave={handleOnMouseLeave}
                  />
                  <Configurator />
                  {configsButton}
                </>
              )}
              {layout === "vr" && <Configurator />}
              <Switch>
                {/* Auth routes */}
                <Route exact path="/authentication/login" component={Login} />
                <Route exact path="/authentication/register" component={Register} />
                
                {/* Protected routes */}
                {getProtectedRoutes(appRoutes)}
                
                {/* Default redirect */}
                <Route path="/authentication" render={() => <Redirect to="/authentication/login" />} />
                <Route path="*" render={() => <Redirect to="/dashboard" />} />
              </Switch>
              
              {/* Toast notifications container */}
              <ToastContainer
                position="top-right"
                autoClose={5000}
                hideProgressBar={false}
                newestOnTop
                closeOnClick
                rtl={false}
                pauseOnFocusLoss
                draggable
                pauseOnHover
                theme="dark"
              />
            </ThemeProvider>
          </CacheProvider>
        ) : (
          <ThemeProvider theme={theme}>
            <CssBaseline />
            {layout === "dashboard" && (
              <>
                <Sidenav
                  color={sidenavColor}
                  brand=""
                  brandName="Insyte Dashboard"
                  routes={routes}
                  onMouseEnter={handleOnMouseEnter}
                  onMouseLeave={handleOnMouseLeave}
                />
                <Configurator />
                {configsButton}
              </>
            )}
            {layout === "vr" && <Configurator />}
            <Switch>
              {/* Auth routes */}
              <Route exact path="/authentication/login" component={Login} />
              <Route exact path="/authentication/register" component={Register} />
              
              {/* Protected routes */}
              {getProtectedRoutes(appRoutes)}
              
              {/* Default redirect */}
              <Route path="/authentication" render={() => <Redirect to="/authentication/login" />} />
              <Route path="*" render={() => <Redirect to="/dashboard" />} />
            </Switch>
            
            {/* Toast notifications container */}
            <ToastContainer
              position="top-right"
              autoClose={5000}
              hideProgressBar={false}
              newestOnTop
              closeOnClick
              rtl={false}
              pauseOnFocusLoss
              draggable
              pauseOnHover
              theme="dark"
            />
          </ThemeProvider>
        )}
      </IntegrationProvider>
    </AuthProvider>
  );
}
