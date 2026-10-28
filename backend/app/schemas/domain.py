from datetime import date

from pydantic import BaseModel, Field

from app.models.domain import EmployeeStatus, ExpenseStatus, InterventionStatus, Role


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: Role
    full_name: str


class LoginRequest(BaseModel):
    email: str
    password: str


class EmployeeBase(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    function: str = Field(min_length=2, max_length=120)
    phone: str | None = None
    status: EmployeeStatus = EmployeeStatus.ACTIVE


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeRead(EmployeeBase):
    id: int

    model_config = {"from_attributes": True}


class InterventionBase(BaseModel):
    intervention_date: date
    client: str
    site: str
    mission: str
    employee_id: int
    status: InterventionStatus = InterventionStatus.PLANNED
    notes: str | None = None


class InterventionCreate(InterventionBase):
    pass


class InterventionRead(InterventionBase):
    id: int
    employee: EmployeeRead

    model_config = {"from_attributes": True}


class ExpenseBase(BaseModel):
    intervention_id: int
    distance_km: float = 0
    transport_amount: float = 0
    meal_amount: float = 0
    other_amount: float = 0
    status: ExpenseStatus = ExpenseStatus.DRAFT


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseRead(ExpenseBase):
    id: int
    total_amount: float

    model_config = {"from_attributes": True}


class MonthlyReport(BaseModel):
    month: str
    total_interventions: int
    total_distance_km: float
    total_expenses: float
    exported_items: int
