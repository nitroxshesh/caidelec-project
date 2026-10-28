from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas
from ..auth import get_current_user, hash_password, normalize_role, verify_password, create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register", response_model=schemas.UserOut)
def register_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    role = normalize_role(user.role)

    if role not in {"admin", "employe"}:
        raise HTTPException(status_code=400, detail="Invalid role")

    if role == "employe" and user.employee_id is None:
        raise HTTPException(status_code=400, detail="Employe users must be linked to an employee")

    existing_user = db.query(models.User).filter(
        models.User.username == user.username
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),
        role=role,
        employee_id=user.employee_id
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=schemas.Token)
def login_user(
    login_data: schemas.LoginData,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.username == login_data.username
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    role = normalize_role(user.role)
    token = create_access_token(
        data={
            "sub": user.username,
            "role": role,
            "employee_id": user.employee_id
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=schemas.UserOut)
def get_me(current_user = Depends(get_current_user)):
    current_user.role = normalize_role(current_user.role)
    return current_user
