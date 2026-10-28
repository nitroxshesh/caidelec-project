import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import AppLayout from "../components/AppLayout";
import api from "../services/api";
import { canAccessPath, getCurrentUser } from "../utils/auth";

function Dashboard() {
  const [employees, setEmployees] = useState([]);
  const [interventions, setInterventions] = useState([]);
  const [expenses, setExpenses] = useState([]);
  const [error, setError] = useState("");
  const [calendarDate, setCalendarDate] = useState(new Date());
  const user = getCurrentUser();
  const canViewEmployees = canAccessPath(user.role, "/employees");
  const canViewInterventions = canAccessPath(user.role, "/interventions");
  const canViewExpenses = canAccessPath(user.role, "/expenses");

  useEffect(() => {
    if (!user.token) {
      window.location.href = "/";
      return;
    }

    async function loadDashboard() {
      const headers = { Authorization: `Bearer ${user.token}` };
      const requests = [];

      if (canViewEmployees) {
        requests.push(api.get("/employees", { headers }).then((response) => setEmployees(response.data)));
      }

      if (canViewInterventions) {
        requests.push(api.get("/interventions", { headers }).then((response) => setInterventions(response.data)));
      }

      if (canViewExpenses) {
        requests.push(api.get("/expenses", { headers }).then((response) => setExpenses(response.data)));
      }

      const results = await Promise.allSettled(requests);
      const allRequestsFailed = results.length > 0 && results.every((result) => result.status === "rejected");

      if (allRequestsFailed) {
        setError("Impossible de charger les donnees du tableau de bord.");
      }
    }

    loadDashboard();
  }, [canViewEmployees, canViewExpenses, canViewInterventions, user.token]);

  const totalExpenses = useMemo(
    () =>
      expenses.reduce(
        (sum, expense) => sum + expense.transport + expense.repas + expense.autre,
        0
      ),
    [expenses]
  );

  const quickLinks = [
    { path: "/interventions", label: "Planning" },
    { path: "/employees", label: "Equipe" },
    { path: "/expenses", label: "Frais" },
  ].filter((link) => canAccessPath(user.role, link.path));

  const toDateKey = (date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
  };

  const today = toDateKey(new Date());
  const currentYear = calendarDate.getFullYear();
  const currentMonth = calendarDate.getMonth();
  const monthLabel = calendarDate.toLocaleDateString("fr-FR", {
    month: "long",
    year: "numeric",
  });
  const weekdayLabels = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"];
  const firstDay = new Date(currentYear, currentMonth, 1);
  const lastDay = new Date(currentYear, currentMonth + 1, 0);
  const calendarStartOffset = (firstDay.getDay() + 6) % 7;
  const calendarDays = Array.from(
    { length: calendarStartOffset + lastDay.getDate() },
    (_, index) => {
      if (index < calendarStartOffset) {
        return null;
      }

      const day = index - calendarStartOffset + 1;
      const date = new Date(currentYear, currentMonth, day);

      return { day, dateKey: toDateKey(date) };
    }
  );

  const employeeNameById = (employeeId) => {
    const employee = employees.find((item) => item.id === employeeId);
    return employee ? employee.full_name : `Employe #${employeeId}`;
  };

  const getInterventionsForDate = (dateKey) =>
    interventions.filter(
      (intervention) => intervention.start_date <= dateKey && intervention.end_date >= dateKey
    );

  const getStatusLabel = (status) => {
    if (status === "a_verifier") return "A verifier";
    if (status === "verifiee") return "Verifiee";
    if (status === "planned") return "Planifiee";
    return status;
  };

  const changeMonth = (offset) => {
    setCalendarDate(new Date(currentYear, currentMonth + offset, 1));
  };

  return (
    <AppLayout title="Tableau de bord">
      {error && <div className="alert">{error}</div>}

      <section className="stats-grid">
        {canViewEmployees && (
          <article className="stat-card">
            <span>Employes</span>
            <strong>{employees.length}</strong>
          </article>
        )}
        {canViewInterventions && (
          <article className="stat-card">
            <span>Interventions</span>
            <strong>{interventions.length}</strong>
          </article>
        )}
        {canViewExpenses && (
          <article className="stat-card">
            <span>Frais</span>
            <strong>{totalExpenses.toFixed(0)} DH</strong>
          </article>
        )}
      </section>

      <section className="panel">
        <div className="quick-links">
          {quickLinks.map((link) => (
            <Link key={link.path} to={link.path}>
              {link.label}
            </Link>
          ))}
        </div>
      </section>

      {canViewInterventions && (
        <section className="panel calendar-panel">
          <div className="calendar-toolbar">
            <button type="button" className="calendar-nav-button" onClick={() => changeMonth(-1)}>
              {"<"}
            </button>
            <h2>{monthLabel}</h2>
            <button type="button" className="calendar-nav-button" onClick={() => changeMonth(1)}>
              {">"}
            </button>
          </div>

          <div className="calendar-grid">
            {weekdayLabels.map((weekday) => (
              <div key={weekday} className="calendar-weekday">
                {weekday}
              </div>
            ))}

            {calendarDays.map((day, index) => {
              if (!day) {
                return <div key={`empty-${index}`} className="calendar-day empty" />;
              }

              const dayInterventions = getInterventionsForDate(day.dateKey);

              return (
                <Link
                  key={day.dateKey}
                  className={[
                    "calendar-day",
                    day.dateKey === today ? "today" : "",
                    dayInterventions.length > 0 ? "has-events" : "",
                  ].join(" ")}
                  to={`/interventions/date/${day.dateKey}`}
                >
                  <div className="calendar-day-number">{day.day}</div>

                  <div className="calendar-events">
                    {dayInterventions.slice(0, 2).map((intervention) => (
                      <div key={intervention.id} className="calendar-event">
                        <strong>{intervention.chantier}</strong>
                        <span>{employeeNameById(intervention.employee_id)} - {getStatusLabel(intervention.status)}</span>
                      </div>
                    ))}
                    {dayInterventions.length > 2 && (
                      <span className="calendar-more">+{dayInterventions.length - 2}</span>
                    )}
                  </div>
                </Link>
              );
            })}
          </div>
        </section>
      )}

      {canViewExpenses && (
        <section className="panel section-panel">
          <div className="panel-header">
            <h2>Frais</h2>
          </div>

          <div className="data-table">
            <div className="table-row table-head five-cols">
              <span>ID</span>
              <span>Intervention</span>
              <span>Transport</span>
              <span>Repas</span>
              <span>Autre</span>
            </div>
            {expenses.length === 0 ? (
              <p className="empty-state">Aucun frais declare.</p>
            ) : (
              expenses.map((expense) => (
                <div key={expense.id} className="table-row five-cols">
                  <span>#{expense.id}</span>
                  <span>#{expense.intervention_id}</span>
                  <span>{expense.transport} DH</span>
                  <span>{expense.repas} DH</span>
                  <span>{expense.autre} DH</span>
                </div>
              ))
            )}
          </div>
        </section>
      )}
    </AppLayout>
  );
}

export default Dashboard;
