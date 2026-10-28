import { useState } from "react";
import ThemeToggle from "../components/ThemeToggle";
import api from "../services/api";
import logo from "../assets/caidelec-logo.jpeg";

function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (event) => {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await api.post("/auth/login", {
        username,
        password,
      });

      localStorage.setItem("token", response.data.access_token);
      window.location.href = "/dashboard";
    } catch {
      setError("Identifiants incorrects.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="login-page">
      <section className="login-visual">
        <div className="login-theme">
          <ThemeToggle />
        </div>

        <div className="brand large">
          <img className="brand-logo login-logo" src={logo} alt="CAIDELEC" />
        </div>

        <div className="login-copy">
          <h1>Système de gestion de la planification des interventions quotidiennes et les frais de leurs déplacements</h1>
        </div>
      </section>

      <section className="login-card">
        <form onSubmit={handleLogin}>
          {error && <div className="alert">{error}</div>}

          <label>
            Nom utilisateur
            <input
              type="text"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              autoComplete="username"
            />
          </label>

          <label>
            Mot de passe
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              autoComplete="current-password"
            />
          </label>

          <button className="primary-button" disabled={loading}>
            {loading ? "Connexion..." : "Se connecter"}
          </button>
        </form>
      </section>
    </main>
  );
}

export default Login;
