from sqlalchemy import (
    Column,
    BigInteger,
    DateTime,
    Date,
    Numeric,
    String,
    ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class Compra(Base):
    __tablename__ = "compras"

    id_compra = Column(
        BigInteger,
        primary_key=True,
        index=True
    )

    fecha = Column(
        DateTime,
        server_default=func.now()
    )

    id_proveedor = Column(
        BigInteger,
        ForeignKey("proveedores.id_proveedor"),
        nullable=False
    )

    factura = Column(String(50))

    subtotal = Column(
        Numeric(18, 2),
        default=0
    )

    iva = Column(
        Numeric(18, 2),
        default=0
    )

    total = Column(
        Numeric(18, 2),
        default=0
    )

    id_medio_pago = Column(
        BigInteger,
        ForeignKey("medios_pago.id_medio_pago")
    )

    observacion = Column(String(250))

    id_usuario = Column(
        BigInteger,
        ForeignKey("usuarios.id_usuario")
    )

    valor_pagado = Column(Numeric(18, 2), default=0)
    saldo = Column(Numeric(18, 2), default=0)
    estado_pago = Column(String(20), default='PENDIENTE')
    fecha_vencimiento = Column(Date, nullable=True)



detalle = relationship(
    "DetalleCompra",
    back_populates="compra",
    cascade="all, delete-orphan"
)

proveedor = relationship(
    "Proveedor",
    back_populates="compras"
)

usuario = relationship(
    "Usuario",
    back_populates="compras"
)

medio_pago = relationship(
    "MedioPago",
    back_populates="compras"
)