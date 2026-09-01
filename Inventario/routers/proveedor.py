from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models.proveedor import Proveedor
from schemas.proveedor import ProveedorCreate
from dependencies import get_current_user
from services import proveedor_service

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/proveedor")
def crear_proveedor(
    proveedor: ProveedorCreate,
    db: Session = Depends(get_db)
):
    return proveedor_service.crear_proveedor(db, proveedor)

@router.get("/proveedor")
def listar_proveedor(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return proveedor_service.listar_proveedor(db)


@router.put("/proveedor/{id_proveedor}")
def editar_proveedor(
    id_proveedor: int,
    proveedor: ProveedorCreate,
    db: Session = Depends(get_db)
):
    return proveedor_service.editar_proveedor(db, id_proveedor, proveedor)


@router.delete("/proveedor/{id_proveedor}")
def eliminar_proveedor(
    id_proveedor: int,
    db: Session = Depends(get_db)
):
    return proveedor_service.eliminar_proveedor(db, id_proveedor)