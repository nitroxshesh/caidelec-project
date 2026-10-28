from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app.api.deps import current_user, require_roles
from app.db.session import get_db
from app.models.domain import Intervention, Role
from app.schemas.domain import InterventionCreate, InterventionRead

router = APIRouter(dependencies=[Depends(current_user)])


@router.get("", response_model=list[InterventionRead])
def list_planning(
    day: date | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[Intervention]:
    query = db.query(Intervention).options(joinedload(Intervention.employee))
    if day:
        query = query.filter(Intervention.intervention_date == day)
    return query.order_by(Intervention.intervention_date.desc(), Intervention.id.desc()).all()


@router.post("", response_model=InterventionRead, status_code=201)
def create_intervention(
    payload: InterventionCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_roles(Role.ADMIN, Role.RECEPTION, Role.MANAGER)),
) -> Intervention:
    intervention = Intervention(**payload.model_dump())
    db.add(intervention)
    db.commit()
    db.refresh(intervention)
    return intervention
