from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import SessionLocal
from models.usuario import Usuario
from core.security import verify_password, create_access_token

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    user = (
        db.query(Usuario)
        .filter(Usuario.usuario == form_data.username)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Usuario no existe"
        )

    if not verify_password(
        form_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=400,
            detail="Password incorrecta"
        )

    token = create_access_token({
        "sub": user.usuario,
        "rol": user.id_rol
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }
