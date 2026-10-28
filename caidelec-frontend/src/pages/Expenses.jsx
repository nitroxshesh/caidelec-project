import { useEffect, useMemo, useState } from "react";
import AppLayout from "../components/AppLayout";
import api from "../services/api";
import { getCurrentUser } from "../utils/auth";

function Expenses() {
  const [expenses, setExpenses] = useState([]);
  const [interventions, setInterventions] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [interventionId, setInterventionId] = useState("");
  const [transport, setTransport] = useState("");
  const [repas, setRepas] = useState("");
  const [autre, setAutre] = useState("");
  const [receiptPhoto, setReceiptPhoto] = useState("");
  const [error, setError] = useState("");
  const [editingExpenseId, setEditingExpenseId] = useState(null);
  const user = getCurrentUser();
  const isAdmin = user.role === "admin";
  const canManage = user.role === "employe";

  const loadExpenses = async () => {
    try {
      const response = await api.get("/expenses", {
        headers: { Authorization: `Bearer ${user.token}` },
      });
      setExpenses(response.data);
    } catch {
      setError("Impossible de charger les frais.");
    }
  };

  const getInterventionLabel = (interventionIdValue) => {
    const intervention = interventions.find((item) => item.id === interventionIdValue);

    if (!intervention) {
      return `#${interventionIdValue}`;
    }

    const employee = employees.find((item) => item.id === intervention.employee_id);
    const employeeName = employee ? employee.full_name : `Employe #${intervention.employee_id}`;

    return `${intervention.chantier} - ${employeeName}`;
  };

  const getStatusLabel = (status) => {
    if (status === "verifie") return "Verifie";
    return "A verifier";
  };

  const handleReceiptPhoto = (event) => {
    const file = event.target.files?.[0];

    if (!file) {
      setReceiptPhoto("");
      return;
    }

    const reader = new FileReader();
    reader.onloadend = () => setReceiptPhoto(reader.result);
    reader.readAsDataURL(file);
  };

  useEffect(() => {
    if (!user.token) {
      window.location.href = "/";
      return;
    }

    let active = true;

    const headers = { Authorization: `Bearer ${user.token}` };

    const requests = [
      api.get("/expenses", { headers }),
      api.get("/interventions", { headers }),
    ];

    if (isAdmin) {
      requests.push(api.get("/employees", { headers }));
    }

    Promise.all(requests)
      .then(([expensesResponse, interventionsResponse, employeesResponse]) => {
        if (active) {
          setExpenses(expensesResponse.data);
          setInterventions(interventionsResponse.data);
          setEmployees(employeesResponse?.data || []);
        }
      })
      .catch(() => {
        if (active) {
          setError("Impossible de charger les frais.");
        }
      });

    return () => {
      active = false;
    };
  }, [isAdmin, user.token]);

  const total = useMemo(
    () =>
      expenses.reduce(
        (sum, expense) => sum + expense.transport + expense.repas + expense.autre,
        0
      ),
    [expenses]
  );

  const resetForm = () => {
    setInterventionId("");
    setTransport("");
    setRepas("");
    setAutre("");
    setReceiptPhoto("");
    setEditingExpenseId(null);
  };

  const saveExpense = async (event) => {
    event.preventDefault();
    setError("");

    try {
      const payload = {
        intervention_id: Number(interventionId),
        transport: Number(transport || 0),
        repas: Number(repas || 0),
        autre: Number(autre || 0),
        receipt_photo: receiptPhoto || null,
      };

      if (editingExpenseId) {
        await api.put(
          `/expenses/${editingExpenseId}`,
          payload,
          { headers: { Authorization: `Bearer ${user.token}` } }
        );
      } else {
        await api.post(
          "/expenses",
          payload,
          { headers: { Authorization: `Bearer ${user.token}` } }
        );
      }

      resetForm();
      loadExpenses();
    } catch {
      setError("L'enregistrement des frais a echoue.");
    }
  };

  const editExpense = (expense) => {
    setEditingExpenseId(expense.id);
    setInterventionId(String(expense.intervention_id));
    setTransport(String(expense.transport));
    setRepas(String(expense.repas));
    setAutre(String(expense.autre));
    setReceiptPhoto(expense.receipt_photo || "");
  };

  const deleteExpense = async (expenseId) => {
    if (!window.confirm("Supprimer ces frais ?")) {
      return;
    }

    setError("");

    try {
      await api.delete(
        `/expenses/${expenseId}`,
        {
          headers: { Authorization: `Bearer ${user.token}` },
        }
      );

      if (editingExpenseId === expenseId) {
        resetForm();
      }

      loadExpenses();
    } catch {
      setError("La suppression des frais a echoue.");
    }
  };

  const verifyExpense = async (expenseId) => {
    setError("");

    try {
      await api.patch(
        `/expenses/${expenseId}/verify`,
        {},
        { headers: { Authorization: `Bearer ${user.token}` } }
      );
      loadExpenses();
    } catch {
      setError("La verification des frais a echoue. Photo justificative obligatoire.");
    }
  };

  return (
    <AppLayout
      title={user.role === "employe" ? "Mes frais" : "Frais"}
    >
      {error && <div className="alert">{error}</div>}

      <section className="stats-grid narrow">
        <article className="stat-card">
          <span>Total frais</span>
          <strong>{total.toFixed(0)} DH</strong>
          <small>{expenses.length} lignes declarees</small>
        </article>
      </section>

      <section className={canManage ? "content-grid" : "content-grid single-column"}>
        {canManage && (
          <form className="panel form-panel" onSubmit={saveExpense}>
            <label>
              Intervention
              <select
                value={interventionId}
                onChange={(event) => setInterventionId(event.target.value)}
                required
              >
                <option value="">Choisir une intervention</option>
                {interventions.map((intervention) => (
                  <option key={intervention.id} value={intervention.id}>
                    {getInterventionLabel(intervention.id)}
                  </option>
                ))}
              </select>
            </label>

            <label>
              Transport
              <input
                type="number"
                value={transport}
                onChange={(event) => setTransport(event.target.value)}
              />
            </label>

            <label>
              Repas
              <input
                type="number"
                value={repas}
                onChange={(event) => setRepas(event.target.value)}
              />
            </label>

            <label>
              Autre
              <input
                type="number"
                value={autre}
                onChange={(event) => setAutre(event.target.value)}
              />
            </label>

            <label>
              Photo justificative
              <input type="file" accept="image/*" onChange={handleReceiptPhoto} />
            </label>

            {receiptPhoto && (
              <img className="receipt-preview" src={receiptPhoto} alt="Justificatif frais" />
            )}

            <div className="button-row">
              <button className="primary-button">
                {editingExpenseId ? "Enregistrer" : "Ajouter"}
              </button>
              {editingExpenseId && (
                <button type="button" className="ghost-button" onClick={resetForm}>
                  Annuler
                </button>
              )}
            </div>
          </form>
        )}

        <div className="panel table-panel">
          <div className="data-table">
            <div className={isAdmin ? "table-row table-head expenses-admin-cols" : "table-row table-head expenses-user-cols"}>
              <span>ID</span>
              <span>Intervention</span>
              <span>Transport</span>
              <span>Repas</span>
              <span>Autre</span>
              <span>Justificatif</span>
              <span>Statut</span>
              {(canManage || isAdmin) && <span>Actions</span>}
            </div>
            {expenses.length === 0 ? (
              <p className="empty-state">Aucun frais declare.</p>
            ) : (
              expenses.map((expense) => (
                <div key={expense.id} className={isAdmin ? "table-row expenses-admin-cols" : "table-row expenses-user-cols"}>
                  <span>#{expense.id}</span>
                  <span>{getInterventionLabel(expense.intervention_id)}</span>
                  <span>{expense.transport} DH</span>
                  <span>{expense.repas} DH</span>
                  <span>{expense.autre} DH</span>
                  <span>
                    {expense.receipt_photo ? (
                      <a className="text-link" href={expense.receipt_photo} target="_blank" rel="noreferrer">
                        Voir photo
                      </a>
                    ) : (
                      "-"
                    )}
                  </span>
                  <span className="status-pill">{getStatusLabel(expense.status)}</span>
                  {canManage && (
                    <span className="actions-cell">
                      <button
                        type="button"
                        className="secondary-button"
                        onClick={() => editExpense(expense)}
                      >
                        Modifier
                      </button>
                      <button
                        type="button"
                        className="danger-button"
                        onClick={() => deleteExpense(expense.id)}
                      >
                        Supprimer
                      </button>
                    </span>
                  )}
                  {isAdmin && (
                    <span className="actions-cell">
                      <button
                        type="button"
                        className="secondary-button"
                        onClick={() => verifyExpense(expense.id)}
                        disabled={!expense.receipt_photo || expense.status === "verifie"}
                      >
                        Verifier
                      </button>
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

export default Expenses;
