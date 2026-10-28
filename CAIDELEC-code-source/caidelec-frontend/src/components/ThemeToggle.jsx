import { useEffect, useState } from "react";

function getSavedTheme() {
  return localStorage.getItem("theme") || "light";
}

function ThemeToggle() {
  const [theme, setTheme] = useState(getSavedTheme);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("theme", theme);
  }, [theme]);

  const nextTheme = theme === "light" ? "dark" : "light";

  return (
    <button
      type="button"
      className="theme-toggle"
      aria-label={`Switch to ${nextTheme} mode`}
      title={`Switch to ${nextTheme} mode`}
      onClick={() => setTheme(nextTheme)}
    >
      <span aria-hidden="true">{theme === "light" ? "☀" : "☾"}</span>
    </button>
  );
}

export default ThemeToggle;
