from sqlalchemy import Column, BigInteger, DateTime, Date, Numeric, String, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from database import Base

class ComprobanteEgreso(Base):
    __tablename__ = "comprobantes_egreso"

    id_egreso = Column(BigInteger, primary_key=True, index=True)
    fecha = Column(DateTime, server_default=func.now())
    numero = Column(String(30))
    id_proveedor = Column(BigInteger, ForeignKey("proveedores.id_proveedor"))
    id_usuario = Column(BigInteger, ForeignKey("usuarios.id_usuario"))
    observacion = Column(String(250))
    total = Column(Numeric(18, 2), default=0)

    proveedor = relationship("Proveedor")
    usuario = relationship("Usuario")
    detalles = relationship("DetalleComprobanteEgreso", back_populates="comprobante", cascade="all, delete-orphan")


class DetalleComprobanteEgreso(Base):
    __tablename__ = "detalle_comprobante_egreso"

    id_detalle = Column(BigInteger, primary_key=True, index=True)
    id_egreso = Column(BigInteger, ForeignKey("comprobantes_egreso.id_egreso", ondelete="CASCADE"))
    id_compra = Column(BigInteger, ForeignKey("compras.id_compra"))
    valor = Column(Numeric(18, 2))

    comprobante = relationship("ComprobanteEgreso", back_populates="detalles")
    compra = relationship("Compra")
