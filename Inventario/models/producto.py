from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


from database import Base


class Producto(Base):
    __tablename__ = "productos"

    id_producto = Column(Integer, primary_key=True, index=True)

    codigo = Column(String(30), unique=True, nullable=False)

    nombre = Column(String(200), nullable=False)

    id_categoria = Column(Integer, nullable=False)

    stock_minimo = Column(Numeric(18, 2), default=0)

    precio_venta_sugerido = Column(Numeric(18, 2), default=0)

    activo = Column(Boolean, default=True)

    fecha_creacion = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    
    stock_actual = Column(Numeric(18, 2), default=0)

    costo_promedio = Column(Numeric(18, 2), default=0)

    ultimo_costo = Column(Numeric(18, 2), default=0)

detalle_compra = relationship(
    "DetalleCompra",
    back_populates="producto"
)

detalle_venta = relationship(
    "DetalleVenta",
    back_populates="producto"
)
