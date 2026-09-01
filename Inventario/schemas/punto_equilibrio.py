from decimal import Decimal
from pydantic import BaseModel


# ==========================================================
# PERIODO
# ==========================================================

class Periodo(BaseModel):

    mes: int

    anio: int


# ==========================================================
# ESTADO DE RESULTADOS
# ==========================================================

class EstadoResultados(BaseModel):

    ventas: Decimal

    costo_ventas: Decimal

    utilidad_bruta: Decimal

    gastos: Decimal

    utilidad_neta: Decimal

    margen_bruto: Decimal


# ==========================================================
# PUNTO DE EQUILIBRIO
# ==========================================================

class PuntoEquilibrio(BaseModel):

    meta: Decimal

    avance: Decimal

    faltante: Decimal

    ventas_diarias: Decimal

    proyeccion: Decimal

    cumplido: bool


# ==========================================================
# SALUD FINANCIERA
# ==========================================================

class SaludFinanciera(BaseModel):

    estado: str

    color: str


# ==========================================================
# RESPUESTA
# ==========================================================

class PuntoEquilibrioResponse(BaseModel):

    periodo: Periodo

    estado_resultados: EstadoResultados

    punto_equilibrio: PuntoEquilibrio

    salud: SaludFinanciera

    mensaje: str