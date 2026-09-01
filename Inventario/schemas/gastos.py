from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class GastoCreate(BaseModel):
    fecha: datetime | None = None
    id_tipo_gasto: int
    id_categoria_gasto: int
    concepto: str
    base: Decimal
    aplica_iva: bool = False
    porcentaje_iva: Decimal = Decimal("19")
    id_medio_pago: int
    observacion: str | None = None
