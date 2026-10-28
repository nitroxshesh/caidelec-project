from collections import defaultdict
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import require_roles
from ..database import get_db

router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


def expense_total(expense: models.Expense) -> float:
    return (expense.transport or 0) + (expense.repas or 0) + (expense.autre or 0)


@router.get("/summary", response_model=schemas.ReportSummaryOut)
def get_report_summary(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "employe"))
):
    if start_date and end_date and end_date < start_date:
        raise HTTPException(status_code=400, detail="end_date must be greater than or equal to start_date")

    interventions_query = db.query(models.Intervention)

    if current_user.role == "employe":
        if current_user.employee_id is None:
            interventions = []
        else:
            interventions_query = interventions_query.filter(
                models.Intervention.employee_id == current_user.employee_id
            )
            interventions = interventions_query.all()
    else:
        interventions = interventions_query.all()

    if start_date:
        interventions = [
            intervention
            for intervention in interventions
            if intervention.end_date and intervention.end_date >= start_date
        ]

    if end_date:
        interventions = [
            intervention
            for intervention in interventions
            if intervention.start_date and intervention.start_date <= end_date
        ]

    intervention_ids = [intervention.id for intervention in interventions]
    expenses = []

    if intervention_ids:
        expenses = (
            db.query(models.Expense)
            .filter(models.Expense.intervention_id.in_(intervention_ids))
            .all()
        )

    employees = db.query(models.Employee).all()
    employee_by_id = {employee.id: employee for employee in employees}
    intervention_by_id = {intervention.id: intervention for intervention in interventions}

    total_transport = sum(expense.transport or 0 for expense in expenses)
    total_repas = sum(expense.repas or 0 for expense in expenses)
    total_autre = sum(expense.autre or 0 for expense in expenses)

    interventions_by_status = defaultdict(int)
    for intervention in interventions:
        interventions_by_status[intervention.status or "non_defini"] += 1

    expenses_by_status = defaultdict(int)
    expenses_by_employee = defaultdict(float)
    expenses_by_intervention = defaultdict(float)

    for expense in expenses:
        total = expense_total(expense)
        intervention = intervention_by_id.get(expense.intervention_id)

        expenses_by_status[expense.status or "non_defini"] += 1

        if intervention:
            expenses_by_employee[intervention.employee_id] += total
            expenses_by_intervention[intervention.id] += total

    employee_items = []
    for employee_id, total in expenses_by_employee.items():
        employee = employee_by_id.get(employee_id)
        employee_items.append({
            "employee_id": employee_id,
            "employee_name": employee.full_name if employee else f"Employe #{employee_id}",
            "total": total,
        })

    intervention_items = []
    for intervention_id, total in expenses_by_intervention.items():
        intervention = intervention_by_id.get(intervention_id)
        employee = employee_by_id.get(intervention.employee_id) if intervention else None
        intervention_items.append({
            "intervention_id": intervention_id,
            "chantier": intervention.chantier if intervention else f"Intervention #{intervention_id}",
            "employee_name": employee.full_name if employee else "Employe non defini",
            "total": total,
        })

    visible_employee_ids = {intervention.employee_id for intervention in interventions}

    return {
        "period": {
            "start_date": start_date,
            "end_date": end_date,
        },
        "totals": {
            "employees_count": len(visible_employee_ids),
            "interventions_count": len(interventions),
            "expenses_count": len(expenses),
            "total_transport": total_transport,
            "total_repas": total_repas,
            "total_autre": total_autre,
            "total_expenses": total_transport + total_repas + total_autre,
        },
        "interventions_by_status": [
            {"status": status, "count": count}
            for status, count in sorted(interventions_by_status.items())
        ],
        "expenses_by_status": [
            {"status": status, "count": count}
            for status, count in sorted(expenses_by_status.items())
        ],
        "expenses_by_employee": sorted(
            employee_items,
            key=lambda item: item["total"],
            reverse=True
        ),
        "expenses_by_intervention": sorted(
            intervention_items,
            key=lambda item: item["total"],
            reverse=True
        ),
    }
