from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.proveedor import Proveedor
from schemas.proveedor import ProveedorCreate


def crear_proveedor(
     db: Session,
    proveedor: ProveedorCreate
  
):

    existe = db.query(Proveedor).filter(
        Proveedor.nit == proveedor.nit
    ).first()
    if existe:
        raise HTTPException(
            status_code=400,
            detail="El proveedor ya existe"
        )
    
    nuevo = Proveedor(
        nit=proveedor.nit,
        nombre=proveedor.nombre,
        telefono=proveedor.telefono,
        correo=proveedor.correo,
        direccion=proveedor.direccion,
        activo=True
)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return nuevo

def listar_proveedor(
    db: Session
):

    return (
        db.query(Proveedor)
        .filter(Proveedor.activo == True)
        .all()
    )


def editar_proveedor(
    db: Session,
    id_proveedor: int,
    proveedor: ProveedorCreate
):

    proveedor_db = (
        db.query(Proveedor)
        .filter(Proveedor.id_proveedor == id_proveedor)
        .first()
    )

    if not proveedor_db:
        raise HTTPException(
            status_code=404,
            detail="Proveedor no encontrado"
        )

    proveedor_db.nit = proveedor.nit
    proveedor_db.nombre = proveedor.nombre
    proveedor_db.telefono = proveedor.telefono
    proveedor_db.correo = proveedor.correo
    proveedor_db.direccion = proveedor.direccion

    db.commit()
    db.refresh(proveedor_db)

    return proveedor_db


def eliminar_proveedor(
    db: Session,
    id_proveedor: int
):

    proveedor = (
        db.query(Proveedor)
        .filter(Proveedor.id_proveedor == id_proveedor)
        .first()
    )

    if not proveedor:
        raise HTTPException(
            status_code=404,
            detail="proveedor no encontrado"
        )

    proveedor.activo = False

    db.commit()

    return {
        "mensaje": "proveedor desactivado correctamente"
    }