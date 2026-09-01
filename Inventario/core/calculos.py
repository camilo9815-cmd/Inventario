from decimal import Decimal

def calcular_item(
    cantidad,
    costo_unitario,
    porcentaje_iva
):

    base = cantidad * costo_unitario

    iva = base * (
        porcentaje_iva / Decimal("100")
    )

    total = base + iva

    return {
        "base": base,
        "iva": iva,
        "total": total
    }

def calcular_totales(detalles):

    subtotal = Decimal("0")
    iva = Decimal("0")
    total = Decimal("0")

    for item in detalles:

        subtotal += item.base
        iva += item.iva
        total += item.total

    return {
        "subtotal": subtotal,
        "iva": iva,
        "total": total
    }