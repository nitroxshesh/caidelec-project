from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth import require_roles
from .. import models, schemas

router = APIRouter(
    prefix="/expenses",
    tags=["Expenses"]
)


def expense_total(expense_data: schemas.ExpenseCreate):
    return expense_data.transport + expense_data.repas + expense_data.autre


def ensure_expense_within_limit(
    db: Session,
    current_user,
    expense_data: schemas.ExpenseCreate,
    exclude_expense_id: int | None = None
):
    if current_user.expense_limit is None:
        return

    existing_expenses = (
        db.query(models.Expense)
        .join(models.Intervention)
        .filter(models.Intervention.employee_id == current_user.employee_id)
        .all()
    )

    current_total = sum(
        item.transport + item.repas + item.autre
        for item in existing_expenses
        if exclude_expense_id is None or item.id != exclude_expense_id
    )

    new_total = current_total + expense_total(expense_data)

    if new_total > current_user.expense_limit:
        raise HTTPException(
            status_code=403,
            detail=f"Expense limit exceeded. Limit is {current_user.expense_limit} DH"
        )


@router.post("/", response_model=schemas.ExpenseOut)
def create_expense(
    expense: schemas.ExpenseCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("employe"))
):
    if current_user.employee_id is None:
        raise HTTPException(status_code=403, detail="Employe user must be linked to an employee")

    intervention = db.query(models.Intervention).filter(
        models.Intervention.id == expense.intervention_id
    ).first()

    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention not found")

    if intervention.employee_id != current_user.employee_id:
        raise HTTPException(status_code=403, detail="You can only add expenses for your own interventions")

    ensure_expense_within_limit(db, current_user, expense)

    new_expense = models.Expense(**expense.model_dump())

    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)

    return new_expense


@router.get("/", response_model=list[schemas.ExpenseOut])
def get_expenses(
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("admin", "employe"))
):
    if current_user.role == "employe":
        if current_user.employee_id is None:
            return []

        return (
            db.query(models.Expense)
            .join(models.Intervention)
            .filter(models.Intervention.employee_id == current_user.employee_id)
            .all()
        )

    return db.query(models.Expense).all()


@router.get("/{expense_id}", response_model=schemas.ExpenseOut)
def get_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("admin", "employe"))
):
    expense = db.query(models.Expense).filter(
        models.Expense.id == expense_id
    ).first()

    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    if current_user.role == "employe":
        intervention = db.query(models.Intervention).filter(
            models.Intervention.id == expense.intervention_id
        ).first()

        if not intervention or intervention.employee_id != current_user.employee_id:
            raise HTTPException(status_code=403, detail="You can only view your own expenses")

    return expense


@router.put("/{expense_id}", response_model=schemas.ExpenseOut)
def update_expense(
    expense_id: int,
    expense_data: schemas.ExpenseCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("employe"))
):
    expense = db.query(models.Expense).filter(
        models.Expense.id == expense_id
    ).first()

    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    current_intervention = db.query(models.Intervention).filter(
        models.Intervention.id == expense.intervention_id
    ).first()

    if not current_intervention or current_intervention.employee_id != current_user.employee_id:
        raise HTTPException(status_code=403, detail="You can only update your own expenses")

    intervention = db.query(models.Intervention).filter(
        models.Intervention.id == expense_data.intervention_id
    ).first()

    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention not found")

    if intervention.employee_id != current_user.employee_id:
        raise HTTPException(status_code=403, detail="You can only move expenses to your own interventions")

    ensure_expense_within_limit(db, current_user, expense_data, exclude_expense_id=expense.id)

    expense.intervention_id = expense_data.intervention_id
    expense.transport = expense_data.transport
    expense.repas = expense_data.repas
    expense.autre = expense_data.autre
    expense.receipt_photo = expense_data.receipt_photo
    expense.status = "a_verifier"

    db.commit()
    db.refresh(expense)

    return expense


@router.patch("/{expense_id}/verify", response_model=schemas.ExpenseOut)
def verify_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("admin"))
):
    expense = db.query(models.Expense).filter(
        models.Expense.id == expense_id
    ).first()

    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    if not expense.receipt_photo:
        raise HTTPException(status_code=400, detail="Receipt photo is required before verification")

    expense.status = "verifie"
    db.commit()
    db.refresh(expense)

    return expense


@router.delete("/{expense_id}")
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("employe"))
):
    expense = db.query(models.Expense).filter(
        models.Expense.id == expense_id
    ).first()

    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    intervention = db.query(models.Intervention).filter(
        models.Intervention.id == expense.intervention_id
    ).first()

    if not intervention or intervention.employee_id != current_user.employee_id:
        raise HTTPException(status_code=403, detail="You can only delete your own expenses")

    db.delete(expense)
    db.commit()

    return {"message": "Expense deleted successfully"}
