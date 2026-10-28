import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import AppLayout from "../components/AppLayout";
import api from "../services/api";
import { getCurrentUser } from "../utils/auth";
import logo from "../assets/caidelec-logo.jpeg";

function InterventionDayDetails() {
  const { date } = useParams();
  const [interventions, setInterventions] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [error, setError] = useState("");
  const user = getCurrentUser();
  const canLoadEmployees = user.role === "admin";

  useEffect(() => {
    if (!user.token) {
      window.location.href = "/";
      return;
    }

    async function loadDetails() {
      try {
        const headers = { Authorization: `Bearer ${user.token}` };
        const requests = [api.get("/interventions", { headers })];

        if (canLoadEmployees) {
          requests.push(api.get("/employees", { headers }));
        }

        const [interventionsResponse, employeesResponse] = await Promise.all(requests);
        setInterventions(interventionsResponse.data);
        setEmployees(employeesResponse?.data || []);
      } catch {
        setError("Impossible de charger les details des interventions.");
      }
    }

    loadDetails();
  }, [canLoadEmployees, user.token]);

  const employeeNameById = (employeeId) => {
    const employee = employees.find((item) => item.id === employeeId);
    return employee ? `${employee.full_name} (${employee.role})` : `Employe #${employeeId}`;
  };

  const dayInterventions = interventions.filter(
    (intervention) => intervention.start_date <= date && intervention.end_date >= date
  );

  const getStatusLabel = (status) => {
    if (status === "a_verifier") return "A verifier";
    if (status === "verifiee") return "Verifiee";
    if (status === "planned") return "Planifiee";
    return status;
  };

  const getLogoDataUrl = async () => {
    const response = await fetch(logo);
    const blob = await response.blob();

    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onloadend = () => resolve(reader.result);
      reader.readAsDataURL(blob);
    });
  };

  const exportToExcel = async () => {
    const ExcelJS = (await import("exceljs")).default;
    const workbook = new ExcelJS.Workbook();
    workbook.creator = "CAIDELEC";
    workbook.created = new Date();
    const worksheet = workbook.addWorksheet("Affectations", {
      pageSetup: {
        orientation: "landscape",
        fitToPage: true,
        fitToWidth: 1,
        fitToHeight: 1,
        margins: {
          left: 0.35,
          right: 0.35,
          top: 0.45,
          bottom: 0.45,
          header: 0.2,
          footer: 0.2,
        },
      },
      views: [{ showGridLines: false }],
    });

    worksheet.columns = [
      { key: "chantier", width: 24 },
      { key: "nature", width: 24 },
      { key: "intervenants", width: 30 },
      { key: "contacts", width: 22 },
      { key: "admin", width: 26 },
      { key: "observations", width: 28 },
    ];

    worksheet.mergeCells("A1:B2");
    worksheet.mergeCells("C1:F1");
    worksheet.mergeCells("C2:F2");

    const logoDataUrl = await getLogoDataUrl();
    const logoImage = workbook.addImage({
      base64: logoDataUrl,
      extension: "jpeg",
    });
    worksheet.addImage(logoImage, {
      tl: { col: 0.12, row: 0.2 },
      ext: { width: 250, height: 60 },
    });

    const border = {
      top: { style: "thin", color: { argb: "FF6FA3CF" } },
      left: { style: "thin", color: { argb: "FF6FA3CF" } },
      bottom: { style: "thin", color: { argb: "FF6FA3CF" } },
      right: { style: "thin", color: { argb: "FF6FA3CF" } },
    };
    const strongBorder = {
      top: { style: "medium", color: { argb: "FF2D76B8" } },
      left: { style: "medium", color: { argb: "FF2D76B8" } },
      bottom: { style: "medium", color: { argb: "FF2D76B8" } },
      right: { style: "medium", color: { argb: "FF2D76B8" } },
    };
    const alignCenter = { horizontal: "center", vertical: "middle", wrapText: true };

    worksheet.getRow(1).height = 34;
    worksheet.getRow(2).height = 28;
    worksheet.getCell("A1").border = strongBorder;
    worksheet.getCell("C1").value = "AFFECTATIONS JOURNALIERES";
    worksheet.getCell("C1").font = { name: "Arial", size: 15, bold: true };
    worksheet.getCell("C1").alignment = alignCenter;
    worksheet.getCell("C1").fill = { type: "pattern", pattern: "solid", fgColor: { argb: "FFF0C73D" } };
    worksheet.getCell("C1").border = strongBorder;
    worksheet.getCell("C2").value = date;
    worksheet.getCell("C2").font = { name: "Arial", size: 12, bold: true };
    worksheet.getCell("C2").alignment = alignCenter;
    worksheet.getCell("C2").fill = { type: "pattern", pattern: "solid", fgColor: { argb: "FFF0C73D" } };
    worksheet.getCell("C2").border = strongBorder;

    ["A1", "B1", "A2", "B2", "C1", "D1", "E1", "F1", "C2", "D2", "E2", "F2"].forEach((cellRef) => {
      worksheet.getCell(cellRef).border = strongBorder;
    });

    const headerRow = worksheet.getRow(3);
    headerRow.height = 42;
    headerRow.values = [
      "CHANTIER",
      "NATURE DES TRAVAUX",
      "INTERVENANTS",
      "CONTACTS INTERVENANTS",
      "ACCOMPAGNEMENT ADMINISTRATIF",
      "OBSERVATIONS",
    ];
    headerRow.eachCell((cell) => {
      cell.font = { name: "Arial", size: 10, bold: true };
      cell.alignment = alignCenter;
      cell.fill = { type: "pattern", pattern: "solid", fgColor: { argb: "FFDCEBF7" } };
      cell.border = border;
    });

    const reportRows = dayInterventions.length > 0
      ? dayInterventions
      : [{ chantier: "Aucune intervention pour cette date.", nature_travaux: "", employee_id: "", observation: "" }];

    reportRows.forEach((intervention, index) => {
      const row = worksheet.getRow(index + 4);
      row.height = dayInterventions.length > 0 ? 52 : 70;
      row.values = [
        intervention.chantier,
        intervention.nature_travaux || (dayInterventions.length > 0 ? "-" : ""),
        dayInterventions.length > 0 ? employeeNameById(intervention.employee_id) : "",
        "",
        "",
        dayInterventions.length > 0
          ? `${intervention.observation || getStatusLabel(intervention.status)}\n${intervention.start_date} - ${intervention.end_date}`
          : "",
      ];
      row.eachCell({ includeEmpty: true }, (cell, colNumber) => {
        cell.font = {
          name: "Arial",
          size: 10,
          bold: dayInterventions.length > 0,
          italic: dayInterventions.length === 0,
          color: { argb: dayInterventions.length > 0 ? "FF111827" : "FF64748B" },
        };
        cell.alignment = colNumber === 1
          ? { horizontal: "left", vertical: "middle", wrapText: true }
          : alignCenter;
        cell.border = border;
      });
    });

    const blankStart = 4 + reportRows.length;
    const blankCount = Math.max(0, 12 - dayInterventions.length);
    for (let index = 0; index < blankCount; index += 1) {
      const row = worksheet.getRow(blankStart + index);
      row.height = 38;
      row.eachCell({ includeEmpty: true }, (cell, colNumber) => {
        if (colNumber <= 6) {
          cell.border = border;
          cell.alignment = alignCenter;
        }
      });
      for (let col = 1; col <= 6; col += 1) {
        const cell = row.getCell(col);
        cell.border = border;
        cell.alignment = alignCenter;
      }
    }

    const signatureRowNumber = blankStart + blankCount;
    worksheet.mergeCells(`A${signatureRowNumber}:B${signatureRowNumber}`);
    worksheet.mergeCells(`C${signatureRowNumber}:D${signatureRowNumber}`);
    worksheet.mergeCells(`E${signatureRowNumber}:F${signatureRowNumber}`);
    const signatureRow = worksheet.getRow(signatureRowNumber);
    signatureRow.height = 70;
    ["A", "C", "E"].forEach((column, index) => {
      const cell = worksheet.getCell(`${column}${signatureRowNumber}`);
      cell.value = ["Visa RES HSE :", "Visa RES TRAVAUX :", "Visa GERANTE :"][index];
      cell.font = { name: "Arial", size: 10, bold: true, italic: true };
      cell.alignment = { horizontal: "center", vertical: "top", wrapText: true };
      cell.border = strongBorder;
    });
    ["B", "D", "F"].forEach((column) => {
      worksheet.getCell(`${column}${signatureRowNumber}`).border = strongBorder;
    });

    const buffer = await workbook.xlsx.writeBuffer();
    const blob = new Blob([buffer], {
      type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `affectations-${date}.xlsx`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  };

  return (
    <AppLayout title={`Interventions du ${date}`}>
      {error && <div className="alert">{error}</div>}

      <section className="panel daily-report-panel">
        <div className="filter-bar">
          <h2>{date}</h2>
          <div className="button-row">
            <button type="button" className="primary-button" onClick={exportToExcel}>
              Exporter Excel
            </button>
            <Link className="secondary-button" to="/dashboard">
              Retour dashboard
            </Link>
          </div>
        </div>

        <div className="daily-report">
          <div className="daily-report-top">
            <div className="daily-logo-box">
              <img src={logo} alt="CAIDELEC" />
            </div>
            <div className="daily-title-box">
              <strong>AFFECTATIONS JOURNALIERES</strong>
              <span>{date}</span>
            </div>
          </div>

          <div className="daily-table-wrap">
            <table className="daily-table">
              <thead>
                <tr>
                  <th>CHANTIER</th>
                  <th>NATURE DES TRAVAUX</th>
                  <th>INTERVENANTS</th>
                  <th>CONTACTS INTERVENANTS</th>
                  <th>ACCOMPAGNEMENT ADMINISTRATIF</th>
                  <th>OBSERVATIONS</th>
                </tr>
              </thead>
              <tbody>
                {dayInterventions.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="daily-empty">
                      Aucune intervention pour cette date.
                    </td>
                  </tr>
                ) : (
                  dayInterventions.map((intervention) => (
                    <tr key={intervention.id}>
                      <td>{intervention.chantier}</td>
                      <td>{intervention.nature_travaux || "-"}</td>
                      <td>{employeeNameById(intervention.employee_id)}</td>
                      <td />
                      <td />
                      <td>
                        {intervention.observation || getStatusLabel(intervention.status)}
                        <br />
                        {intervention.start_date} - {intervention.end_date}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          <div className="daily-signatures">
            <span>Visa RES HSE :</span>
            <span>Visa RES TRAVAUX :</span>
            <span>Visa GERANTE :</span>
          </div>
        </div>
      </section>
    </AppLayout>
  );
}

export default InterventionDayDetails;
