from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import SessionLocal
from dependencies import get_current_user

from schemas.compras import CompraCreate, CompraUpdate
from services import compra_service
from fastapi.responses import StreamingResponse

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/compras")
def crear_compra(
    compra: CompraCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return compra_service.crear_compra(
        db,
        compra,
        current_user.id_usuario
    )


@router.get("/compras")
def listar_compras(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return compra_service.listar_compras(db)


@router.get("/compras/{id_compra}")
def obtener_compra(
    id_compra: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return compra_service.obtener_compra(
        db,
        id_compra
    )


@router.put("/compras/{id_compra}")
def actualizar_compra(
    id_compra: int,
    compra: CompraUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return compra_service.actualizar_compra(db, id_compra, compra)


@router.delete("/compras/{id_compra}")
def eliminar_compra(
    id_compra: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return compra_service.eliminar_compra(db, id_compra)


@router.get("/compras/{id_compra}/pdf")
def imprimir_compra(
    id_compra: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    pdf = compra_service.generar_pdf_compra(
        db,
        id_compra
    )

    return StreamingResponse(

        pdf,

        media_type="application/pdf",

        headers={
            "Content-Disposition":
            f'inline; filename="Compra_{id_compra}.pdf"'
        }

    )
