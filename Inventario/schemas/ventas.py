from decimal import Decimal
from typing import List
from datetime import date

from pydantic import BaseModel


class DetalleVentaCreate(BaseModel):
    id_producto: int
    cantidad: Decimal
    precio_unitario: Decimal
    porcentaje_iva: Decimal


class VentaCreate(BaseModel):
    id_cliente: int | None = None
    factura: str | None = None
    id_medio_pago: int
    observacion: str | None = None
    fecha_vencimiento: date | None = None
    detalle: List[DetalleVentaCreate]



class VentaUpdate(VentaCreate):
    pass
