from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.medio_pago import MedioPago
from schemas.medio_pago import MedioPagoCreate


def crear_medio_pago(
    db: Session,
    medio_pago: MedioPagoCreate
):

    existe = (
        db.query(MedioPago)
        .filter(MedioPago.nombre == medio_pago.nombre)
        .first()
    )

    if existe:
        raise HTTPException(
            status_code=400,
            detail="El medio de pago ya existe"
        )

    nuevo = MedioPago(
        nombre=medio_pago.nombre,
        activo=True
    )

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return nuevo


def listar_medios_pago(
    db: Session
):

    return (
        db.query(MedioPago)
        .filter(MedioPago.activo == True)
        .order_by(MedioPago.nombre)
        .all()
    )


def editar_medio_pago(
    db: Session,
    id_medio_pago: int,
    medio_pago: MedioPagoCreate
):

    medio = (
        db.query(MedioPago)
        .filter(MedioPago.id_medio_pago == id_medio_pago)
        .first()
    )

    if not medio:
        raise HTTPException(
            status_code=404,
            detail="Medio de pago no encontrado"
        )

    medio.nombre = medio_pago.nombre

    db.commit()
    db.refresh(medio)

    return medio


def eliminar_medio_pago(
    db: Session,
    id_medio_pago: int
):

    medio = (
        db.query(MedioPago)
        .filter(MedioPago.id_medio_pago == id_medio_pago)
        .first()
    )

    if not medio:
        raise HTTPException(
            status_code=404,
            detail="Medio de pago no encontrado"
        )

    medio.activo = False

    db.commit()

    return {
        "mensaje": "Medio de pago desactivado correctamente"
    }