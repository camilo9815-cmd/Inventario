from sqlalchemy import Column, BigInteger, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from database import Base


class MedioPago(Base):
    __tablename__ = "medios_pago"

    id_medio_pago = Column(BigInteger, primary_key=True, index=True)

    nombre = Column(String(100), nullable=False)

    activo = Column(Boolean, default=True)


compras = relationship(
    "Compra",
    back_populates="medio_pago"
) 