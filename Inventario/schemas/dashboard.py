from pydantic import BaseModel
from decimal import Decimal


class VentasDashboard(BaseModel):
    total: Decimal
    cantidad: int


class ComprasDashboard(BaseModel):
    total: Decimal
    cantidad: int


class GastosDashboard(BaseModel):
    total: Decimal


class UtilidadDashboard(BaseModel):
    total: Decimal


class TesoreriaDashboard(BaseModel):
    por_cobrar: Decimal
    por_pagar: Decimal
    flujo: Decimal


class InventarioDashboard(BaseModel):
    total: Decimal


class DashboardResponse(BaseModel):

    ventas: VentasDashboard

    compras: ComprasDashboard

    gastos: GastosDashboard

    utilidad: UtilidadDashboard

    tesoreria: TesoreriaDashboard

    inventario: InventarioDashboard

    top_clientes: list = []

    top_proveedores: list = []

    stock_bajo: list = []

    alertas: list = []