from decimal import Decimal

from sqlalchemy import func, extract

from models.venta import Venta
from models.detalle_venta import DetalleVenta
from models.gasto import Gasto
from datetime import date
import calendar


# ============================================================
# VENTAS DEL PERIODO
# ============================================================

def obtener_ventas(db, mes: int, anio: int) -> Decimal:

    total = (
        db.query(
            func.coalesce(
                func.sum(Venta.total),
                0
            )
        )
        .filter(
            extract("month", Venta.fecha) == mes,
            extract("year", Venta.fecha) == anio
        )
        .scalar()
    )

    return Decimal(total or 0)


# ============================================================
# COSTO DE VENTAS
# ============================================================

def obtener_costo_ventas(db, mes: int, anio: int) -> Decimal:

    total = (
        db.query(
            func.coalesce(
                func.sum(
                    DetalleVenta.costo_venta
                ),
                0
            )
        )
        .join(
            Venta,
            Venta.id_venta == DetalleVenta.id_venta
        )
        .filter(
            extract("month", Venta.fecha) == mes,
            extract("year", Venta.fecha) == anio
        )
        .scalar()
    )

    return Decimal(total or 0)


# ============================================================
# UTILIDAD BRUTA
# ============================================================

def obtener_utilidad_bruta(db, mes: int, anio: int) -> Decimal:

    utilidad = (
        db.query(
            func.coalesce(
                func.sum(
                    DetalleVenta.utilidad_bruta
                ),
                0
            )
        )
        .join(
            Venta,
            Venta.id_venta == DetalleVenta.id_venta
        )
        .filter(
            extract("month", Venta.fecha) == mes,
            extract("year", Venta.fecha) == anio
        )
        .scalar()
    )

    return Decimal(utilidad or 0)


# ============================================================
# GASTOS DEL PERIODO
# ============================================================

def obtener_gastos(db, mes: int, anio: int) -> Decimal:

    gastos = (
        db.query(
            func.coalesce(
                func.sum(
                    Gasto.total
                ),
                0
            )
        )
        .filter(
            extract("month", Gasto.fecha) == mes,
            extract("year", Gasto.fecha) == anio
        )
        .scalar()
    )

    return Decimal(gastos or 0)


# ============================================================
# MARGEN BRUTO
# ============================================================

def calcular_margen_bruto(
    ventas: Decimal,
    utilidad_bruta: Decimal
) -> Decimal:

    if ventas <= 0:
        return Decimal("0")

    return (
        utilidad_bruta / ventas
    ) * Decimal("100")


# ============================================================
# UTILIDAD NETA
# ============================================================

def calcular_utilidad_neta(
    utilidad_bruta: Decimal,
    gastos: Decimal
) -> Decimal:

    return utilidad_bruta - gastos
# ============================================================
# META DE VENTAS
# ============================================================

def calcular_meta_ventas(
    gastos: Decimal,
    margen_bruto: Decimal
) -> Decimal:

    if margen_bruto <= 0:
        return Decimal("0")

    return gastos / (margen_bruto / Decimal("100"))


# ============================================================
# AVANCE HACIA LA META
# ============================================================

def calcular_avance(
    ventas: Decimal,
    meta: Decimal
) -> Decimal:

    if meta <= 0:
        return Decimal("0")

    return (ventas / meta) * Decimal("100")


# ============================================================
# FALTANTE
# ============================================================

def calcular_faltante(
    ventas: Decimal,
    meta: Decimal
) -> Decimal:

    if ventas >= meta:
        return Decimal("0")

    return meta - ventas


# ============================================================
# VENTAS DIARIAS NECESARIAS
# ============================================================

def calcular_ventas_diarias(
    faltante: Decimal,
    mes: int,
    anio: int
) -> Decimal:

    if faltante <= 0:
        return Decimal("0")

    hoy = date.today()

    # Si se consulta un período diferente al actual,
    # se toma la cantidad de días del mes.
    if hoy.month != mes or hoy.year != anio:

        dias_restantes = calendar.monthrange(anio, mes)[1]

    else:

        ultimo_dia = calendar.monthrange(anio, mes)[1]

        dias_restantes = ultimo_dia - hoy.day + 1

    if dias_restantes <= 0:
        dias_restantes = 1

    return faltante / Decimal(dias_restantes)


# ============================================================
# PROYECCIÓN DE VENTAS
# ============================================================

def calcular_proyeccion(
    ventas: Decimal,
    mes: int,
    anio: int
):

    hoy = date.today()

    if hoy.month != mes or hoy.year != anio:

        return ventas

    dias_transcurridos = hoy.day

    if dias_transcurridos <= 0:
        return ventas

    promedio = ventas / Decimal(dias_transcurridos)

    dias_mes = calendar.monthrange(anio, mes)[1]

    return promedio * Decimal(dias_mes)


# ============================================================
# MENSAJE GERENCIAL
# ============================================================

def generar_mensaje(
    avance: Decimal,
    faltante: Decimal,
    utilidad_neta: Decimal
):

    if avance >= 100:

        if utilidad_neta > 0:

            return (
                "Excelente. Ya cubriste todos los gastos del período. "
                "Las ventas adicionales incrementarán la utilidad del negocio."
            )

        return (
            "Ya alcanzaste el punto de equilibrio."
        )

    return (
        f"Aún faltan ${faltante:,.0f} "
        "en ventas para cubrir todos los gastos del período."
    )


# ============================================================
# INDICADOR DE SALUD FINANCIERA
# ============================================================

def calcular_salud_financiera(
    margen_bruto: Decimal
):

    if margen_bruto >= 40:
        return {
            "estado": "EXCELENTE",
            "color": "success"
        }

    if margen_bruto >= 25:
        return {
            "estado": "BUENA",
            "color": "warning"
        }

    return {
        "estado": "BAJA",
        "color": "danger"
    }
# ============================================================
# PUNTO DE EQUILIBRIO
# ============================================================

def obtener_punto_equilibrio(
    db,
    mes: int,
    anio: int
):

    # ===========================================
    # Estado de Resultados
    # ===========================================

    ventas = obtener_ventas(
        db,
        mes,
        anio
    )

    costo_ventas = obtener_costo_ventas(
        db,
        mes,
        anio
    )

    utilidad_bruta = obtener_utilidad_bruta(
        db,
        mes,
        anio
    )

    gastos = obtener_gastos(
        db,
        mes,
        anio
    )

    utilidad_neta = calcular_utilidad_neta(
        utilidad_bruta,
        gastos
    )

    margen_bruto = calcular_margen_bruto(
        ventas,
        utilidad_bruta
    )

    # ===========================================
    # Punto de Equilibrio
    # ===========================================

    meta = calcular_meta_ventas(
        gastos,
        margen_bruto
    )

    avance = calcular_avance(
        ventas,
        meta
    )

    faltante = calcular_faltante(
        ventas,
        meta
    )

    ventas_diarias = calcular_ventas_diarias(
        faltante,
        mes,
        anio
    )

    proyeccion = calcular_proyeccion(
        ventas,
        mes,
        anio
    )

    salud = calcular_salud_financiera(
        margen_bruto
    )

    mensaje = generar_mensaje(
        avance,
        faltante,
        utilidad_neta
    )

    # ===========================================
    # Respuesta
    # ===========================================

    return {

        "periodo": {

            "mes": mes,

            "anio": anio

        },

        "estado_resultados": {

            "ventas": round(ventas, 2),

            "costo_ventas": round(costo_ventas, 2),

            "utilidad_bruta": round(utilidad_bruta, 2),

            "gastos": round(gastos, 2),

            "utilidad_neta": round(utilidad_neta, 2),

            "margen_bruto": round(margen_bruto, 2)

        },

        "punto_equilibrio": {

            "meta": round(meta, 2),

            "avance": round(avance, 2),

            "faltante": round(faltante, 2),

            "ventas_diarias": round(
                ventas_diarias,
                2
            ),

            "proyeccion": round(
                proyeccion,
                2
            ),

            "cumplido": avance >= 100

        },

        "salud": {

            "estado": salud["estado"],

            "color": salud["color"]

        },

        "mensaje": mensaje

    }