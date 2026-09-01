from pydantic import BaseModel
from typing import List
from decimal import Decimal
from datetime import datetime


class DetalleComprobanteEgresoCreate(BaseModel):
    id_compra: int
    valor: Decimal


class ComprobanteEgresoCreate(BaseModel):
    numero: str | None = None
    id_proveedor: int
    observacion: str | None = None
    detalles: List[DetalleComprobanteEgresoCreate]


class DetalleComprobanteEgresoResponse(BaseModel):
    id_detalle: int
    id_egreso: int
    id_compra: int
    valor: Decimal
    factura_compra: str | None = None

    class Config:
        from_attributes = True


class ComprobanteEgresoResponse(BaseModel):
    id_egreso: int
    fecha: datetime
    numero: str | None = None
    id_proveedor: int
    proveedor_nombre: str | None = None
    id_usuario: int | None = None
    usuario_nombre: str | None = None
    observacion: str | None = None
    total: Decimal
    detalles: List[DetalleComprobanteEgresoResponse] = []

    class Config:
        from_attributes = True
