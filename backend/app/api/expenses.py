from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import current_user, require_roles
from app.db.session import get_db
from app.models.domain import Role, TravelExpense
from app.schemas.domain import ExpenseCreate, ExpenseRead

router = APIRouter(dependencies=[Depends(current_user)])


@router.get("", response_model=list[ExpenseRead])
def list_expenses(db: Session = Depends(get_db)) -> list[TravelExpense]:
    return db.query(TravelExpense).order_by(TravelExpense.created_at.desc()).all()


@router.post("", response_model=ExpenseRead, status_code=201)
def create_expense(
    payload: ExpenseCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_roles(Role.ADMIN, Role.RECEPTION, Role.COMPTABLE)),
) -> TravelExpense:
    expense = TravelExpense(**payload.model_dump())
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense
