from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.domain import Role, User
from app.schemas.domain import LoginRequest, Token

router = APIRouter()


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> Token:
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email ou mot de passe incorrect")

    return Token(
        access_token=create_access_token(user.email, user.role),
        role=user.role,
        full_name=user.full_name,
    )


@router.post("/seed-admin")
def seed_admin(db: Session = Depends(get_db)) -> dict[str, str]:
    existing = db.query(User).filter(User.email == "admin@caidelec.local").first()
    if existing:
        return {"message": "Admin already exists", "email": existing.email}

    user = User(
        full_name="Administrateur CAIDELEC",
        email="admin@caidelec.local",
        password_hash=hash_password("admin123"),
        role=Role.ADMIN,
    )
    db.add(user)
    db.commit()
    return {"message": "Admin created", "email": user.email, "password": "admin123"}
