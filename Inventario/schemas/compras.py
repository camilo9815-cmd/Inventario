from pydantic import BaseModel
from typing import List
from decimal import Decimal
from datetime import date


class DetalleCompraCreate(BaseModel):
    id_producto: int
    cantidad: Decimal
    costo_unitario: Decimal
    porcentaje_iva: Decimal


class CompraCreate(BaseModel):
    id_proveedor: int
    factura: str
    id_medio_pago: int
    observacion: str | None = None
    fecha_vencimiento: date | None = None
    detalle: List[DetalleCompraCreate]


class CompraUpdate(CompraCreate):
    pass
