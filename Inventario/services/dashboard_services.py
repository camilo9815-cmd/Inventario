from sqlalchemy import func, extract
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import datetime

from models.venta import Venta
from models.compra import Compra




def obtener_resumen(
    db,
    mes,
    anio
):

    return {

        "ventas_mes": Decimal(0),

        "compras_mes": Decimal(0),

        "gastos_mes": Decimal(0),

        "utilidad_mes": Decimal(0),

        "iva_neto": Decimal(0),

        "por_cobrar": Decimal(0),

        "por_pagar": Decimal(0),

        "flujo_proyectado": Decimal(0),

        "valor_inventario": Decimal(0)

    }

def obtener_ventas_mes(db, mes, anio):

    total = (
        db.query(
            func.coalesce(func.sum(Venta.total), 0)
        )
        .filter(
            extract("month", Venta.fecha) == mes,
            extract("year", Venta.fecha) == anio
        )
        .scalar()
    )

    cantidad = (
        db.query(func.count(Venta.id_venta))
        .filter(
            extract("month", Venta.fecha) == mes,
            extract("year", Venta.fecha) == anio
        )
        .scalar()
    )

    return {
        "total": total,
        "cantidad": cantidad
    }
