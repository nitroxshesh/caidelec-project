import { BrowserRouter, Navigate, Routes, Route } from "react-router-dom";

import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Employees from "./pages/Employees";
import Interventions from "./pages/Interventions";
import InterventionDayDetails from "./pages/InterventionDayDetails";
import Expenses from "./pages/Expenses";
import { canAccessPath, getCurrentUser } from "./utils/auth";

function ProtectedRoute({ path, children }) {
  const user = getCurrentUser();

  if (!user.token) {
    return <Navigate to="/" replace />;
  }

  if (!canAccessPath(user.role, path)) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute path="/dashboard">
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/employees"
          element={
            <ProtectedRoute path="/employees">
              <Employees />
            </ProtectedRoute>
          }
        />
        <Route
          path="/interventions"
          element={
            <ProtectedRoute path="/interventions">
              <Interventions />
            </ProtectedRoute>
          }
        />
        <Route
          path="/interventions/date/:date"
          element={
            <ProtectedRoute path="/interventions">
              <InterventionDayDetails />
            </ProtectedRoute>
          }
        />
        <Route
          path="/expenses"
          element={
            <ProtectedRoute path="/expenses">
              <Expenses />
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
