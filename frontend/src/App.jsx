import {
  CalendarDays,
  CircleDollarSign,
  ClipboardList,
  LogOut,
  ShieldCheck,
  Sparkles,
  UserRound,
  Users,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { api, login } from "./api.js";

const demoAccounts = [
  { label: "Admin", role: "admin", email: "admin@caidelec.local", password: "admin123", icon: ShieldCheck },
  { label: "Reception", role: "reception", email: "reception@caidelec.local", password: "reception123", icon: UserRound },
  { label: "Comptable", role: "comptable", email: "comptable@caidelec.local", password: "comptable123", icon: CircleDollarSign },
  { label: "Manager", role: "manager", email: "manager@caidelec.local", password: "manager123", icon: ClipboardList },
];

const statusLabel = {
  active: "Disponible",
  on_leave: "Conge",
  sick: "Maladie",
  absent: "Absent",
  planned: "Planifiee",
  in_progress: "En cours",
  done: "Terminee",
  cancelled: "Annulee",
  draft: "Brouillon",
  validated: "Validee",
  exported: "Exportee",
};

const roleLabel = {
  admin: "Espace administrateur",
  reception: "Espace reception",
  comptable: "Espace comptabilite",
  manager: "Espace manager",
};

export function App() {
  const [session, setSession] = useState(() => {
    const saved = localStorage.getItem("caidelec-session");
    return saved ? JSON.parse(saved) : null;
  });
  const [email, setEmail] = useState("admin@caidelec.local");
  const [password, setPassword] = useState("admin123");
  const [error, setError] = useState("");
  const [employees, setEmployees] = useState([]);
  const [planning, setPlanning] = useState([]);
  const [expenses, setExpenses] = useState([]);
  const [report, setReport] = useState(null);
  const [employeeForm, setEmployeeForm] = useState({ full_name: "", function: "", phone: "", status: "active" });
  const [interventionForm, setInterventionForm] = useState({
    intervention_date: new Date().toISOString().slice(0, 10),
    client: "",
    site: "",
    mission: "",
    employee_id: 0,
    status: "planned",
    notes: "",
  });
  const [expenseForm, setExpenseForm] = useState({
    intervention_id: 0,
    distance_km: 0,
    transport_amount: 0,
    meal_amount: 0,
    other_amount: 0,
    status: "draft",
  });

  const role = session?.role;
  const canManageEmployees = ["admin", "manager"].includes(role);
  const canCreatePlanning = ["admin", "reception", "manager"].includes(role);
  const canCreateExpense = ["admin", "reception", "comptable"].includes(role);
  const canSeeReports = ["admin", "comptable", "manager"].includes(role);

  useEffect(() => {
    if (!session) return;
    refreshData(session).catch((err) => setError(err.message));
  }, [session]);

  const kpis = useMemo(
    () => [
      { label: "Interventions", value: planning.length, icon: ClipboardList },
      { label: "Employes actifs", value: employees.filter((item) => item.status === "active").length, icon: Users },
      { label: "Frais du mois", value: `${report?.total_expenses?.toFixed(2) ?? "0.00"} MAD`, icon: CircleDollarSign },
      { label: "Distance", value: `${report?.total_distance_km?.toFixed(0) ?? "0"} km`, icon: CalendarDays },
    ],
    [employees, planning, report]
  );

  async function refreshData(activeSession = session) {
    if (!activeSession) return;
    const now = new Date();
    const [employeeRows, planningRows, expenseRows, reportData] = await Promise.all([
      api.employees(activeSession.access_token),
      api.planning(activeSession.access_token),
      api.expenses(activeSession.access_token),
      api.monthlyReport(activeSession.access_token, now.getFullYear(), now.getMonth() + 1),
    ]);
    setEmployees(employeeRows);
    setPlanning(planningRows);
    setExpenses(expenseRows);
    setReport(reportData);
    setInterventionForm((form) => ({ ...form, employee_id: employeeRows[0]?.id ?? 0 }));
    setExpenseForm((form) => ({ ...form, intervention_id: planningRows[0]?.id ?? 0 }));
  }

  async function handleLogin(event) {
    event.preventDefault();
    setError("");
    try {
      const nextSession = await login(email, password);
      localStorage.setItem("caidelec-session", JSON.stringify(nextSession));
      setSession(nextSession);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Connexion impossible");
    }
  }

  function useDemoAccount(account) {
    setEmail(account.email);
    setPassword(account.password);
  }

  function logout() {
    localStorage.removeItem("caidelec-session");
    setSession(null);
  }

  async function runAction(action) {
    setError("");
    try {
      await action();
      await refreshData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Operation impossible");
    }
  }

  async function addEmployee(event) {
    event.preventDefault();
    await runAction(async () => {
      await api.createEmployee(session.access_token, employeeForm);
      setEmployeeForm({ full_name: "", function: "", phone: "", status: "active" });
    });
  }

  async function addIntervention(event) {
    event.preventDefault();
    await runAction(async () => {
      await api.createIntervention(session.access_token, interventionForm);
      setInterventionForm((form) => ({ ...form, client: "", site: "", mission: "", notes: "" }));
    });
  }

  async function addExpense(event) {
    event.preventDefault();
    await runAction(async () => {
      await api.createExpense(session.access_token, expenseForm);
      setExpenseForm((form) => ({ ...form, distance_km: 0, transport_amount: 0, meal_amount: 0, other_amount: 0 }));
    });
  }

  if (!session) {
    return (
      <main className="login-page">
        <section className="login-panel animated-panel">
          <div className="login-copy">
            <p className="eyebrow">CAIDELEC</p>
            <h1>Gestion des plannings et frais de deplacement</h1>
            <p className="muted">Interface animee en JavaScript avec espaces separes par role.</p>
            <div className="account-switcher">
              {demoAccounts.map((account) => {
                const Icon = account.icon;
                return (
                  <button className="account-button" type="button" key={account.role} onClick={() => useDemoAccount(account)}>
                    <Icon size={18} />
                    <span>{account.label}</span>
                  </button>
                );
              })}
            </div>
          </div>
          <form onSubmit={handleLogin} className="login-form">
            <Sparkles className="form-spark" size={22} />
            <label>
              Email
              <input value={email} onChange={(event) => setEmail(event.target.value)} />
            </label>
            <label>
              Mot de passe
              <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} />
            </label>
            {error && <p className="error">{error}</p>}
            <button type="submit">Se connecter</button>
          </form>
        </section>
      </main>
    );
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div>
          <p className="eyebrow">CAIDELEC</p>
          <h1>Planning</h1>
          <span className={`role-badge role-${role}`}>{roleLabel[role]}</span>
        </div>
        <nav>
          <a href="#dashboard">Tableau de bord</a>
          <a href="#planning">Interventions</a>
          <a href="#employees">Personnel</a>
          <a href="#expenses">Frais</a>
        </nav>
      </aside>

      <section className="workspace">
        <header className="topbar animated-panel">
          <div>
            <p className="eyebrow">Connecte</p>
            <h2>{session.full_name}</h2>
          </div>
          <button className="ghost-button" onClick={logout} aria-label="Se deconnecter">
            <LogOut size={18} />
            Sortir
          </button>
        </header>

        {error && <p className="error">{error}</p>}

        <section id="dashboard" className="kpi-grid">
          {kpis.map((item, index) => {
            const Icon = item.icon;
            return (
              <article className="kpi-card animated-card" style={{ animationDelay: `${index * 80}ms` }} key={item.label}>
                <Icon size={22} />
                <span>{item.label}</span>
                <strong>{item.value}</strong>
              </article>
            );
          })}
        </section>

        <section id="planning" className="content-grid">
          <Panel title="Planning quotidien" subtitle="Affectation des equipes techniques sur les chantiers">
            <PlanningTable planning={planning} />
          </Panel>

          {canSeeReports && (
            <Panel title="Synthese mensuelle" subtitle="Donnees exportables pour la comptabilite">
              <ReportList report={report} />
            </Panel>
          )}
        </section>

        {(canCreatePlanning || canCreateExpense) && (
          <section className="content-grid compact">
            {canCreatePlanning && (
              <Panel title="Nouvelle intervention" subtitle="Saisie rapide pour la reception">
                <form className="inline-form" onSubmit={addIntervention}>
                  <input type="date" value={interventionForm.intervention_date} onChange={(event) => setInterventionForm({ ...interventionForm, intervention_date: event.target.value })} />
                  <input placeholder="Client" value={interventionForm.client} onChange={(event) => setInterventionForm({ ...interventionForm, client: event.target.value })} required />
                  <input placeholder="Site / chantier" value={interventionForm.site} onChange={(event) => setInterventionForm({ ...interventionForm, site: event.target.value })} required />
                  <input placeholder="Mission" value={interventionForm.mission} onChange={(event) => setInterventionForm({ ...interventionForm, mission: event.target.value })} required />
                  <select value={interventionForm.employee_id} onChange={(event) => setInterventionForm({ ...interventionForm, employee_id: Number(event.target.value) })}>
                    {employees.map((employee) => (
                      <option value={employee.id} key={employee.id}>{employee.full_name}</option>
                    ))}
                  </select>
                  <button type="submit">Ajouter</button>
                </form>
              </Panel>
            )}

            {canCreateExpense && (
              <Panel title="Nouveau frais" subtitle="Transport, repas et autres montants">
                <form className="inline-form" onSubmit={addExpense}>
                  <select value={expenseForm.intervention_id} onChange={(event) => setExpenseForm({ ...expenseForm, intervention_id: Number(event.target.value) })}>
                    {planning.map((item) => (
                      <option value={item.id} key={item.id}>#{item.id} - {item.client}</option>
                    ))}
                  </select>
                  <input type="number" min="0" placeholder="Distance km" value={expenseForm.distance_km} onChange={(event) => setExpenseForm({ ...expenseForm, distance_km: Number(event.target.value) })} />
                  <input type="number" min="0" placeholder="Transport" value={expenseForm.transport_amount} onChange={(event) => setExpenseForm({ ...expenseForm, transport_amount: Number(event.target.value) })} />
                  <input type="number" min="0" placeholder="Repas" value={expenseForm.meal_amount} onChange={(event) => setExpenseForm({ ...expenseForm, meal_amount: Number(event.target.value) })} />
                  <input type="number" min="0" placeholder="Autres" value={expenseForm.other_amount} onChange={(event) => setExpenseForm({ ...expenseForm, other_amount: Number(event.target.value) })} />
                  <button type="submit">Enregistrer</button>
                </form>
              </Panel>
            )}
          </section>
        )}

        <section id="employees" className="content-grid compact">
          <Panel title="Personnel" subtitle="Presence, conges, absences maladie">
            {canManageEmployees && (
              <form className="inline-form split-form" onSubmit={addEmployee}>
                <input placeholder="Nom complet" value={employeeForm.full_name} onChange={(event) => setEmployeeForm({ ...employeeForm, full_name: event.target.value })} required />
                <input placeholder="Fonction" value={employeeForm.function} onChange={(event) => setEmployeeForm({ ...employeeForm, function: event.target.value })} required />
                <input placeholder="Telephone" value={employeeForm.phone} onChange={(event) => setEmployeeForm({ ...employeeForm, phone: event.target.value })} />
                <button type="submit">Ajouter employe</button>
              </form>
            )}
            <div className="employee-grid">
              {employees.map((employee) => (
                <article className="employee-card animated-card" key={employee.id}>
                  <strong>{employee.full_name}</strong>
                  <span>{employee.function}</span>
                  <Status value={statusLabel[employee.status]} />
                </article>
              ))}
            </div>
          </Panel>

          <Panel title="Frais de deplacement" subtitle="Transport, repas et autres frais">
            <div className="expense-list">
              {expenses.map((expense) => (
                <article className="animated-card" key={expense.id}>
                  <span>Intervention #{expense.intervention_id}</span>
                  <strong>{Number(expense.total_amount).toFixed(2)} MAD</strong>
                  <small>{expense.distance_km} km</small>
                </article>
              ))}
            </div>
          </Panel>
        </section>
      </section>
    </main>
  );
}

function PlanningTable({ planning }) {
  return (
    <div className="table">
      <div className="table-row table-head">
        <span>Date</span>
        <span>Client / site</span>
        <span>Technicien</span>
        <span>Statut</span>
      </div>
      {planning.map((item) => (
        <div className="table-row animated-row" key={item.id}>
          <span>{item.intervention_date}</span>
          <span>
            <strong>{item.client}</strong>
            <small>{item.site}</small>
          </span>
          <span>{item.employee.full_name}</span>
          <Status value={statusLabel[item.status]} />
        </div>
      ))}
    </div>
  );
}

function ReportList({ report }) {
  return (
    <dl className="report-list">
      <div>
        <dt>Mois</dt>
        <dd>{report?.month ?? "-"}</dd>
      </div>
      <div>
        <dt>Interventions</dt>
        <dd>{report?.total_interventions ?? 0}</dd>
      </div>
      <div>
        <dt>Pieces frais</dt>
        <dd>{report?.exported_items ?? 0}</dd>
      </div>
      <div>
        <dt>Total</dt>
        <dd>{report?.total_expenses?.toFixed(2) ?? "0.00"} MAD</dd>
      </div>
    </dl>
  );
}

function Panel({ title, subtitle, children }) {
  return (
    <section className="panel animated-panel">
      <header>
        <h3>{title}</h3>
        <p>{subtitle}</p>
      </header>
      {children}
    </section>
  );
}

function Status({ value }) {
  return <span className="status-pill">{value}</span>;
}
