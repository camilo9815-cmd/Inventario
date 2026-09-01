from calendar import monthrange
from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from models.categoria_gasto import CategoriaGasto
from models.detalle_venta import DetalleVenta
from models.gasto import Gasto
from models.medio_pago import MedioPago
from models.tipo_gasto import TipoGasto
from models.venta import Venta
from schemas.gastos import GastoCreate


def _rango_mes(anio: int, mes: int):
    if mes < 1 or mes > 12:
        raise HTTPException(status_code=400, detail="El mes no es valido.")

    ultimo_dia = monthrange(anio, mes)[1]
    inicio = datetime(anio, mes, 1)
    fin = datetime(anio, mes, ultimo_dia, 23, 59, 59, 999999)
    return inicio, fin


def crear_gasto(db: Session, gasto: GastoCreate, id_usuario: int):
    if gasto.base <= 0:
        raise HTTPException(
            status_code=400,
            detail="La base del gasto debe ser mayor que cero."
        )

    tipo = (
        db.query(TipoGasto)
        .filter(
            TipoGasto.id_tipo_gasto == gasto.id_tipo_gasto,
            TipoGasto.activo == True
        )
        .first()
    )
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo de gasto no encontrado.")

    categoria = (
        db.query(CategoriaGasto)
        .filter(
            CategoriaGasto.id_categoria_gasto == gasto.id_categoria_gasto,
            CategoriaGasto.activo == True
        )
        .first()
    )
    if not categoria:
        raise HTTPException(
            status_code=404,
            detail="Categoria de gasto no encontrada."
        )

    medio_pago = (
        db.query(MedioPago)
        .filter(
            MedioPago.id_medio_pago == gasto.id_medio_pago,
            MedioPago.activo == True
        )
        .first()
    )
    if not medio_pago:
        raise HTTPException(status_code=404, detail="Medio de pago no encontrado.")

    iva = Decimal("0")
    if gasto.aplica_iva:
        iva = gasto.base * (gasto.porcentaje_iva / Decimal("100"))

    nuevo_gasto = Gasto(
        fecha=gasto.fecha,
        id_tipo_gasto=gasto.id_tipo_gasto,
        id_categoria_gasto=gasto.id_categoria_gasto,
        concepto=gasto.concepto,
        base=gasto.base,
        aplica_iva=gasto.aplica_iva,
        iva=iva,
        total=gasto.base + iva,
        id_medio_pago=gasto.id_medio_pago,
        id_usuario=id_usuario,
        observacion=gasto.observacion
    )

    if gasto.fecha is None:
        nuevo_gasto.fecha = datetime.now()

    db.add(nuevo_gasto)
    db.commit()
    db.refresh(nuevo_gasto)
    return nuevo_gasto


def listar_gastos(db: Session, anio: int, mes: int):
    inicio, fin = _rango_mes(anio, mes)

    filas = (
        db.query(
            Gasto,
            TipoGasto.nombre.label("tipo"),
            CategoriaGasto.nombre.label("categoria"),
            MedioPago.nombre.label("medio_pago")
        )
        .join(TipoGasto, Gasto.id_tipo_gasto == TipoGasto.id_tipo_gasto)
        .join(
            CategoriaGasto,
            Gasto.id_categoria_gasto == CategoriaGasto.id_categoria_gasto
        )
        .join(MedioPago, Gasto.id_medio_pago == MedioPago.id_medio_pago)
        .filter(Gasto.fecha >= inicio, Gasto.fecha <= fin)
        .order_by(Gasto.fecha.desc(), Gasto.id_gasto.desc())
        .all()
    )

    return [
        {
            "id_gasto": gasto.id_gasto,
            "fecha": gasto.fecha,
            "tipo": tipo,
            "categoria": categoria,
            "concepto": gasto.concepto,
            "base": gasto.base,
            "aplica_iva": gasto.aplica_iva,
            "iva": gasto.iva,
            "total": gasto.total,
            "medio_pago": medio_pago,
            "observacion": gasto.observacion,
        }
        for gasto, tipo, categoria, medio_pago in filas
    ]


def obtener_resumen_mensual(db: Session, anio: int, mes: int):
    inicio, fin = _rango_mes(anio, mes)

    ventas = (
        db.query(
            func.coalesce(func.sum(Venta.subtotal), 0),
            func.coalesce(func.sum(Venta.iva), 0),
            func.coalesce(func.sum(Venta.total), 0)
        )
        .filter(Venta.fecha >= inicio, Venta.fecha <= fin)
        .one()
    )

    costos = (
        db.query(
            func.coalesce(func.sum(DetalleVenta.costo_venta), 0),
            func.coalesce(func.sum(DetalleVenta.utilidad_bruta), 0)
        )
        .join(Venta, Venta.id_venta == DetalleVenta.id_venta)
        .filter(Venta.fecha >= inicio, Venta.fecha <= fin)
        .one()
    )

    gastos = (
        db.query(
            TipoGasto.nombre,
            func.coalesce(func.sum(Gasto.base), 0),
            func.coalesce(func.sum(Gasto.iva), 0),
            func.coalesce(func.sum(Gasto.total), 0)
        )
        .join(TipoGasto, Gasto.id_tipo_gasto == TipoGasto.id_tipo_gasto)
        .filter(Gasto.fecha >= inicio, Gasto.fecha <= fin)
        .group_by(TipoGasto.nombre)
        .all()
    )

    gastos_fijos = Decimal("0")
    gastos_variables = Decimal("0")
    iva_gastos = Decimal("0")

    for nombre, base, iva, total in gastos:
        iva_gastos += Decimal(iva)
        if "fijo" in nombre.lower():
            gastos_fijos += Decimal(total)
        else:
            gastos_variables += Decimal(total)

    ventas_base = Decimal(ventas[0])
    iva_ventas = Decimal(ventas[1])
    ventas_total = Decimal(ventas[2])
    costo_reposicion = Decimal(costos[0])
    utilidad_bruta = Decimal(costos[1])
    gastos_totales = gastos_fijos + gastos_variables
    utilidad_despues_gastos = utilidad_bruta - gastos_totales
    disponible_para_compras = max(
        Decimal("0"),
        costo_reposicion + utilidad_despues_gastos
    )
    porcentaje_cobertura = Decimal("100")

    if gastos_fijos > 0:
        porcentaje_cobertura = min(
            Decimal("100"),
            (utilidad_bruta / gastos_fijos) * Decimal("100")
        )

    faltante_gastos_fijos = max(Decimal("0"), gastos_fijos - utilidad_bruta)

    return {
        "anio": anio,
        "mes": mes,
        "ventas_base": ventas_base,
        "iva_ventas": iva_ventas,
        "ventas_total": ventas_total,
        "dinero_reposicion": costo_reposicion,
        "utilidad_bruta": utilidad_bruta,
        "gastos_fijos": gastos_fijos,
        "gastos_variables": gastos_variables,
        "gastos_totales": gastos_totales,
        "iva_gastos": iva_gastos,
        "iva_neto": iva_ventas - iva_gastos,
        "utilidad_despues_gastos": utilidad_despues_gastos,
        "disponible_para_compras": disponible_para_compras,
        "porcentaje_cobertura_fijos": porcentaje_cobertura,
        "faltante_gastos_fijos": faltante_gastos_fijos,
        "gastos_fijos_cubiertos": utilidad_bruta >= gastos_fijos,
    }
