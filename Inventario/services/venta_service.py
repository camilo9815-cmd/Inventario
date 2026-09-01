from fastapi import HTTPException
from sqlalchemy.orm import Session

from core.calculos import calcular_item, calcular_totales
from models.cliente import Cliente
from models.detalle_venta import DetalleVenta
from models.medio_pago import MedioPago
from models.producto import Producto
from models.venta import Venta
from schemas.ventas import VentaCreate, VentaUpdate


def crear_venta(
    db: Session,
    venta: VentaCreate,
    id_usuario: int
):
    if len(venta.detalle) == 0:
        raise HTTPException(
            status_code=400,
            detail="La venta debe tener al menos un producto."
        )

    try:
        if venta.id_cliente is not None:
            cliente = (
                db.query(Cliente)
                .filter(
                    Cliente.id_cliente == venta.id_cliente,
                    Cliente.activo == True
                )
                .first()
            )

            if not cliente:
                raise HTTPException(
                    status_code=404,
                    detail="Cliente no encontrado."
                )

        medio_pago = (
            db.query(MedioPago)
            .filter(
                MedioPago.id_medio_pago == venta.id_medio_pago,
                MedioPago.activo == True
            )
            .first()
        )

        if not medio_pago:
            raise HTTPException(
                status_code=404,
                detail="Medio de pago no encontrado."
            )

        nueva_venta = Venta(
            id_cliente=venta.id_cliente,
            factura=venta.factura,
            id_medio_pago=venta.id_medio_pago,
            observacion=venta.observacion,
            id_usuario=id_usuario,
            subtotal=0,
            iva=0,
            total=0
        )

        db.add(nueva_venta)
        db.flush()

        detalle_guardado = []

        for item in venta.detalle:
            if item.cantidad <= 0:
                raise HTTPException(
                    status_code=400,
                    detail="La cantidad debe ser mayor que cero."
                )

            if item.precio_unitario <= 0:
                raise HTTPException(
                    status_code=400,
                    detail="El precio unitario debe ser mayor que cero."
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

            if producto.stock_actual < item.cantidad:
                raise HTTPException(
                    status_code=400,
                    detail=f"Stock insuficiente para {producto.nombre}."
                )

            calculo = calcular_item(
                item.cantidad,
                item.precio_unitario,
                item.porcentaje_iva
            )

            costo_promedio = producto.costo_promedio or 0
            costo_venta = item.cantidad * costo_promedio
            utilidad_bruta = calculo["base"] - costo_venta

            detalle = DetalleVenta(
                id_venta=nueva_venta.id_venta,
                id_producto=item.id_producto,
                cantidad=item.cantidad,
                precio_unitario=item.precio_unitario,
                base=calculo["base"],
                iva=calculo["iva"],
                total=calculo["total"],
                costo_promedio=costo_promedio,
                costo_venta=costo_venta,
                utilidad_bruta=utilidad_bruta
            )

            db.add(detalle)
            detalle_guardado.append(detalle)

            producto.stock_actual -= item.cantidad

        totales = calcular_totales(detalle_guardado)

        nueva_venta.subtotal = totales["subtotal"]
        nueva_venta.iva = totales["iva"]
        nueva_venta.total = totales["total"]

        total_venta = totales["total"]
        if venta.id_medio_pago == 5:
            nueva_venta.valor_pagado = 0
            nueva_venta.saldo = total_venta
            nueva_venta.estado_pago = "PENDIENTE"
            nueva_venta.fecha_vencimiento = venta.fecha_vencimiento
        else:
            nueva_venta.valor_pagado = total_venta
            nueva_venta.saldo = 0
            nueva_venta.estado_pago = "PAGADO"
            nueva_venta.fecha_vencimiento = None

        db.commit()
        db.refresh(nueva_venta)

        return nueva_venta

    except Exception:
        db.rollback()
        raise


def obtener_venta(
    db: Session,
    id_venta: int
):
    venta = (
        db.query(Venta)
        .filter(Venta.id_venta == id_venta)
        .first()
    )

    if not venta:
        raise HTTPException(
            status_code=404,
            detail="Venta no encontrada."
        )

    cliente = None

    if venta.id_cliente is not None:
        cliente = (
            db.query(Cliente)
            .filter(Cliente.id_cliente == venta.id_cliente)
            .first()
        )

    medio_pago = (
        db.query(MedioPago)
        .filter(MedioPago.id_medio_pago == venta.id_medio_pago)
        .first()
    )

    detalle = (
        db.query(
            DetalleVenta,
            Producto.codigo,
            Producto.nombre
        )
        .join(
            Producto,
            Producto.id_producto == DetalleVenta.id_producto
        )
        .filter(DetalleVenta.id_venta == venta.id_venta)
        .all()
    )

    items = []

    for det, codigo, nombre in detalle:
        items.append({
            "id_detalle_venta": det.id_detalle_venta,
            "id_producto": det.id_producto,
            "codigo": codigo,
            "nombre": nombre,
            "cantidad": det.cantidad,
            "precio_unitario": det.precio_unitario,
            "base": det.base,
            "iva": det.iva,
            "total": det.total,
            "costo_promedio": det.costo_promedio,
            "costo_venta": det.costo_venta,
            "utilidad_bruta": det.utilidad_bruta,
        })

    return {
        "id_venta": venta.id_venta,
        "fecha": venta.fecha,
        "factura": venta.factura,
        "id_cliente": venta.id_cliente,
        "id_medio_pago": venta.id_medio_pago,
        "cliente": cliente.nombre if cliente else "Consumidor final",
        "medio_pago": medio_pago.nombre if medio_pago else "",
        "subtotal": venta.subtotal,
        "iva": venta.iva,
        "total": venta.total,
        "observacion": venta.observacion,
        "valor_pagado": venta.valor_pagado,
        "saldo": venta.saldo,
        "estado_pago": venta.estado_pago,
        "fecha_vencimiento": venta.fecha_vencimiento,
        "detalle": items,
    }


def listar_ventas(db: Session):
    ventas = (
        db.query(
            Venta,
            Cliente.nombre.label("cliente"),
            MedioPago.nombre.label("medio_pago")
        )
        .outerjoin(
            Cliente,
            Venta.id_cliente == Cliente.id_cliente
        )
        .join(
            MedioPago,
            Venta.id_medio_pago == MedioPago.id_medio_pago
        )
        .order_by(Venta.id_venta.desc())
        .all()
    )

    resultado = []

    for venta, cliente, medio_pago in ventas:
        resultado.append({
            "id_venta": venta.id_venta,
            "fecha": venta.fecha,
            "factura": venta.factura,
            "id_cliente": venta.id_cliente,
            "cliente": cliente or "Consumidor final",
            "medio_pago": medio_pago,
            "subtotal": venta.subtotal,
            "iva": venta.iva,
            "total": venta.total,
            "valor_pagado": venta.valor_pagado,
            "saldo": venta.saldo,
            "estado_pago": venta.estado_pago,
            "fecha_vencimiento": venta.fecha_vencimiento,
        })

    return resultado


def actualizar_venta(
    db: Session,
    id_venta: int,
    datos: VentaUpdate
):
    venta = db.query(Venta).filter(Venta.id_venta == id_venta).first()
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada.")
    if not datos.detalle:
        raise HTTPException(
            status_code=400,
            detail="La venta debe tener al menos un producto."
        )

    try:
        if datos.id_cliente is not None:
            cliente = (
                db.query(Cliente)
                .filter(
                    Cliente.id_cliente == datos.id_cliente,
                    Cliente.activo == True
                )
                .first()
            )
            if not cliente:
                raise HTTPException(status_code=404, detail="Cliente no encontrado.")

        medio_pago = (
            db.query(MedioPago)
            .filter(
                MedioPago.id_medio_pago == datos.id_medio_pago,
                MedioPago.activo == True
            )
            .first()
        )
        if not medio_pago:
            raise HTTPException(status_code=404, detail="Medio de pago no encontrado.")

        anteriores = (
            db.query(DetalleVenta)
            .filter(DetalleVenta.id_venta == id_venta)
            .all()
        )
        cantidades_anteriores = {}
        for item in anteriores:
            cantidades_anteriores[item.id_producto] = (
                cantidades_anteriores.get(item.id_producto, 0) + item.cantidad
            )

        cantidades_nuevas = {}
        for item in datos.detalle:
            if item.cantidad <= 0 or item.precio_unitario <= 0:
                raise HTTPException(
                    status_code=400,
                    detail="Cantidad y precio deben ser mayores que cero."
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
            stock_resultante = (
                producto.stock_actual
                + cantidades_anteriores.get(id_producto, 0)
                - cantidades_nuevas.get(id_producto, 0)
            )
            if stock_resultante < 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"Stock insuficiente para {producto.nombre}."
                )
            producto.stock_actual = stock_resultante
            productos[id_producto] = producto

        db.query(DetalleVenta).filter(
            DetalleVenta.id_venta == id_venta
        ).delete(synchronize_session=False)

        detalles = []
        for item in datos.detalle:
            producto = productos[item.id_producto]
            calculo = calcular_item(
                item.cantidad,
                item.precio_unitario,
                item.porcentaje_iva
            )
            costo_promedio = producto.costo_promedio or 0
            costo_venta = item.cantidad * costo_promedio
            detalle = DetalleVenta(
                id_venta=id_venta,
                id_producto=item.id_producto,
                cantidad=item.cantidad,
                precio_unitario=item.precio_unitario,
                base=calculo["base"],
                iva=calculo["iva"],
                total=calculo["total"],
                costo_promedio=costo_promedio,
                costo_venta=costo_venta,
                utilidad_bruta=calculo["base"] - costo_venta
            )
            db.add(detalle)
            detalles.append(detalle)

        totales = calcular_totales(detalles)
        venta.id_cliente = datos.id_cliente
        venta.factura = datos.factura
        venta.id_medio_pago = datos.id_medio_pago
        venta.observacion = datos.observacion
        venta.subtotal = totales["subtotal"]
        venta.iva = totales["iva"]
        venta.total = totales["total"]

        venta.saldo = venta.total - (venta.valor_pagado or 0)
        if datos.id_medio_pago == 5:
            if venta.saldo <= 0:
                venta.estado_pago = "PAGADO"
            elif (venta.valor_pagado or 0) > 0:
                venta.estado_pago = "PARCIAL"
            else:
                venta.estado_pago = "PENDIENTE"
            venta.fecha_vencimiento = datos.fecha_vencimiento
        else:
            venta.valor_pagado = venta.total
            venta.saldo = 0
            venta.estado_pago = "PAGADO"
            venta.fecha_vencimiento = None

        db.commit()
        db.refresh(venta)
        return venta
    except Exception:
        db.rollback()
        raise


def eliminar_venta(db: Session, id_venta: int):
    venta = db.query(Venta).filter(Venta.id_venta == id_venta).first()
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada.")

    try:
        detalles = (
            db.query(DetalleVenta)
            .filter(DetalleVenta.id_venta == id_venta)
            .all()
        )
        for detalle in detalles:
            producto = (
                db.query(Producto)
                .filter(Producto.id_producto == detalle.id_producto)
                .with_for_update()
                .first()
            )
            if producto:
                producto.stock_actual += detalle.cantidad

        db.delete(venta)
        db.commit()
        return {"mensaje": "Venta eliminada correctamente."}
    except Exception:
        db.rollback()
        raise


def generar_pdf_venta(
    db: Session,
    id_venta: int
):
    from reports.venta_report import generar_pdf

    venta = obtener_venta(
        db,
        id_venta
    )

    return generar_pdf(venta)
