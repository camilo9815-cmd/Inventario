from fastapi import HTTPException
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import datetime

from models.comprobante_egreso import ComprobanteEgreso, DetalleComprobanteEgreso
from models.compra import Compra
from models.proveedor import Proveedor
from models.usuario import Usuario
from schemas.comprobantes_egreso import ComprobanteEgresoCreate


def crear_egreso(db: Session, egreso: ComprobanteEgresoCreate, id_usuario: int):
    proveedor = db.query(Proveedor).filter(Proveedor.id_proveedor == egreso.id_proveedor, Proveedor.activo == True).first()
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado.")

    if not egreso.detalles:
        raise HTTPException(status_code=400, detail="El comprobante de egreso debe tener al menos un detalle de pago.")

    try:
        numero_egreso = egreso.numero
        if not numero_egreso:
            count = db.query(ComprobanteEgreso).count() + 1
            numero_egreso = f"CE-{datetime.now().strftime('%Y%m')}-{count:04d}"

        nuevo_egreso = ComprobanteEgreso(
            numero=numero_egreso,
            id_proveedor=egreso.id_proveedor,
            id_usuario=id_usuario,
            observacion=egreso.observacion,
            total=0
        )
        db.add(nuevo_egreso)
        db.flush()

        total_egreso = Decimal(0)
        for item in egreso.detalles:
            if item.valor <= 0:
                raise HTTPException(status_code=400, detail="El valor a pagar debe ser mayor que cero.")

            compra = db.query(Compra).filter(Compra.id_compra == item.id_compra).first()
            if not compra:
                raise HTTPException(status_code=404, detail=f"Compra {item.id_compra} no encontrada.")

            if compra.id_proveedor != egreso.id_proveedor:
                raise HTTPException(status_code=400, detail=f"La compra {item.id_compra} no pertenece al proveedor seleccionado.")

            saldo_pendiente = compra.saldo or compra.total
            if item.valor > saldo_pendiente:
                raise HTTPException(
                    status_code=400,
                    detail=f"El valor a pagar ({item.valor}) supera el saldo pendiente ({saldo_pendiente}) de la compra {compra.id_compra}."
                )

            # Actualizar compra
            compra.valor_pagado = (compra.valor_pagado or 0) + item.valor
            compra.saldo = compra.total - compra.valor_pagado
            
            if compra.saldo <= 0:
                compra.estado_pago = "PAGADO"
            elif compra.valor_pagado > 0:
                compra.estado_pago = "PARCIAL"
            else:
                compra.estado_pago = "PENDIENTE"

            detalle = DetalleComprobanteEgreso(
                id_egreso=nuevo_egreso.id_egreso,
                id_compra=item.id_compra,
                valor=item.valor
            )
            db.add(detalle)
            total_egreso += item.valor

        nuevo_egreso.total = total_egreso
        db.commit()
        db.refresh(nuevo_egreso)
        return nuevo_egreso

    except Exception:
        db.rollback()
        raise


def listar_egresos(db: Session):
    egresos = (
        db.query(
            ComprobanteEgreso,
            Proveedor.nombre.label("proveedor_nombre"),
            Usuario.nombre.label("usuario_nombre")
        )
        .join(Proveedor, ComprobanteEgreso.id_proveedor == Proveedor.id_proveedor)
        .outerjoin(Usuario, ComprobanteEgreso.id_usuario == Usuario.id_usuario)
        .order_by(ComprobanteEgreso.id_egreso.desc())
        .all()
    )

    resultado = []
    for egreso, proveedor_nombre, usuario_nombre in egresos:
        resultado.append({
            "id_egreso": egreso.id_egreso,
            "fecha": egreso.fecha,
            "numero": egreso.numero,
            "id_proveedor": egreso.id_proveedor,
            "proveedor_nombre": proveedor_nombre,
            "id_usuario": egreso.id_usuario,
            "usuario_nombre": usuario_nombre,
            "observacion": egreso.observacion,
            "total": egreso.total
        })
    return resultado


def obtener_egreso(db: Session, id_egreso: int):
    egreso = db.query(ComprobanteEgreso).filter(ComprobanteEgreso.id_egreso == id_egreso).first()
    if not egreso:
        raise HTTPException(status_code=404, detail="Comprobante de egreso no encontrado.")

    proveedor = db.query(Proveedor).filter(Proveedor.id_proveedor == egreso.id_proveedor).first()
    usuario = db.query(Usuario).filter(Usuario.id_usuario == egreso.id_usuario).first()

    detalles_db = (
        db.query(DetalleComprobanteEgreso, Compra.factura)
        .join(Compra, DetalleComprobanteEgreso.id_compra == Compra.id_compra)
        .filter(DetalleComprobanteEgreso.id_egreso == id_egreso)
        .all()
    )

    detalles = []
    for det, factura in detalles_db:
        detalles.append({
            "id_detalle": det.id_detalle,
            "id_egreso": det.id_egreso,
            "id_compra": det.id_compra,
            "valor": det.valor,
            "factura_compra": factura
        })

    return {
        "id_egreso": egreso.id_egreso,
        "fecha": egreso.fecha,
        "numero": egreso.numero,
        "id_proveedor": egreso.id_proveedor,
        "proveedor_nombre": proveedor.nombre if proveedor else "",
        "id_usuario": egreso.id_usuario,
        "usuario_nombre": usuario.nombre if usuario else "",
        "observacion": egreso.observacion,
        "total": egreso.total,
        "detalles": detalles
    }

def eliminar_egreso(db: Session, id_egreso: int):

    egreso = (
        db.query(ComprobanteEgreso)
        .filter(ComprobanteEgreso.id_egreso == id_egreso)
        .first()
    )

    if not egreso:
        raise HTTPException(
            status_code=404,
            detail="Comprobante de egreso no encontrado."
        )

    try:

        detalles = (
            db.query(DetalleComprobanteEgreso)
            .filter(
                DetalleComprobanteEgreso.id_egreso == id_egreso
            )
            .all()
        )

        for detalle in detalles:

            compra = (
                db.query(Compra)
                .filter(
                    Compra.id_compra == detalle.id_compra
                )
                .first()
            )

            if compra:

                compra.valor_pagado = (
                    (compra.valor_pagado or 0)
                    - detalle.valor
                )

                if compra.valor_pagado < 0:
                    compra.valor_pagado = 0

                compra.saldo = (
                    compra.total
                    - compra.valor_pagado
                )

                if compra.valor_pagado <= 0:

                    compra.valor_pagado = 0
                    compra.saldo = compra.total
                    compra.estado_pago = "PENDIENTE"

                elif compra.valor_pagado < compra.total:

                    compra.saldo = (
                        compra.total
                        - compra.valor_pagado
                    )

                    compra.estado_pago = "PARCIAL"

                else:

                    compra.saldo = 0
                    compra.estado_pago = "PAGADO"

            db.delete(detalle)

        db.delete(egreso)

        db.commit()

        return {
            "mensaje": "Comprobante eliminado correctamente."
        }

    except Exception:
        db.rollback()
        raise
