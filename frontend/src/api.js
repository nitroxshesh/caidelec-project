const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

async function request(path, token, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Erreur inconnue" }));
    throw new Error(error.detail ?? "Erreur inconnue");
  }

  return response.json();
}

export function login(email, password) {
  return request("/api/auth/login", null, {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export const api = {
  employees: (token) => request("/api/employees", token),
  planning: (token) => request("/api/planning", token),
  expenses: (token) => request("/api/expenses", token),
  createEmployee: (token, payload) =>
    request("/api/employees", token, { method: "POST", body: JSON.stringify(payload) }),
  createIntervention: (token, payload) =>
    request("/api/planning", token, { method: "POST", body: JSON.stringify(payload) }),
  createExpense: (token, payload) =>
    request("/api/expenses", token, { method: "POST", body: JSON.stringify(payload) }),
  monthlyReport: (token, year, month) =>
    request(`/api/reports/monthly?year=${year}&month=${month}`, token),
};
