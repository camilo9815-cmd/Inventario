from sqlalchemy import BigInteger, Boolean, Column, String

from database import Base


class TipoGasto(Base):
    __tablename__ = "tipos_gasto"

    id_tipo_gasto = Column(BigInteger, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    activo = Column(Boolean, default=True)
