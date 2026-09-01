from pydantic import BaseModel


class ProductoCreate(BaseModel):
    codigo: str
    nombre: str
    id_categoria: int
    stock_minimo: float
    precio_venta_sugerido: float


class ProductoResponse(BaseModel):
    id_producto: int
    codigo: str
    nombre: str
    id_categoria: int
    stock_minimo: float
    precio_venta_sugerido: float
    activo: bool

    class Config:
        from_attributes = True