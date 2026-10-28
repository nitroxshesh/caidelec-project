from fastapi import APIRouter, Depends
from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.db.session import get_db
from app.models.domain import Intervention, TravelExpense
from app.schemas.domain import MonthlyReport

router = APIRouter(dependencies=[Depends(current_user)])


@router.get("/monthly", response_model=MonthlyReport)
def monthly_report(year: int, month: int, db: Session = Depends(get_db)) -> MonthlyReport:
    total_interventions = (
        db.query(func.count(Intervention.id))
        .filter(extract("year", Intervention.intervention_date) == year)
        .filter(extract("month", Intervention.intervention_date) == month)
        .scalar()
        or 0
    )

    expense_row = (
        db.query(
            func.coalesce(func.sum(TravelExpense.distance_km), 0),
            func.coalesce(func.sum(TravelExpense.transport_amount + TravelExpense.meal_amount + TravelExpense.other_amount), 0),
            func.count(TravelExpense.id),
        )
        .join(Intervention, TravelExpense.intervention_id == Intervention.id)
        .filter(extract("year", Intervention.intervention_date) == year)
        .filter(extract("month", Intervention.intervention_date) == month)
        .one()
    )

    return MonthlyReport(
        month=f"{year}-{month:02d}",
        total_interventions=total_interventions,
        total_distance_km=float(expense_row[0]),
        total_expenses=float(expense_row[1]),
        exported_items=int(expense_row[2]),
    )
