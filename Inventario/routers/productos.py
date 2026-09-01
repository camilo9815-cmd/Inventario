from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models.producto import Producto
from schemas.producto import ProductoCreate
from dependencies import get_current_user
from services import producto_service

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/productos")
def crear_producto(
    producto: ProductoCreate,
    db: Session = Depends(get_db)
):
    return producto_service.crear_producto(db, producto)

@router.get("/productos")
def listar_productos(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return producto_service.listar_productos(db)


@router.put("/productos/{id_producto}")
def editar_producto(
    id_producto: int,
    producto: ProductoCreate,
    db: Session = Depends(get_db)
):
    return producto_service.editar_producto(db, id_producto, producto)


@router.delete("/productos/{id_producto}")
def eliminar_producto(
    id_producto: int,
    db: Session = Depends(get_db)
):
    return producto_service.eliminar_producto(db, id_producto)