from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from database import SessionLocal
from dependencies import get_current_user
from schemas.comprobantes_egreso import ComprobanteEgresoCreate, ComprobanteEgresoResponse
from services import comprobante_egreso_service

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/comprobantes-egreso", response_model=ComprobanteEgresoResponse)
def crear_egreso(
    egreso: ComprobanteEgresoCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return comprobante_egreso_service.crear_egreso(
        db,
        egreso,
        current_user.id_usuario
    )


@router.get("/comprobantes-egreso", response_model=List[ComprobanteEgresoResponse])
def listar_egresos(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return comprobante_egreso_service.listar_egresos(db)


@router.get("/comprobantes-egreso/{id_egreso}", response_model=ComprobanteEgresoResponse)
def obtener_egreso(
    id_egreso: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return comprobante_egreso_service.obtener_egreso(db, id_egreso)

@router.delete("/comprobantes-egreso/{id_egreso}")
def eliminar_egreso(
    id_egreso: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return comprobante_egreso_service.eliminar_egreso(
        db,
        id_egreso
    )
