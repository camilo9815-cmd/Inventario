from pydantic import BaseModel
from typing import List
from decimal import Decimal
from datetime import datetime


class DetalleReciboCajaCreate(BaseModel):
    id_venta: int
    valor: Decimal


class ReciboCajaCreate(BaseModel):
    numero: str | None = None
    id_cliente: int
    observacion: str | None = None
    detalles: List[DetalleReciboCajaCreate]


class DetalleReciboCajaResponse(BaseModel):
    id_detalle: int
    id_recibo: int
    id_venta: int
    valor: Decimal
    factura_venta: str | None = None

    class Config:
        from_attributes = True


class ReciboCajaResponse(BaseModel):
    id_recibo: int
    fecha: datetime
    numero: str | None = None
    id_cliente: int
    cliente_nombre: str | None = None
    id_usuario: int | None = None
    usuario_nombre: str | None = None
    observacion: str | None = None
    total: Decimal
    detalles: List[DetalleReciboCajaResponse] = []

    class Config:
        from_attributes = True
