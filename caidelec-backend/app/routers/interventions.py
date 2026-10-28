from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth import require_roles
from .. import models, schemas

router = APIRouter(
    prefix="/interventions",
    tags=["Interventions"]
)


@router.post("/", response_model=schemas.InterventionOut)
def create_intervention(
    intervention: schemas.InterventionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("admin"))
):
    employee = db.query(models.Employee).filter(
        models.Employee.id == intervention.employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    new_intervention = models.Intervention(
        **intervention.model_dump(),
        date=intervention.start_date
    )

    db.add(new_intervention)
    db.commit()
    db.refresh(new_intervention)

    return new_intervention


@router.get("/", response_model=list[schemas.InterventionOut])
def get_interventions(
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("admin", "employe"))
):
    if current_user.role == "employe":
        if current_user.employee_id is None:
            return []

        return db.query(models.Intervention).filter(
            models.Intervention.employee_id == current_user.employee_id
        ).all()

    return db.query(models.Intervention).all()


@router.get("/{intervention_id}", response_model=schemas.InterventionOut)
def get_intervention(
    intervention_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("admin", "employe"))
):
    intervention = db.query(models.Intervention).filter(
        models.Intervention.id == intervention_id
    ).first()

    if not intervention:
        raise HTTPException(
            status_code=404,
            detail="Intervention not found"
        )

    if current_user.role == "employe" and intervention.employee_id != current_user.employee_id:
        raise HTTPException(status_code=403, detail="You can only view your own interventions")

    return intervention


@router.put("/{intervention_id}", response_model=schemas.InterventionOut)
def update_intervention(
    intervention_id: int,
    intervention_data: schemas.InterventionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("admin"))
):
    intervention = db.query(models.Intervention).filter(
        models.Intervention.id == intervention_id
    ).first()

    if not intervention:
        raise HTTPException(
            status_code=404,
            detail="Intervention not found"
        )

    employee = db.query(models.Employee).filter(
        models.Employee.id == intervention_data.employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    intervention.employee_id = intervention_data.employee_id
    intervention.chantier = intervention_data.chantier
    intervention.nature_travaux = intervention_data.nature_travaux
    intervention.observation = intervention_data.observation
    intervention.date = intervention_data.start_date
    intervention.start_date = intervention_data.start_date
    intervention.end_date = intervention_data.end_date
    intervention.status = intervention_data.status

    db.commit()
    db.refresh(intervention)

    return intervention


@router.patch("/{intervention_id}/declare-done", response_model=schemas.InterventionOut)
def declare_intervention_done(
    intervention_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("employe"))
):
    intervention = db.query(models.Intervention).filter(
        models.Intervention.id == intervention_id
    ).first()

    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention not found")

    if intervention.employee_id != current_user.employee_id:
        raise HTTPException(status_code=403, detail="You can only declare your own interventions")

    intervention.status = "a_verifier"
    db.commit()
    db.refresh(intervention)

    return intervention


@router.patch("/{intervention_id}/verify", response_model=schemas.InterventionOut)
def verify_intervention(
    intervention_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("admin"))
):
    intervention = db.query(models.Intervention).filter(
        models.Intervention.id == intervention_id
    ).first()

    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention not found")

    intervention.status = "verifiee"
    db.commit()
    db.refresh(intervention)

    return intervention


@router.delete("/{intervention_id}")
def delete_intervention(
    intervention_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("admin"))
):
    intervention = db.query(models.Intervention).filter(
        models.Intervention.id == intervention_id
    ).first()

    if not intervention:
        raise HTTPException(
            status_code=404,
            detail="Intervention not found"
        )

    db.delete(intervention)
    db.commit()

    return {"message": "Intervention deleted successfully"}
