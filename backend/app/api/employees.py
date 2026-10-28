from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import current_user, require_roles
from app.db.session import get_db
from app.models.domain import Employee, Role, User
from app.schemas.domain import EmployeeCreate, EmployeeRead

router = APIRouter(dependencies=[Depends(current_user)])


@router.get("", response_model=list[EmployeeRead])
def list_employees(db: Session = Depends(get_db)) -> list[Employee]:
    return db.query(Employee).order_by(Employee.full_name).all()


@router.post("", response_model=EmployeeRead, status_code=201)
def create_employee(
    payload: EmployeeCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(Role.ADMIN, Role.MANAGER)),
) -> Employee:
    employee = Employee(**payload.model_dump())
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee
