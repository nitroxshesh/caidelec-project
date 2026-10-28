from datetime import date

from pydantic import BaseModel, model_validator


class EmployeeCreate(BaseModel):
    full_name: str
    role: str
    phone: str | None = None
    expense_limit: float | None = None
    user_username: str | None = None
    user_email: str | None = None
    user_password: str | None = None


class EmployeeOut(BaseModel):
    id: int
    full_name: str
    role: str
    phone: str | None = None
    expense_limit: float | None = None

    class Config:
        from_attributes = True


class GeneratedUserOut(BaseModel):
    username: str
    default_password: str
    role: str
    expense_limit: float | None = None


class EmployeeCreateWithUserOut(BaseModel):
    employee: EmployeeOut
    user: GeneratedUserOut


class InterventionCreate(BaseModel):
    employee_id: int
    chantier: str
    nature_travaux: str | None = None
    observation: str | None = None
    start_date: date
    end_date: date
    status: str = "planned"

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date < self.start_date:
            raise ValueError("end_date must be greater than or equal to start_date")

        return self


class InterventionOut(InterventionCreate):
    id: int

    class Config:
        from_attributes = True


class ExpenseCreate(BaseModel):
    intervention_id: int
    transport: float = 0
    repas: float = 0
    autre: float = 0
    receipt_photo: str | None = None


class ExpenseOut(ExpenseCreate):
    id: int
    status: str = "a_verifier"

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "employe"
    employee_id: int | None = None
    expense_limit: float | None = None


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    role: str
    employee_id: int | None = None
    expense_limit: float | None = None

    class Config:
        from_attributes = True


class LoginData(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class ReportTotals(BaseModel):
    employees_count: int = 0
    interventions_count: int = 0
    expenses_count: int = 0
    total_transport: float = 0
    total_repas: float = 0
    total_autre: float = 0
    total_expenses: float = 0


class ReportStatusItem(BaseModel):
    status: str
    count: int


class ReportEmployeeExpenseItem(BaseModel):
    employee_id: int | None = None
    employee_name: str
    total: float


class ReportInterventionExpenseItem(BaseModel):
    intervention_id: int
    chantier: str
    employee_name: str
    total: float


class ReportPeriod(BaseModel):
    start_date: date | None = None
    end_date: date | None = None


class ReportSummaryOut(BaseModel):
    period: ReportPeriod
    totals: ReportTotals
    interventions_by_status: list[ReportStatusItem]
    expenses_by_status: list[ReportStatusItem]
    expenses_by_employee: list[ReportEmployeeExpenseItem]
    expenses_by_intervention: list[ReportInterventionExpenseItem]
