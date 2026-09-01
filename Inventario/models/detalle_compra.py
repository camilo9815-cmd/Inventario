from sqlalchemy import (
    Column,
    BigInteger,
    Numeric,
    ForeignKey
)

from sqlalchemy.orm import relationship

from database import Base


class DetalleCompra(Base):
    __tablename__ = "detalle_compra"

    id_detalle_compra = Column(
        BigInteger,
        primary_key=True,
        index=True
    )

    id_compra = Column(
        BigInteger,
        ForeignKey("compras.id_compra"),
        nullable=False
    )

    id_producto = Column(
        BigInteger,
        ForeignKey("productos.id_producto"),
        nullable=False
    )

    cantidad = Column(
        Numeric(18,2),
        nullable=False
    )

    costo_unitario = Column(
        Numeric(18,2),
        nullable=False
    )

    base = Column(
        Numeric(18,2),
        nullable=False
    )

    iva = Column(
        Numeric(18,2),
        nullable=False
    )

    total = Column(
        Numeric(18,2),
        nullable=False
    )

compra = relationship(
    "Compra",
    back_populates="detalle"
)

producto = relationship(
    "Producto",
    back_populates="detalle_compra"
)