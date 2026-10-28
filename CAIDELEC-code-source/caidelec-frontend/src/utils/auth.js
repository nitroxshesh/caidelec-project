export function normalizeRole(role) {
  return role === "admin" ? "admin" : "employe";
}

export function getCurrentUser() {
  const token = localStorage.getItem("token");

  if (!token) {
    return { token: null, username: "", role: "employe", employee_id: null };
  }

  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return {
      token,
      username: payload.sub || "",
      role: normalizeRole(payload.role || "employe"),
      employee_id: payload.employee_id || null,
    };
  } catch {
    return { token, username: "", role: "employe", employee_id: null };
  }
}

export const roleAccess = {
  admin: ["/dashboard", "/employees", "/interventions", "/expenses"],
  employe: ["/dashboard", "/interventions", "/expenses"],
};

export function canAccessPath(role, path) {
  return (roleAccess[normalizeRole(role)] || roleAccess.employe).includes(path);
}

export function getAllowedPaths(role) {
  return roleAccess[normalizeRole(role)] || roleAccess.employe;
}

export function logout() {
  localStorage.removeItem("token");
  window.location.href = "/";
}
