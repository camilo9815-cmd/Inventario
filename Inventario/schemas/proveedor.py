from pydantic import BaseModel


class ProveedorCreate(BaseModel):
    nit: str | None = None
    nombre: str
    telefono: str | None = None
    correo: str | None = None
    direccion: str | None = None


class ProveedorResponse(BaseModel):
    id_proveedor: int
    nit: str | None
    nombre: str
    telefono: str | None
    correo: str | None
    direccion: str | None
    activo: bool

    class Config:
        from_attributes = True