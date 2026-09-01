from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import SessionLocal
from dependencies import get_current_user

from services import dashboard_services
from schemas.dashboard import DashboardResponse

router = APIRouter()


def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()


@router.get(
    "/dashboard",
    response_model=DashboardResponse
)
def dashboard(
    mes: int,
    anio: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return dashboard_services.obtener_dashboard(
        db,
        mes,
        anio
    )