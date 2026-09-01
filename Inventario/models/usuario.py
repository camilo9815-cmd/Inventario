from sqlalchemy import Column, BigInteger, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import relationship

from database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(BigInteger, primary_key=True, index=True)

    nombre = Column(String(150))

    usuario = Column(String(50), unique=True)

    correo = Column(String(150))

    password_hash = Column(String(255))

    id_rol = Column(BigInteger, ForeignKey("roles.id_rol"))

    activo = Column(Boolean, default=True)

