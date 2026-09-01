from pydantic import BaseModel


class ClienteBase(BaseModel):
    documento: str | None = None
    nombre: str
    telefono: str | None = None
    correo: str | None = None
    activo: bool = True


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(ClienteBase):
    pass
