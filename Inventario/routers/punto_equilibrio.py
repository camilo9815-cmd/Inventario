from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import SessionLocal
from dependencies import get_current_user

from schemas.punto_equilibrio import PuntoEquilibrioResponse
from services import punto_equilibrio_service


router = APIRouter(
    prefix="",
    tags=["Punto de Equilibrio"]
)


def get_db():

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.get(
    "/punto-equilibrio",
    response_model=PuntoEquilibrioResponse
)
def obtener_punto_equilibrio(
    mes: int,
    anio: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return punto_equilibrio_service.obtener_punto_equilibrio(
        db=db,
        mes=mes,
        anio=anio
    )