from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import SessionLocal
from dependencies import get_current_user
from schemas.medio_pago import MedioPagoCreate
from services import medio_pago

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/medios-pago")
def crear_medio_pago(
    medio_pago: MedioPagoCreate,
    db: Session = Depends(get_db)
):
    return medio_pago.crear_medio_pago(db, medio_pago)


@router.get("/medios-pago")
def listar_medios_pago(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return medio_pago.listar_medios_pago(db)


@router.put("/medios-pago/{id_medio_pago}")
def editar_medio_pago(
    id_medio_pago: int,
    medio_pago: MedioPagoCreate,
    db: Session = Depends(get_db)
):
    return medio_pago.editar_medio_pago(
        db,
        id_medio_pago,
        medio_pago
    )


@router.delete("/medios-pago/{id_medio_pago}")
def eliminar_medio_pago(
    id_medio_pago: int,
    db: Session = Depends(get_db)
):
    return medio_pago.eliminar_medio_pago(
        db,
        id_medio_pago
    )