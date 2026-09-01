from sqlalchemy import Column, BigInteger, String, Boolean
from database import Base

class Rol(Base):

    __tablename__ = "roles"

    id_rol = Column(BigInteger, primary_key=True)
    nombre = Column(String(50))
    descripcion = Column(String(200))
    activo = Column(Boolean)