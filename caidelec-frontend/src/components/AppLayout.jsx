import { Link, useLocation } from "react-router-dom";
import { canAccessPath, getCurrentUser, logout } from "../utils/auth";
import ThemeToggle from "./ThemeToggle";
import logo from "../assets/caidelec-logo.jpeg";

const navItems = [
  { path: "/dashboard", label: "Tableau de bord" },
  { path: "/employees", label: "Employes" },
  { path: "/interventions", label: "Interventions", employeLabel: "Mes interventions" },
  { path: "/expenses", label: "Frais", employeLabel: "Mes frais" },
  { path: "/reports", label: "Rapports", employeLabel: "Mes rapports" },
];

function AppLayout({ title, children }) {
  const location = useLocation();
  const user = getCurrentUser();
  const visibleNavItems = navItems.filter((item) => canAccessPath(user.role, item.path));

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <img className="brand-logo" src={logo} alt="CAIDELEC" />
        </div>

        <nav className="nav-list">
          {visibleNavItems.map((item) => (
            <Link
              key={item.path}
              className={location.pathname === item.path ? "nav-link active" : "nav-link"}
              to={item.path}
            >
              {user.role === "employe" && item.employeLabel ? item.employeLabel : item.label}
            </Link>
          ))}
        </nav>

        <button className="ghost-button logout-button" onClick={logout}>
          Se deconnecter
        </button>
      </aside>

      <main className="main-panel">
        <header className="topbar">
          <div>
            <h1>{title}</h1>
          </div>

          <div className="topbar-actions">
            <ThemeToggle />
            <div className="user-chip">
              <span className="user-icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" role="img">
                  <path d="M12 12a4 4 0 1 0-4-4 4 4 0 0 0 4 4Zm0 2c-4.2 0-7 2.1-7 5v1h14v-1c0-2.9-2.8-5-7-5Z" />
                </svg>
              </span>
              <div>
                <strong>{user.username || "Utilisateur"}</strong>
              </div>
            </div>
          </div>
        </header>

        {children}
      </main>
    </div>
  );
}

export default AppLayout;
