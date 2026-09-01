from sqlalchemy import Column, BigInteger, DateTime, Date, Numeric, String, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from database import Base

class ReciboCaja(Base):
    __tablename__ = "recibos_caja"

    id_recibo = Column(BigInteger, primary_key=True, index=True)
    fecha = Column(DateTime, server_default=func.now())
    numero = Column(String(30))
    id_cliente = Column(BigInteger, ForeignKey("clientes.id_cliente"), nullable=False)
    id_usuario = Column(BigInteger, ForeignKey("usuarios.id_usuario"))
    observacion = Column(String(250))
    total = Column(Numeric(18, 2), default=0)

    cliente = relationship("Cliente")
    usuario = relationship("Usuario")
    detalles = relationship("DetalleReciboCaja", back_populates="recibo", cascade="all, delete-orphan")


class DetalleReciboCaja(Base):
    __tablename__ = "detalle_recibo_caja"

    id_detalle = Column(BigInteger, primary_key=True, index=True)
    id_recibo = Column(BigInteger, ForeignKey("recibos_caja.id_recibo", ondelete="CASCADE"), nullable=False)
    id_venta = Column(BigInteger, ForeignKey("ventas.id_venta"), nullable=False)
    valor = Column(Numeric(18, 2), nullable=False)

    recibo = relationship("ReciboCaja", back_populates="detalles")
    venta = relationship("Venta")
