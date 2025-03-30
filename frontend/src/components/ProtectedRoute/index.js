import { Route, Redirect } from "react-router-dom";
import { useAuth } from "context/auth";

// Protected route component
const ProtectedRoute = ({ component: Component, ...rest }) => {
  const { isAuthenticated, loading } = useAuth();

  return (
    <Route
      {...rest}
      render={(props) => {
        // If still loading authentication state, don't render anything yet
        if (loading) {
          return <div>Loading...</div>;
        }

        // If authenticated, render the component
        if (isAuthenticated) {
          return <Component {...props} />;
        }

        // If not authenticated, redirect to login
        return (
          <Redirect
            to={{
              pathname: "/authentication/login",
              state: { from: props.location },
            }}
          />
        );
      }}
    />
  );
};

export default ProtectedRoute; 