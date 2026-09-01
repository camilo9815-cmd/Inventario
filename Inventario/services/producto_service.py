from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.producto import Producto
from schemas.producto import ProductoCreate


def crear_producto(
     db: Session,
    producto: ProductoCreate
  
):

    existe = db.query(Producto).filter(
        Producto.codigo == producto.codigo
    ).first()
    if existe:
        raise HTTPException(
            status_code=400,
            detail="El código ya existe"
        )
    
    nuevo = Producto(
        codigo=producto.codigo,
        nombre=producto.nombre,
        id_categoria=producto.id_categoria,
        stock_minimo=producto.stock_minimo,
        precio_venta_sugerido=producto.precio_venta_sugerido,
        activo=True
)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return nuevo

def listar_productos(
    db: Session
):

    return (
        db.query(Producto)
        .filter(Producto.activo == True)
        .all()
    )


def editar_producto(
    db: Session,
    id_producto: int,
    producto: ProductoCreate
):

    producto_db = (
        db.query(Producto)
        .filter(Producto.id_producto == id_producto)
        .first()
    )

    if not producto_db:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado"
        )

    producto_db.codigo = producto.codigo
    producto_db.nombre = producto.nombre
    producto_db.id_categoria = producto.id_categoria
    producto_db.stock_minimo = producto.stock_minimo
    producto_db.precio_venta_sugerido = producto.precio_venta_sugerido

    db.commit()
    db.refresh(producto_db)

    return producto_db


def eliminar_producto(
    db: Session,
    id_producto: int
):

    producto = (
        db.query(Producto)
        .filter(Producto.id_producto == id_producto)
        .first()
    )

    if not producto:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado"
        )

    producto.activo = False

    db.commit()

    return {
        "mensaje": "Producto desactivado correctamente"
    }