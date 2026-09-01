from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Numeric, String
from sqlalchemy.sql import func

from database import Base


class Gasto(Base):
    __tablename__ = "gastos"

    id_gasto = Column(BigInteger, primary_key=True, index=True)
    fecha = Column(DateTime, server_default=func.now())
    id_tipo_gasto = Column(BigInteger, ForeignKey("tipos_gasto.id_tipo_gasto"))
    id_categoria_gasto = Column(
        BigInteger,
        ForeignKey("categorias_gasto.id_categoria_gasto")
    )
    concepto = Column(String(250))
    base = Column(Numeric(18, 2), default=0)
    aplica_iva = Column(Boolean, default=False)
    iva = Column(Numeric(18, 2), default=0)
    total = Column(Numeric(18, 2), default=0)
    id_medio_pago = Column(BigInteger, ForeignKey("medios_pago.id_medio_pago"))
    id_usuario = Column(BigInteger, ForeignKey("usuarios.id_usuario"))
    observacion = Column(String(250))
