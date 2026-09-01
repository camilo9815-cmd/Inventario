from sqlalchemy import Column, BigInteger, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from database import Base


class Proveedor(Base):
    __tablename__ = "proveedores"

    id_proveedor = Column(BigInteger, primary_key=True, index=True)

    nit = Column(String(30))

    nombre = Column(String(200), nullable=False)

    telefono = Column(String(50))

    correo = Column(String(150))

    direccion = Column(String(250))

    activo = Column(Boolean, default=True)

    fecha_creacion = Column(
        DateTime,
        server_default=func.now()
    )



