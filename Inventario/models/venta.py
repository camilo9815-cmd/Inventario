from sqlalchemy import Column, BigInteger, DateTime, Date, Numeric, String, ForeignKey
from sqlalchemy.sql import func

from database import Base


class Venta(Base):
    __tablename__ = "ventas"

    id_venta = Column(BigInteger, primary_key=True, index=True)
    fecha = Column(DateTime, server_default=func.now())
    id_cliente = Column(BigInteger, ForeignKey("clientes.id_cliente"))
    factura = Column(String(50))
    subtotal = Column(Numeric(18, 2), default=0)
    iva = Column(Numeric(18, 2), default=0)
    total = Column(Numeric(18, 2), default=0)
    id_medio_pago = Column(BigInteger, ForeignKey("medios_pago.id_medio_pago"))
    id_usuario = Column(BigInteger, ForeignKey("usuarios.id_usuario"))
    observacion = Column(String(250))
    valor_pagado = Column(Numeric(18, 2), default=0)
    saldo = Column(Numeric(18, 2), default=0)
    estado_pago = Column(String(20), default='PENDIENTE')
    fecha_vencimiento = Column(Date, nullable=True)

