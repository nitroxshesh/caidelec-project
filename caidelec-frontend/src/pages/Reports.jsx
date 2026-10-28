import { useEffect, useMemo, useState } from "react";
import AppLayout from "../components/AppLayout";
import api from "../services/api";
import { getCurrentUser } from "../utils/auth";

function getMonthStart() {
  const date = new Date();
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-01`;
}

function getMonthEnd() {
  const date = new Date();
  return new Date(date.getFullYear(), date.getMonth() + 1, 0).toISOString().slice(0, 10);
}

function formatMoney(value) {
  return `${Number(value || 0).toFixed(0)} DH`;
}

function getStatusLabel(status) {
  const labels = {
    planned: "Planifiee",
    a_verifier: "A verifier",
    verifie: "Verifie",
    verifiee: "Verifiee",
    terminee: "Terminee",
  };

  return labels[status] || status || "Non defini";
}

function Reports() {
  const user = getCurrentUser();
  const [startDate, setStartDate] = useState(getMonthStart());
  const [endDate, setEndDate] = useState(getMonthEnd());
  const [report, setReport] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const headers = useMemo(
    () => ({ Authorization: `Bearer ${user.token}` }),
    [user.token]
  );

  async function loadReport() {
    setLoading(true);
    setError("");

    try {
      const response = await api.get("/reports/summary", {
        headers,
        params: {
          start_date: startDate || undefined,
          end_date: endDate || undefined,
        },
      });

      setReport(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Impossible de charger le rapport.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadReport();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function exportCsv() {
    if (!report) return;

    const lines = [
      ["Rapport CAIDELEC"],
      ["Periode", startDate, endDate],
      [],
      ["Indicateur", "Valeur"],
      ["Employes", report.totals.employees_count],
      ["Interventions", report.totals.interventions_count],
      ["Frais", report.totals.expenses_count],
      ["Transport", report.totals.total_transport],
      ["Repas", report.totals.total_repas],
      ["Autre", report.totals.total_autre],
      ["Total frais", report.totals.total_expenses],
      [],
      ["Frais par employe"],
      ["Employe", "Total"],
      ...report.expenses_by_employee.map((item) => [item.employee_name, item.total]),
      [],
      ["Frais par intervention"],
      ["Intervention", "Chantier", "Employe", "Total"],
      ...report.expenses_by_intervention.map((item) => [
        item.intervention_id,
        item.chantier,
        item.employee_name,
        item.total,
      ]),
    ];

    const csv = lines
      .map((row) => row.map((cell) => `"${String(cell ?? "").replace(/"/g, '""')}"`).join(";"))
      .join("\n");

    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `rapport-caidelec-${startDate || "debut"}-${endDate || "fin"}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <AppLayout title={user.role === "admin" ? "Rapports" : "Mes rapports"}>
      {error && <div className="alert">{error}</div>}

      <section className="panel report-filters">
        <label>
          Date debut
          <input type="date" value={startDate} onChange={(event) => setStartDate(event.target.value)} />
        </label>

        <label>
          Date fin
          <input type="date" value={endDate} onChange={(event) => setEndDate(event.target.value)} />
        </label>

        <button type="button" className="primary-button" onClick={loadReport} disabled={loading}>
          {loading ? "Chargement..." : "Afficher"}
        </button>

        <button type="button" className="ghost-button" onClick={exportCsv} disabled={!report}>
          Exporter CSV
        </button>
      </section>

      {report && (
        <>
          <section className="stats-grid section-panel">
            <article className="stat-card">
              <span>Employes</span>
              <strong>{report.totals.employees_count}</strong>
            </article>
            <article className="stat-card">
              <span>Interventions</span>
              <strong>{report.totals.interventions_count}</strong>
            </article>
            <article className="stat-card">
              <span>Total frais</span>
              <strong>{formatMoney(report.totals.total_expenses)}</strong>
            </article>
          </section>

          <section className="stats-grid section-panel">
            <article className="stat-card">
              <span>Transport</span>
              <strong>{formatMoney(report.totals.total_transport)}</strong>
            </article>
            <article className="stat-card">
              <span>Repas</span>
              <strong>{formatMoney(report.totals.total_repas)}</strong>
            </article>
            <article className="stat-card">
              <span>Autre</span>
              <strong>{formatMoney(report.totals.total_autre)}</strong>
            </article>
          </section>

          <section className="content-grid section-panel">
            <article className="panel">
              <div className="panel-header">
                <h2>Interventions par statut</h2>
              </div>
              <div className="report-bars">
                {report.interventions_by_status.length === 0 ? (
                  <p className="empty-state">Aucune intervention.</p>
                ) : (
                  report.interventions_by_status.map((item) => (
                    <div key={item.status} className="report-bar-row">
                      <span>{getStatusLabel(item.status)}</span>
                      <strong>{item.count}</strong>
                    </div>
                  ))
                )}
              </div>
            </article>

            <article className="panel">
              <div className="panel-header">
                <h2>Frais par statut</h2>
              </div>
              <div className="report-bars">
                {report.expenses_by_status.length === 0 ? (
                  <p className="empty-state">Aucun frais.</p>
                ) : (
                  report.expenses_by_status.map((item) => (
                    <div key={item.status} className="report-bar-row">
                      <span>{getStatusLabel(item.status)}</span>
                      <strong>{item.count}</strong>
                    </div>
                  ))
                )}
              </div>
            </article>
          </section>

          <section className="panel section-panel">
            <div className="panel-header">
              <h2>Frais par employe</h2>
            </div>

            <div className="data-table">
              <div className="table-row report-two-cols table-head">
                <span>Employe</span>
                <span>Total</span>
              </div>
              {report.expenses_by_employee.length === 0 ? (
                <p className="empty-state">Aucun frais.</p>
              ) : (
                report.expenses_by_employee.map((item) => (
                  <div key={item.employee_id || item.employee_name} className="table-row report-two-cols">
                    <span>{item.employee_name}</span>
                    <strong>{formatMoney(item.total)}</strong>
                  </div>
                ))
              )}
            </div>
          </section>

          <section className="panel section-panel">
            <div className="panel-header">
              <h2>Frais par intervention</h2>
            </div>

            <div className="data-table">
              <div className="table-row report-four-cols table-head">
                <span>ID</span>
                <span>Chantier</span>
                <span>Employe</span>
                <span>Total</span>
              </div>
              {report.expenses_by_intervention.length === 0 ? (
                <p className="empty-state">Aucun frais.</p>
              ) : (
                report.expenses_by_intervention.map((item) => (
                  <div key={item.intervention_id} className="table-row report-four-cols">
                    <span>#{item.intervention_id}</span>
                    <span>{item.chantier}</span>
                    <span>{item.employee_name}</span>
                    <strong>{formatMoney(item.total)}</strong>
                  </div>
                ))
              )}
            </div>
          </section>
        </>
      )}
    </AppLayout>
  );
}

export default Reports;
