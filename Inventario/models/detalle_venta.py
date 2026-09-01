from sqlalchemy import Column, BigInteger, Numeric, ForeignKey

from database import Base


class DetalleVenta(Base):
    __tablename__ = "detalle_venta"

    id_detalle_venta = Column(BigInteger, primary_key=True, index=True)
    id_venta = Column(
        BigInteger,
        ForeignKey("ventas.id_venta", ondelete="CASCADE"),
        nullable=False
    )
    id_producto = Column(
        BigInteger,
        ForeignKey("productos.id_producto"),
        nullable=False
    )
    cantidad = Column(Numeric(18, 2), nullable=False)
    precio_unitario = Column(Numeric(18, 2), nullable=False)
    base = Column(Numeric(18, 2), nullable=False)
    iva = Column(Numeric(18, 2), nullable=False)
    total = Column(Numeric(18, 2), nullable=False)
    costo_promedio = Column(Numeric(18, 2), default=0)
    costo_venta = Column(Numeric(18, 2), default=0)
    utilidad_bruta = Column(Numeric(18, 2), default=0)
