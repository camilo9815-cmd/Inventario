from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from database import SessionLocal
from dependencies import get_current_user
from schemas.recibos_caja import ReciboCajaCreate, ReciboCajaResponse
from services import recibo_caja_service

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/recibos-caja", response_model=ReciboCajaResponse)
def crear_recibo(
    recibo: ReciboCajaCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return recibo_caja_service.crear_recibo(
        db,
        recibo,
        current_user.id_usuario
    )


@router.get("/recibos-caja", response_model=List[ReciboCajaResponse])
def listar_recibos(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return recibo_caja_service.listar_recibos(db)


@router.get("/recibos-caja/{id_recibo}", response_model=ReciboCajaResponse)
def obtener_recibo(
    id_recibo: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return recibo_caja_service.obtener_recibo(db, id_recibo)

@router.delete("/recibos-caja/{id_recibo}")
def eliminar_recibo(
    id_recibo: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return recibo_caja_service.eliminar_recibo(db, id_recibo)
