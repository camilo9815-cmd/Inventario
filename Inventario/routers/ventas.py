from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from database import SessionLocal
from dependencies import get_current_user
from schemas.ventas import VentaCreate, VentaUpdate
from services import venta_service

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/ventas")
def crear_venta(
    venta: VentaCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return venta_service.crear_venta(
        db,
        venta,
        current_user.id_usuario
    )


@router.get("/ventas")
def listar_ventas(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return venta_service.listar_ventas(db)


@router.get("/ventas/{id_venta}")
def obtener_venta(
    id_venta: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return venta_service.obtener_venta(
        db,
        id_venta
    )


@router.put("/ventas/{id_venta}")
def actualizar_venta(
    id_venta: int,
    venta: VentaUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return venta_service.actualizar_venta(db, id_venta, venta)


@router.delete("/ventas/{id_venta}")
def eliminar_venta(
    id_venta: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return venta_service.eliminar_venta(db, id_venta)


@router.get("/ventas/{id_venta}/pdf")
def imprimir_venta(
    id_venta: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    pdf = venta_service.generar_pdf_venta(
        db,
        id_venta
    )

    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            f'inline; filename="Venta_{id_venta}.pdf"'
        }
    )
