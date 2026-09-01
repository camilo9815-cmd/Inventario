from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from models.compra import Compra
from models.detalle_compra import DetalleCompra
from models.producto import Producto
from models.proveedor import Proveedor
from models.medio_pago import MedioPago

from schemas.compras import CompraCreate, CompraUpdate

from core.calculos import (
    calcular_item,
    calcular_totales
)


def crear_compra(
    db: Session,
    compra: CompraCreate,
    id_usuario: int
):

    if len(compra.detalle) == 0:
        raise HTTPException(
            status_code=400,
            detail="La compra debe tener al menos un producto."
        )

    try:

        proveedor = (
            db.query(Proveedor)
            .filter(
                Proveedor.id_proveedor == compra.id_proveedor,
                Proveedor.activo == True
            )
            .first()
        )

        if not proveedor:
            raise HTTPException(
                status_code=404,
                detail="Proveedor no encontrado."
            )

        nueva_compra = Compra(
            id_proveedor=compra.id_proveedor,
            factura=compra.factura,
            id_medio_pago=compra.id_medio_pago,
            observacion=compra.observacion,
            id_usuario=id_usuario,
            subtotal=0,
            iva=0,
            total=0
        )

        db.add(nueva_compra)
        db.flush()

        detalle_guardado = []

        for item in compra.detalle:

            if item.cantidad <= 0:
                raise HTTPException(
                    status_code=400,
                    detail="La cantidad debe ser mayor que cero."
                )

            if item.costo_unitario <= 0:
                raise HTTPException(
                    status_code=400,
                    detail="El costo unitario debe ser mayor que cero."
                )

            producto = (
                db.query(Producto)
                .filter(
                    Producto.id_producto == item.id_producto,
                    Producto.activo == True
                )
                .with_for_update()
                .first()
            )

            if not producto:
                raise HTTPException(
                    status_code=404,
                    detail=f"Producto {item.id_producto} no existe."
                )

            calculo = calcular_item(
                item.cantidad,
                item.costo_unitario,
                item.porcentaje_iva
            )

            detalle = DetalleCompra(
                id_compra=nueva_compra.id_compra,
                id_producto=item.id_producto,
                cantidad=item.cantidad,
                costo_unitario=item.costo_unitario,
                base=calculo["base"],
                iva=calculo["iva"],
                total=calculo["total"]
            )

            db.add(detalle)
            detalle_guardado.append(detalle)

            # ====================================================
            # ACTUALIZAR INVENTARIO Y COSTO PROMEDIO
            # ====================================================

            stock_anterior = producto.stock_actual or 0
            costo_promedio_anterior = producto.costo_promedio or 0

            cantidad_compra = item.cantidad
            costo_compra = item.costo_unitario

            if stock_anterior == 0:

                nuevo_costo_promedio = costo_compra

            else:

                valor_stock_anterior = (
                    stock_anterior * costo_promedio_anterior
                )

                valor_compra = (
                    cantidad_compra * costo_compra
                )

                nuevo_costo_promedio = (
                    valor_stock_anterior + valor_compra
                ) / (
                    stock_anterior + cantidad_compra
                )

            producto.stock_actual = stock_anterior + cantidad_compra
            producto.ultimo_costo = costo_compra
            producto.costo_promedio = nuevo_costo_promedio

        totales = calcular_totales(detalle_guardado)

        nueva_compra.subtotal = totales["subtotal"]
        nueva_compra.iva = totales["iva"]
        nueva_compra.total = totales["total"]

        total_compra = totales["total"]

        if compra.id_medio_pago == 5:

            nueva_compra.valor_pagado = 0
            nueva_compra.saldo = total_compra
            nueva_compra.estado_pago = "PENDIENTE"
            nueva_compra.fecha_vencimiento = compra.fecha_vencimiento

        else:

            nueva_compra.valor_pagado = total_compra
            nueva_compra.saldo = 0
            nueva_compra.estado_pago = "PAGADO"
            nueva_compra.fecha_vencimiento = None

        db.commit()
        db.refresh(nueva_compra)

        return nueva_compra

    except Exception:
        db.rollback()
        raise

def obtener_compra(
    db: Session,
    id_compra: int
):

    compra = (
        db.query(Compra)
        .filter(Compra.id_compra == id_compra)
        .first()
    )

    if not compra:
        raise HTTPException(
            status_code=404,
            detail="Compra no encontrada."
        )

    proveedor = (
        db.query(Proveedor)
        .filter(
            Proveedor.id_proveedor == compra.id_proveedor
        )
        .first()
    )

    medio_pago = (
        db.query(MedioPago)
        .filter(
            MedioPago.id_medio_pago == compra.id_medio_pago
        )
        .first()
    )

    detalle = (
        db.query(
            DetalleCompra,
            Producto.codigo,
            Producto.nombre
        )
        .join(
            Producto,
            Producto.id_producto == DetalleCompra.id_producto
        )
        .filter(
            DetalleCompra.id_compra == compra.id_compra
        )
        .all()
    )

    items = []

    for det, codigo, nombre in detalle:

        items.append({

            "id_detalle_compra": det.id_detalle_compra,
            "id_producto": det.id_producto,
            "codigo": codigo,
            "nombre": nombre,
            "cantidad": det.cantidad,
            "costo_unitario": det.costo_unitario,
            "base": det.base,
            "iva": det.iva,
            "total": det.total

        })

    return {

        "id_compra": compra.id_compra,
        "fecha": compra.fecha,
        "factura": compra.factura,
        "id_proveedor": compra.id_proveedor,
        "id_medio_pago": compra.id_medio_pago,
        "proveedor": proveedor.nombre if proveedor else "",
        "medio_pago": medio_pago.nombre if medio_pago else "",
        "subtotal": compra.subtotal,
        "iva": compra.iva,
        "total": compra.total,
        "observacion": compra.observacion,
        "valor_pagado": compra.valor_pagado,
        "saldo": compra.saldo,
        "estado_pago": compra.estado_pago,
        "fecha_vencimiento": compra.fecha_vencimiento,
        "detalle": items

    }

def listar_compras(db: Session):

    compras = (
        db.query(
            Compra,
            Proveedor.nombre.label("proveedor"),
            MedioPago.nombre.label("medio_pago")
        )
        .join(
            Proveedor,
            Compra.id_proveedor == Proveedor.id_proveedor
        )
        .join(
            MedioPago,
            Compra.id_medio_pago == MedioPago.id_medio_pago
        )
        .order_by(Compra.id_compra.desc())
        .all()
    )

    resultado = []

    for compra, proveedor, medio_pago in compras:

        resultado.append({
            "id_proveedor": compra.id_proveedor,
            "id_compra": compra.id_compra,
            "fecha": compra.fecha,
            "factura": compra.factura,
            "proveedor": proveedor,
            "medio_pago": medio_pago,
            "subtotal": compra.subtotal,
            "iva": compra.iva,
            "total": compra.total,
            "valor_pagado": compra.valor_pagado,
            "saldo": compra.saldo,
            "estado_pago": compra.estado_pago,
            "fecha_vencimiento": compra.fecha_vencimiento

        })

    return resultado


def actualizar_compra(
    db: Session,
    id_compra: int,
    datos: CompraUpdate
):
    compra = (
        db.query(Compra)
        .filter(Compra.id_compra == id_compra)
        .first()
    )

    if not compra:
        raise HTTPException(status_code=404, detail="Compra no encontrada.")

    if not datos.detalle:
        raise HTTPException(
            status_code=400,
            detail="La compra debe tener al menos un producto."
        )

    try:
        proveedor = (
            db.query(Proveedor)
            .filter(
                Proveedor.id_proveedor == datos.id_proveedor,
                Proveedor.activo == True
            )
            .first()
        )
        medio_pago = (
            db.query(MedioPago)
            .filter(MedioPago.id_medio_pago == datos.id_medio_pago)
            .first()
        )

        if not proveedor:
            raise HTTPException(status_code=404, detail="Proveedor no encontrado.")
        if not medio_pago:
            raise HTTPException(status_code=404, detail="Medio de pago no encontrado.")

        anteriores = (
            db.query(DetalleCompra)
            .filter(DetalleCompra.id_compra == id_compra)
            .all()
        )
        cantidades_anteriores = {}
        for item in anteriores:
            cantidades_anteriores[item.id_producto] = (
                cantidades_anteriores.get(item.id_producto, 0) + item.cantidad
            )

        cantidades_nuevas = {}
        for item in datos.detalle:
            if item.cantidad <= 0 or item.costo_unitario <= 0:
                raise HTTPException(
                    status_code=400,
                    detail="Cantidad y costo deben ser mayores que cero."
                )
            cantidades_nuevas[item.id_producto] = (
                cantidades_nuevas.get(item.id_producto, 0) + item.cantidad
            )

        productos = {}
        for id_producto in set(cantidades_anteriores) | set(cantidades_nuevas):
            producto = (
                db.query(Producto)
                .filter(Producto.id_producto == id_producto)
                .with_for_update()
                .first()
            )
            if not producto:
                raise HTTPException(
                    status_code=404,
                    detail=f"Producto {id_producto} no existe."
                )
            diferencia = (
                cantidades_nuevas.get(id_producto, 0)
                - cantidades_anteriores.get(id_producto, 0)
            )
            if producto.stock_actual + diferencia < 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"No se puede reducir la compra de {producto.nombre}: "
                    "parte de ese inventario ya fue utilizada."
                )
            producto.stock_actual += diferencia
            productos[id_producto] = producto

        db.query(DetalleCompra).filter(
            DetalleCompra.id_compra == id_compra
        ).delete(synchronize_session=False)

        detalles = []
        for item in datos.detalle:
            calculo = calcular_item(
                item.cantidad,
                item.costo_unitario,
                item.porcentaje_iva
            )
            detalle = DetalleCompra(
                id_compra=id_compra,
                id_producto=item.id_producto,
                cantidad=item.cantidad,
                costo_unitario=item.costo_unitario,
                base=calculo["base"],
                iva=calculo["iva"],
                total=calculo["total"]
            )
            db.add(detalle)
            detalles.append(detalle)

        totales = calcular_totales(detalles)
        compra.id_proveedor = datos.id_proveedor
        compra.factura = datos.factura
        compra.id_medio_pago = datos.id_medio_pago
        compra.observacion = datos.observacion
        compra.subtotal = totales["subtotal"]
        compra.iva = totales["iva"]
        compra.total = totales["total"]

        compra.saldo = compra.total - (compra.valor_pagado or 0)
        if datos.id_medio_pago == 5:
            if compra.saldo <= 0:
                compra.estado_pago = "PAGADO"
            elif (compra.valor_pagado or 0) > 0:
                compra.estado_pago = "PARCIAL"
            else:
                compra.estado_pago = "PENDIENTE"
            compra.fecha_vencimiento = datos.fecha_vencimiento
        else:
            compra.valor_pagado = compra.total
            compra.saldo = 0
            compra.estado_pago = "PAGADO"
            compra.fecha_vencimiento = None

        db.commit()
        db.refresh(compra)
        return compra
    except Exception:
        db.rollback()
        raise


def eliminar_compra(db: Session, id_compra: int):
    compra = db.query(Compra).filter(Compra.id_compra == id_compra).first()
    if not compra:
        raise HTTPException(status_code=404, detail="Compra no encontrada.")

    try:
        detalles = (
            db.query(DetalleCompra)
            .filter(DetalleCompra.id_compra == id_compra)
            .all()
        )
        for detalle in detalles:
            producto = (
                db.query(Producto)
                .filter(Producto.id_producto == detalle.id_producto)
                .with_for_update()
                .first()
            )
            if producto.stock_actual < detalle.cantidad:
                raise HTTPException(
                    status_code=400,
                    detail=f"No se puede eliminar: el inventario de "
                    f"{producto.nombre} ya fue utilizado."
                )
            producto.stock_actual -= detalle.cantidad

        db.delete(compra)
        db.commit()
        return {"mensaje": "Compra eliminada correctamente."}
    except Exception:
        db.rollback()
        raise

def generar_pdf_compra(
    db: Session,
    id_compra: int
):

    from reports.compra_pdf import generar_pdf

    compra = obtener_compra(
        db,
        id_compra
    )

    return generar_pdf(compra)
