import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import AppLayout from "../components/AppLayout";
import api from "../services/api";
import { getCurrentUser } from "../utils/auth";

function Interventions() {
  const [interventions, setInterventions] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [employeeId, setEmployeeId] = useState("");
  const [chantier, setChantier] = useState("");
  const [natureTravaux, setNatureTravaux] = useState("");
  const [observation, setObservation] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [error, setError] = useState("");
  const [editingInterventionId, setEditingInterventionId] = useState(null);
  const [searchParams] = useSearchParams();
  const user = getCurrentUser();
  const canManage = user.role === "admin";
  const canDeclareDone = user.role === "employe";
  const showActions = canManage || canDeclareDone;
  const selectedDate = searchParams.get("date") || "";

  const loadInterventions = async () => {
    try {
      const response = await api.get("/interventions", {
        headers: { Authorization: `Bearer ${user.token}` },
      });
      setInterventions(response.data);
    } catch {
      setError("Impossible de charger les interventions.");
    }
  };

  const getEmployeeLabel = (employeeIdValue) => {
    const employee = employees.find((item) => item.id === employeeIdValue);
    return employee ? `${employee.full_name} (${employee.role})` : `#${employeeIdValue}`;
  };

  useEffect(() => {
    if (!user.token) {
      window.location.href = "/";
      return;
    }

    let active = true;

    const headers = { Authorization: `Bearer ${user.token}` };

    const requests = [api.get("/interventions", { headers })];

    if (canManage) {
      requests.push(api.get("/employees", { headers }));
    }

    Promise.all(requests)
      .then(([interventionsResponse, employeesResponse]) => {
        if (active) {
          setInterventions(interventionsResponse.data);
          setEmployees(employeesResponse?.data || []);
        }
      })
      .catch(() => {
        if (active) {
          setError("Impossible de charger les interventions.");
        }
      });

    return () => {
      active = false;
    };
  }, [canManage, user.token]);

  const resetForm = () => {
    setEmployeeId("");
    setChantier("");
    setNatureTravaux("");
    setObservation("");
    setStartDate("");
    setEndDate("");
    setEditingInterventionId(null);
  };

  const saveIntervention = async (event) => {
    event.preventDefault();
    setError("");

    try {
      const payload = {
        employee_id: Number(employeeId),
        chantier,
        nature_travaux: natureTravaux,
        observation,
        start_date: startDate,
        end_date: endDate,
        status: "planned",
      };

      if (editingInterventionId) {
        await api.put(
          `/interventions/${editingInterventionId}`,
          payload,
          { headers: { Authorization: `Bearer ${user.token}` } }
        );
      } else {
        await api.post(
          "/interventions",
          payload,
          { headers: { Authorization: `Bearer ${user.token}` } }
        );
      }

      resetForm();
      loadInterventions();
    } catch {
      setError("L'enregistrement de l'intervention a echoue.");
    }
  };

  const editIntervention = (intervention) => {
    setEditingInterventionId(intervention.id);
    setEmployeeId(String(intervention.employee_id));
    setChantier(intervention.chantier);
    setNatureTravaux(intervention.nature_travaux || "");
    setObservation(intervention.observation || "");
    setStartDate(intervention.start_date);
    setEndDate(intervention.end_date);
  };

  const deleteIntervention = async (interventionId) => {
    if (!window.confirm("Supprimer cette intervention ?")) {
      return;
    }

    setError("");

    try {
      await api.delete(
        `/interventions/${interventionId}`,
        {
          headers: { Authorization: `Bearer ${user.token}` },
        }
      );

      if (editingInterventionId === interventionId) {
        resetForm();
      }

      loadInterventions();
    } catch {
      setError("La suppression de l'intervention a echoue.");
    }
  };

  const declareDone = async (interventionId) => {
    setError("");

    try {
      await api.patch(
        `/interventions/${interventionId}/declare-done`,
        {},
        { headers: { Authorization: `Bearer ${user.token}` } }
      );
      loadInterventions();
    } catch {
      setError("La declaration de l'intervention a echoue.");
    }
  };

  const verifyIntervention = async (interventionId) => {
    setError("");

    try {
      await api.patch(
        `/interventions/${interventionId}/verify`,
        {},
        { headers: { Authorization: `Bearer ${user.token}` } }
      );
      loadInterventions();
    } catch {
      setError("La verification de l'intervention a echoue.");
    }
  };

  const getStatusLabel = (status) => {
    if (status === "a_verifier") return "A verifier";
    if (status === "verifiee") return "Verifiee";
    if (status === "planned") return "Planifiee";
    return status;
  };

  const visibleInterventions = selectedDate
    ? interventions.filter(
        (intervention) =>
          intervention.start_date <= selectedDate && intervention.end_date >= selectedDate
      )
    : interventions;

  return (
    <AppLayout
      title={user.role === "employe" ? "Mes interventions" : "Interventions"}
    >
      {error && <div className="alert">{error}</div>}

      <section className={canManage ? "content-grid" : "content-grid single-column"}>
        {canManage && (
          <form className="panel form-panel" onSubmit={saveIntervention}>
          <label>
            Employe
            <select
              value={employeeId}
              onChange={(event) => setEmployeeId(event.target.value)}
              required
            >
              <option value="">Choisir un employe</option>
              {employees.map((employee) => (
                <option key={employee.id} value={employee.id}>
                  {employee.full_name} - {employee.role}
                </option>
              ))}
            </select>
          </label>

          <label>
            Chantier
            <input
              value={chantier}
              onChange={(event) => setChantier(event.target.value)}
              required
            />
          </label>

          <label>
            Nature des travaux
            <input
              value={natureTravaux}
              onChange={(event) => setNatureTravaux(event.target.value)}
            />
          </label>

          <label>
            Observation
            <input
              value={observation}
              onChange={(event) => setObservation(event.target.value)}
            />
          </label>

          <label>
            Date debut
            <input
              type="date"
              value={startDate}
              onChange={(event) => setStartDate(event.target.value)}
              required
            />
          </label>

          <label>
            Date fin
            <input
              type="date"
              value={endDate}
              onChange={(event) => setEndDate(event.target.value)}
              required
            />
          </label>

          <div className="button-row">
            <button className="primary-button">
              {editingInterventionId ? "Enregistrer" : "Planifier"}
            </button>
            {editingInterventionId && (
              <button type="button" className="ghost-button" onClick={resetForm}>
                Annuler
              </button>
            )}
          </div>
          </form>
        )}

        <div className="panel table-panel">
          {selectedDate && (
            <div className="filter-bar">
              <h2>{selectedDate}</h2>
              <Link className="secondary-button" to="/interventions">
                Tout afficher
              </Link>
            </div>
          )}

          <div className="data-table">
            <div className={showActions ? "table-row table-head seven-cols" : "table-row table-head six-cols"}>
              <span>ID</span>
              <span>Employe</span>
              <span>Chantier</span>
              <span>Nature</span>
              <span>Periode</span>
              <span>Statut</span>
              {showActions && <span>Actions</span>}
            </div>
            {visibleInterventions.length === 0 ? (
              <p className="empty-state">Aucune intervention planifiee.</p>
            ) : (
              visibleInterventions.map((intervention) => (
                <div key={intervention.id} className={showActions ? "table-row seven-cols" : "table-row six-cols"}>
                  <span>#{intervention.id}</span>
                  <span>{getEmployeeLabel(intervention.employee_id)}</span>
                  <span>
                    <Link className="text-link" to={`/interventions/date/${intervention.start_date}`}>
                      {intervention.chantier}
                    </Link>
                  </span>
                  <span>{intervention.nature_travaux || "-"}</span>
                  <span>
                    <Link className="text-link" to={`/interventions/date/${intervention.start_date}`}>
                      {intervention.start_date} - {intervention.end_date}
                    </Link>
                  </span>
                  <span className="status-pill">{getStatusLabel(intervention.status)}</span>
                  {showActions && (
                    <span className="actions-cell">
                      {canManage && (
                        <>
                          <button
                            type="button"
                            className="secondary-button"
                            onClick={() => editIntervention(intervention)}
                          >
                            Modifier
                          </button>
                          <button
                            type="button"
                            className="secondary-button"
                            onClick={() => verifyIntervention(intervention.id)}
                          >
                            Verifier
                          </button>
                          <button
                            type="button"
                            className="danger-button"
                            onClick={() => deleteIntervention(intervention.id)}
                          >
                            Supprimer
                          </button>
                        </>
                      )}
                      {canDeclareDone && intervention.status !== "verifiee" && (
                        <button
                          type="button"
                          className="secondary-button"
                          onClick={() => declareDone(intervention.id)}
                        >
                          Declarer realisee
                        </button>
                      )}
                    </span>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </section>
    </AppLayout>
  );
}

export default Interventions;
