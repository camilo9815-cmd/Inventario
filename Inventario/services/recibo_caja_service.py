from fastapi import HTTPException
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import datetime

from models.recibo_caja import ReciboCaja, DetalleReciboCaja
from models.venta import Venta
from models.cliente import Cliente
from models.usuario import Usuario
from schemas.recibos_caja import ReciboCajaCreate


def crear_recibo(db: Session, recibo: ReciboCajaCreate, id_usuario: int):
    cliente = db.query(Cliente).filter(Cliente.id_cliente == recibo.id_cliente, Cliente.activo == True).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado.")

    if not recibo.detalles:
        raise HTTPException(status_code=400, detail="El recibo debe tener al menos un detalle de pago.")

    try:
        # Auto-generar número si no viene en request
        numero_recibo = recibo.numero
        if not numero_recibo:
            count = db.query(ReciboCaja).count() + 1
            numero_recibo = f"RC-{datetime.now().strftime('%Y%m')}-{count:04d}"

        nuevo_recibo = ReciboCaja(
            numero=numero_recibo,
            id_cliente=recibo.id_cliente,
            id_usuario=id_usuario,
            observacion=recibo.observacion,
            total=0
        )
        db.add(nuevo_recibo)
        db.flush()

        total_recibo = Decimal(0)
        for item in recibo.detalles:
            if item.valor <= 0:
                raise HTTPException(status_code=400, detail="El valor a pagar debe ser mayor que cero.")

            venta = db.query(Venta).filter(Venta.id_venta == item.id_venta).first()
            if not venta:
                raise HTTPException(status_code=404, detail=f"Venta {item.id_venta} no encontrada.")

            if venta.id_cliente != recibo.id_cliente:
                raise HTTPException(status_code=400, detail=f"La venta {item.id_venta} no pertenece al cliente seleccionado.")

            # Validar que no se pague de más
            # Permitir pagar hasta el saldo de la venta
            saldo_pendiente = venta.saldo or venta.total
            if item.valor > saldo_pendiente:
                raise HTTPException(
                    status_code=400,
                    detail=f"El valor a pagar ({item.valor}) supera el saldo pendiente ({saldo_pendiente}) de la venta {venta.id_venta}."
                )

            # Actualizar venta
            venta.valor_pagado = (venta.valor_pagado or 0) + item.valor
            venta.saldo = venta.total - venta.valor_pagado
            
            if venta.saldo <= 0:
                venta.estado_pago = "PAGADO"
            elif venta.valor_pagado > 0:
                venta.estado_pago = "PARCIAL"
            else:
                venta.estado_pago = "PENDIENTE"

            detalle = DetalleReciboCaja(
                id_recibo=nuevo_recibo.id_recibo,
                id_venta=item.id_venta,
                valor=item.valor
            )
            db.add(detalle)
            total_recibo += item.valor

        nuevo_recibo.total = total_recibo
        db.commit()
        db.refresh(nuevo_recibo)
        return nuevo_recibo

    except Exception:
        db.rollback()
        raise


def listar_recibos(db: Session):
    recibos = (
        db.query(
            ReciboCaja,
            Cliente.nombre.label("cliente_nombre"),
            Usuario.nombre.label("usuario_nombre")
        )
        .join(Cliente, ReciboCaja.id_cliente == Cliente.id_cliente)
        .outerjoin(Usuario, ReciboCaja.id_usuario == Usuario.id_usuario)
        .order_by(ReciboCaja.id_recibo.desc())
        .all()
    )

    resultado = []
    for recibo, cliente_nombre, usuario_nombre in recibos:
        resultado.append({
            "id_recibo": recibo.id_recibo,
            "fecha": recibo.fecha,
            "numero": recibo.numero,
            "id_cliente": recibo.id_cliente,
            "cliente_nombre": cliente_nombre,
            "id_usuario": recibo.id_usuario,
            "usuario_nombre": usuario_nombre,
            "observacion": recibo.observacion,
            "total": recibo.total
        })
    return resultado


def obtener_recibo(db: Session, id_recibo: int):
    recibo = db.query(ReciboCaja).filter(ReciboCaja.id_recibo == id_recibo).first()
    if not recibo:
        raise HTTPException(status_code=404, detail="Recibo de caja no encontrado.")

    cliente = db.query(Cliente).filter(Cliente.id_cliente == recibo.id_cliente).first()
    usuario = db.query(Usuario).filter(Usuario.id_usuario == recibo.id_usuario).first()

    detalles_db = (
        db.query(DetalleReciboCaja, Venta.factura)
        .join(Venta, DetalleReciboCaja.id_venta == Venta.id_venta)
        .filter(DetalleReciboCaja.id_recibo == id_recibo)
        .all()
    )

    detalles = []
    for det, factura in detalles_db:
        detalles.append({
            "id_detalle": det.id_detalle,
            "id_recibo": det.id_recibo,
            "id_venta": det.id_venta,
            "valor": det.valor,
            "factura_venta": factura
        })

    return {
        "id_recibo": recibo.id_recibo,
        "fecha": recibo.fecha,
        "numero": recibo.numero,
        "id_cliente": recibo.id_cliente,
        "cliente_nombre": cliente.nombre if cliente else "",
        "id_usuario": recibo.id_usuario,
        "usuario_nombre": usuario.nombre if usuario else "",
        "observacion": recibo.observacion,
        "total": recibo.total,
        "detalles": detalles
    }


def eliminar_recibo(db: Session, id_recibo: int):
    recibo = (
        db.query(ReciboCaja)
        .filter(ReciboCaja.id_recibo == id_recibo)
        .first()
    )

    if not recibo:
        raise HTTPException(
            status_code=404,
            detail="Recibo de caja no encontrado."
        )

    try:
        detalles = (
            db.query(DetalleReciboCaja)
            .filter(DetalleReciboCaja.id_recibo == id_recibo)
            .all()
        )

        for detalle in detalles:

            venta = (
                db.query(Venta)
                .filter(Venta.id_venta == detalle.id_venta)
                .first()
            )

            if not venta:
                continue

            # Revertir el pago
            venta.valor_pagado = (venta.valor_pagado or 0) - detalle.valor

            if venta.valor_pagado < 0:
                venta.valor_pagado = 0

            venta.saldo = venta.total - venta.valor_pagado

            # Actualizar estado de pago
            if venta.valor_pagado <= 0:
                venta.valor_pagado = 0
                venta.saldo = venta.total
                venta.estado_pago = "PENDIENTE"

            elif venta.valor_pagado < venta.total:
                venta.saldo = venta.total - venta.valor_pagado
                venta.estado_pago = "PARCIAL"

            else:
                venta.saldo = 0
                venta.estado_pago = "PAGADO"

            db.delete(detalle)

        db.delete(recibo)

        db.commit()

        return {
            "mensaje": "Recibo de caja eliminado correctamente."
        }

    except Exception:
        db.rollback()
        raise