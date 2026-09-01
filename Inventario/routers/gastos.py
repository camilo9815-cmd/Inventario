from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import SessionLocal
from dependencies import get_current_user
from models.categoria_gasto import CategoriaGasto
from models.tipo_gasto import TipoGasto
from schemas.gastos import GastoCreate
from services import gasto_service

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/gastos")
def crear_gasto(
    gasto: GastoCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return gasto_service.crear_gasto(
        db,
        gasto,
        current_user.id_usuario
    )


@router.get("/gastos")
def listar_gastos(
    anio: int = datetime.now().year,
    mes: int = datetime.now().month,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return gasto_service.listar_gastos(db, anio, mes)


@router.get("/gastos/resumen-mensual")
def resumen_mensual(
    anio: int = datetime.now().year,
    mes: int = datetime.now().month,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return gasto_service.obtener_resumen_mensual(db, anio, mes)


@router.get("/tipos-gasto")
def listar_tipos_gasto(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return (
        db.query(TipoGasto)
        .filter(TipoGasto.activo == True)
        .order_by(TipoGasto.nombre)
        .all()
    )


@router.get("/categorias-gasto")
def listar_categorias_gasto(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return (
        db.query(CategoriaGasto)
        .filter(CategoriaGasto.activo == True)
        .order_by(CategoriaGasto.nombre)
        .all()
    )
