from datetime import date, datetime
from enum import StrEnum

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


def enum_values(enum_cls: type[StrEnum]) -> list[str]:
    return [item.value for item in enum_cls]


class Role(StrEnum):
    ADMIN = "admin"
    RECEPTION = "reception"
    COMPTABLE = "comptable"
    MANAGER = "manager"


class EmployeeStatus(StrEnum):
    ACTIVE = "active"
    ON_LEAVE = "on_leave"
    SICK = "sick"
    ABSENT = "absent"


class InterventionStatus(StrEnum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


class ExpenseStatus(StrEnum):
    DRAFT = "draft"
    VALIDATED = "validated"
    EXPORTED = "exported"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(160), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Role] = mapped_column(Enum(Role, name="user_role", values_callable=enum_values), default=Role.RECEPTION, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    function: Mapped[str] = mapped_column(String(120), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(40))
    status: Mapped[EmployeeStatus] = mapped_column(
        Enum(EmployeeStatus, name="employee_status", values_callable=enum_values),
        default=EmployeeStatus.ACTIVE,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    interventions: Mapped[list["Intervention"]] = relationship(back_populates="employee")


class Intervention(Base):
    __tablename__ = "interventions"

    id: Mapped[int] = mapped_column(primary_key=True)
    intervention_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    client: Mapped[str] = mapped_column(String(160), nullable=False)
    site: Mapped[str] = mapped_column(String(180), nullable=False)
    mission: Mapped[str] = mapped_column(Text, nullable=False)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False)
    status: Mapped[InterventionStatus] = mapped_column(
        Enum(InterventionStatus, name="intervention_status", values_callable=enum_values),
        default=InterventionStatus.PLANNED,
    )
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    employee: Mapped[Employee] = relationship(back_populates="interventions")
    expenses: Mapped[list["TravelExpense"]] = relationship(back_populates="intervention")


class TravelExpense(Base):
    __tablename__ = "travel_expenses"

    id: Mapped[int] = mapped_column(primary_key=True)
    intervention_id: Mapped[int] = mapped_column(ForeignKey("interventions.id"), nullable=False)
    distance_km: Mapped[float] = mapped_column(Numeric(8, 2), default=0)
    transport_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    meal_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    other_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    status: Mapped[ExpenseStatus] = mapped_column(
        Enum(ExpenseStatus, name="expense_status", values_callable=enum_values),
        default=ExpenseStatus.DRAFT,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    intervention: Mapped[Intervention] = relationship(back_populates="expenses")

    @property
    def total_amount(self) -> float:
        return float(self.transport_amount + self.meal_amount + self.other_amount)
