import { useEffect, useState } from "react";
import AppLayout from "../components/AppLayout";
import api from "../services/api";
import { getCurrentUser } from "../utils/auth";

function Employees() {
  const [employees, setEmployees] = useState([]);
  const [fullName, setFullName] = useState("");
  const [role, setRole] = useState("");
  const [phone, setPhone] = useState("");
  const [expenseLimit, setExpenseLimit] = useState("");
  const [userUsername, setUserUsername] = useState("");
  const [userPassword, setUserPassword] = useState("");
  const [error, setError] = useState("");
  const [generatedUser, setGeneratedUser] = useState(null);
  const [editingEmployeeId, setEditingEmployeeId] = useState(null);
  const user = getCurrentUser();

  const loadEmployees = async () => {
    try {
      const response = await api.get("/employees", {
        headers: { Authorization: `Bearer ${user.token}` },
      });
      setEmployees(response.data);
    } catch {
      setError("Impossible de charger les employes.");
    }
  };

  useEffect(() => {
    if (!user.token) {
      window.location.href = "/";
      return;
    }

    let active = true;

    api
      .get("/employees", {
        headers: { Authorization: `Bearer ${user.token}` },
      })
      .then((response) => {
        if (active) {
          setEmployees(response.data);
        }
      })
      .catch(() => {
        if (active) {
          setError("Impossible de charger les employes.");
        }
      });

    return () => {
      active = false;
    };
  }, [user.token]);

  const resetForm = () => {
    setFullName("");
    setRole("");
    setPhone("");
    setExpenseLimit("");
    setUserUsername("");
    setUserPassword("");
    setEditingEmployeeId(null);
  };

  const saveEmployee = async (event) => {
    event.preventDefault();
    setError("");

    try {
      const payload = {
        full_name: fullName,
        role,
        phone,
        expense_limit: expenseLimit === "" ? null : Number(expenseLimit),
        user_username: userUsername || null,
        user_password: userPassword || null,
      };

      if (editingEmployeeId) {
        await api.put(
          `/employees/${editingEmployeeId}`,
          payload,
          { headers: { Authorization: `Bearer ${user.token}` } }
        );
        setGeneratedUser(null);
      } else {
        const response = await api.post(
          "/employees",
          payload,
          { headers: { Authorization: `Bearer ${user.token}` } }
        );
        setGeneratedUser(response.data.user);
      }

      resetForm();
      loadEmployees();
    } catch {
      setError("L'enregistrement de l'employe a echoue.");
    }
  };

  const editEmployee = (employee) => {
      setEditingEmployeeId(employee.id);
    setGeneratedUser(null);
    setFullName(employee.full_name);
    setRole(employee.role);
    setPhone(employee.phone || "");
    setExpenseLimit(employee.expense_limit ?? "");
    setUserUsername("");
    setUserPassword("");
  };

  const deleteEmployee = async (employeeId) => {
    if (!window.confirm("Supprimer cet employe ?")) {
      return;
    }

    setError("");

    try {
      await api.delete(
        `/employees/${employeeId}`,
        {
          headers: { Authorization: `Bearer ${user.token}` },
        }
      );

      if (editingEmployeeId === employeeId) {
        resetForm();
      }

      loadEmployees();
    } catch {
      setError("La suppression de l'employe a echoue.");
    }
  };

  return (
    <AppLayout title="Employés">
      {error && <div className="alert">{error}</div>}

      <section className="content-grid">
        <form className="panel form-panel" onSubmit={saveEmployee}>
          <label>
            Nom complet
            <input
              value={fullName}
              onChange={(event) => setFullName(event.target.value)}
              required
            />
          </label>

          <label>
            Rôle
            <input
              value={role}
              onChange={(event) => setRole(event.target.value)}
              required
            />
          </label>

          <label>
            Telephone
            <input value={phone} onChange={(event) => setPhone(event.target.value)} />
          </label>

          <label>
            Limite frais
            <input
              type="number"
              value={expenseLimit}
              onChange={(event) => setExpenseLimit(event.target.value)}
            />
          </label>

          <div className="account-box">
            <h2>Compte utilisateur</h2>
            <label>
              Nom utilisateur
              <input
                value={userUsername}
                onChange={(event) => setUserUsername(event.target.value)}
              />
            </label>

            <label>
              Mot de passe
              <input
                type="text"
                value={userPassword}
                onChange={(event) => setUserPassword(event.target.value)}
              />
            </label>
          </div>

          <div className="button-row">
            <button className="primary-button">
              {editingEmployeeId ? "Enregistrer" : "Ajouter"}
            </button>
            {editingEmployeeId && (
              <button type="button" className="ghost-button" onClick={resetForm}>
                Annuler
              </button>
            )}
          </div>

          {generatedUser && (
            <div className="credentials-box">
              <strong>Compte employe cree</strong>
              <span>Nom utilisateur : {generatedUser.username}</span>
              <span>Mot de passe : {generatedUser.default_password}</span>
              <span>Rôle : {generatedUser.role}</span>
            </div>
          )}
        </form>

        <div className="panel table-panel">
          <div className="data-table">
            <div className="table-row table-head five-cols">
              <span>Nom</span>
              <span>Rôle</span>
              <span>Telephone</span>
              <span>Limite frais</span>
              <span>Actions</span>
            </div>
            {employees.length === 0 ? (
              <p className="empty-state">Aucun employe enregistre.</p>
            ) : (
              employees.map((employee) => (
                <div key={employee.id} className="table-row five-cols">
                  <span>{employee.full_name}</span>
                  <span>{employee.role}</span>
                  <span>{employee.phone || "-"}</span>
                  <span>{employee.expense_limit == null ? "-" : `${employee.expense_limit} DH`}</span>
                  <span className="actions-cell">
                    <button
                      type="button"
                      className="secondary-button"
                      onClick={() => editEmployee(employee)}
                    >
                      Modifier
                    </button>
                    <button
                      type="button"
                      className="danger-button"
                      onClick={() => deleteEmployee(employee.id)}
                    >
                      Supprimer
                    </button>
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      </section>
    </AppLayout>
  );
}

export default Employees;
