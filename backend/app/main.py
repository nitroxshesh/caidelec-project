from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, employees, expenses, planning, reports
from app.core.config import settings
from app.db.session import Base, engine


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="CAIDELEC Planning API",
    description="Gestion de la planification quotidienne, interventions et frais de déplacement.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(employees.router, prefix="/api/employees", tags=["employees"])
app.include_router(planning.router, prefix="/api/planning", tags=["planning"])
app.include_router(expenses.router, prefix="/api/expenses", tags=["expenses"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "caidelec-planning-api"}
