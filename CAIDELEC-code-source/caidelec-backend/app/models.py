from datetime import date as DateType
from sqlalchemy import ForeignKey, String, Integer, Float, Date, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str | None] = mapped_column(String, nullable=True)
    user: Mapped["User | None"] = relationship(back_populates="employee")
    interventions: Mapped[list["Intervention"]] = relationship(back_populates="employee")

    @property
    def expense_limit(self):
        return self.user.expense_limit if self.user else None


class Intervention(Base):
    __tablename__ = "interventions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False)
    chantier: Mapped[str] = mapped_column(String, nullable=False)
    nature_travaux: Mapped[str | None] = mapped_column(String, nullable=True)
    observation: Mapped[str | None] = mapped_column(String, nullable=True)
    date: Mapped[DateType | None] = mapped_column(Date, nullable=True)
    start_date: Mapped[DateType] = mapped_column(Date, nullable=False)
    end_date: Mapped[DateType] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String, default="planned")
    employee: Mapped["Employee"] = relationship(back_populates="interventions")
    expenses: Mapped[list["Expense"]] = relationship(back_populates="intervention")


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    intervention_id: Mapped[int] = mapped_column(ForeignKey("interventions.id"), nullable=False)
    transport: Mapped[float] = mapped_column(Float, default=0)
    repas: Mapped[float] = mapped_column(Float, default=0)
    autre: Mapped[float] = mapped_column(Float, default=0)
    receipt_photo: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String, default="a_verifier")
    intervention: Mapped["Intervention"] = relationship(back_populates="expenses")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, default="employe")
    employee_id: Mapped[int | None] = mapped_column(ForeignKey("employees.id"), nullable=True)
    expense_limit: Mapped[float | None] = mapped_column(Float, nullable=True)
    employee: Mapped["Employee | None"] = relationship(back_populates="user")
