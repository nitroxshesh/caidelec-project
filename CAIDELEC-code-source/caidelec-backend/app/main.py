from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from .database import Base, engine
from .routers import employees, interventions, expenses, auth

Base.metadata.create_all(bind=engine)


def migrate_existing_sqlite():
    with engine.begin() as conn:
        user_columns = [row[1] for row in conn.execute(text("PRAGMA table_info(users)")).fetchall()]
        intervention_columns = [row[1] for row in conn.execute(text("PRAGMA table_info(interventions)")).fetchall()]
        expense_columns = [row[1] for row in conn.execute(text("PRAGMA table_info(expenses)")).fetchall()]

        if "employee_id" not in user_columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN employee_id INTEGER"))

        if "expense_limit" not in user_columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN expense_limit FLOAT"))

        if "start_date" not in intervention_columns:
            conn.execute(text("ALTER TABLE interventions ADD COLUMN start_date DATE"))

        if "end_date" not in intervention_columns:
            conn.execute(text("ALTER TABLE interventions ADD COLUMN end_date DATE"))

        if "nature_travaux" not in intervention_columns:
            conn.execute(text("ALTER TABLE interventions ADD COLUMN nature_travaux VARCHAR"))

        if "observation" not in intervention_columns:
            conn.execute(text("ALTER TABLE interventions ADD COLUMN observation VARCHAR"))

        if "date" in intervention_columns:
            conn.execute(text("UPDATE interventions SET start_date = date WHERE start_date IS NULL"))
            conn.execute(text("UPDATE interventions SET end_date = date WHERE end_date IS NULL"))

        if "receipt_photo" not in expense_columns:
            conn.execute(text("ALTER TABLE expenses ADD COLUMN receipt_photo TEXT"))

        if "status" not in expense_columns:
            conn.execute(text("ALTER TABLE expenses ADD COLUMN status VARCHAR DEFAULT 'a_verifier'"))
            conn.execute(text("UPDATE expenses SET status = 'a_verifier' WHERE status IS NULL"))

        conn.execute(text("UPDATE users SET role = 'employe' WHERE role != 'admin'"))


migrate_existing_sqlite()

app = FastAPI(title="CAIDELEC Planning API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "API CAIDELEC is running"}

app.include_router(employees.router)
app.include_router(interventions.router)
app.include_router(expenses.router)
app.include_router(auth.router)
