from sqlalchemy import Column, BigInteger, String, Boolean, DateTime
from sqlalchemy.sql import func

from database import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id_cliente = Column(BigInteger, primary_key=True, index=True)
    documento = Column(String(30))
    nombre = Column(String(200), nullable=False)
    telefono = Column(String(50))
    correo = Column(String(150))
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, server_default=func.now())
