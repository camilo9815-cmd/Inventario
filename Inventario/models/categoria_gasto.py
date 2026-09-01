from sqlalchemy import BigInteger, Boolean, Column, String

from database import Base


class CategoriaGasto(Base):
    __tablename__ = "categorias_gasto"

    id_categoria_gasto = Column(BigInteger, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    activo = Column(Boolean, default=True)
