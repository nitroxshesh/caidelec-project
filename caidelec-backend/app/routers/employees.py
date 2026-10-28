import re
import unicodedata

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth import hash_password, require_roles
from .. import models, schemas

router = APIRouter(
    prefix="/employees",
    tags=["Employees"]
)


DEFAULT_EMPLOYEE_PASSWORD = "123456"


def slugify_name(full_name: str):
    normalized = unicodedata.normalize("NFKD", full_name)
    ascii_name = normalized.encode("ascii", "ignore").decode("ascii")
    parts = re.findall(r"[a-zA-Z0-9]+", ascii_name.lower())
    return ".".join(parts) or "employe"


def generate_unique_username(db: Session, full_name: str):
    base_username = slugify_name(full_name)
    username = base_username
    counter = 1

    while db.query(models.User).filter(models.User.username == username).first():
        counter += 1
        username = f"{base_username}{counter}"

    return username


@router.post("/", response_model=schemas.EmployeeCreateWithUserOut)
def create_employee(
    employee: schemas.EmployeeCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("admin"))
):
    username = employee.user_username.strip() if employee.user_username else generate_unique_username(db, employee.full_name)
    email = employee.user_email.strip() if employee.user_email else f"{username}@caidelec.local"
    password = employee.user_password or DEFAULT_EMPLOYEE_PASSWORD

    if db.query(models.User).filter(models.User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already exists")

    if db.query(models.User).filter(models.User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    new_employee = models.Employee(
        full_name=employee.full_name,
        role=employee.role,
        phone=employee.phone,
    )

    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)

    new_user = models.User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
        role="employe",
        employee_id=new_employee.id,
        expense_limit=employee.expense_limit,
    )

    db.add(new_user)
    db.commit()

    return {
        "employee": new_employee,
        "user": {
            "username": username,
            "default_password": password,
            "role": "employe",
            "expense_limit": employee.expense_limit,
        },
    }


@router.get("/", response_model=list[schemas.EmployeeOut])
def get_employees(
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("admin"))
):
    return db.query(models.Employee).all()


@router.get("/{employee_id}", response_model=schemas.EmployeeOut)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("admin"))
):
    employee = db.query(models.Employee).filter(
        models.Employee.id == employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    return employee


@router.put("/{employee_id}", response_model=schemas.EmployeeOut)
def update_employee(
    employee_id: int,
    employee_data: schemas.EmployeeCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("admin"))
):
    employee = db.query(models.Employee).filter(
        models.Employee.id == employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    employee.full_name = employee_data.full_name
    employee.role = employee_data.role
    employee.phone = employee_data.phone

    linked_user = db.query(models.User).filter(
        models.User.employee_id == employee.id
    ).first()

    if linked_user:
        linked_user.expense_limit = employee_data.expense_limit
        if employee_data.user_username:
            username = employee_data.user_username.strip()
            existing_user = db.query(models.User).filter(
                models.User.username == username,
                models.User.id != linked_user.id
            ).first()
            if existing_user:
                raise HTTPException(status_code=400, detail="Username already exists")
            linked_user.username = username

        if employee_data.user_email:
            email = employee_data.user_email.strip()
            existing_user = db.query(models.User).filter(
                models.User.email == email,
                models.User.id != linked_user.id
            ).first()
            if existing_user:
                raise HTTPException(status_code=400, detail="Email already exists")
            linked_user.email = email

        if employee_data.user_password:
            linked_user.hashed_password = hash_password(employee_data.user_password)

    db.commit()
    db.refresh(employee)

    return employee


@router.delete("/{employee_id}")
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("admin"))
):
    employee = db.query(models.Employee).filter(
        models.Employee.id == employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    intervention_ids = [
        intervention.id
        for intervention in db.query(models.Intervention).filter(
            models.Intervention.employee_id == employee.id
        ).all()
    ]

    if intervention_ids:
        db.query(models.Expense).filter(
            models.Expense.intervention_id.in_(intervention_ids)
        ).delete(synchronize_session=False)

        db.query(models.Intervention).filter(
            models.Intervention.id.in_(intervention_ids)
        ).delete(synchronize_session=False)

    db.query(models.User).filter(
        models.User.employee_id == employee.id
    ).delete(synchronize_session=False)

    db.delete(employee)
    db.commit()

    return {"message": "Employee deleted successfully"}
