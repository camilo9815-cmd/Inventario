from pydantic import BaseModel


class MedioPagoCreate(BaseModel):
    nombre: str


class MedioPagoResponse(BaseModel):
    id_medio_pago: int
    nombre: str
    activo: bool

    class Config:
        from_attributes = True