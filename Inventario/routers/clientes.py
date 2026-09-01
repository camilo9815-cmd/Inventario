from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from dependencies import get_current_user
from models.cliente import Cliente
from schemas.clientes import ClienteCreate, ClienteUpdate

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/clientes")
def listar_clientes(
    incluir_inactivos: bool = False,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    consulta = db.query(Cliente)
    if not incluir_inactivos:
        consulta = consulta.filter(Cliente.activo == True)
    return consulta.order_by(Cliente.nombre).all()


@router.get("/clientes/{id_cliente}")
def obtener_cliente(
    id_cliente: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    cliente = db.query(Cliente).filter(Cliente.id_cliente == id_cliente).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado.")
    return cliente


@router.post("/clientes")
def crear_cliente(
    datos: ClienteCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    cliente = Cliente(**datos.model_dump())
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente


@router.put("/clientes/{id_cliente}")
def actualizar_cliente(
    id_cliente: int,
    datos: ClienteUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    cliente = db.query(Cliente).filter(Cliente.id_cliente == id_cliente).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado.")
    for campo, valor in datos.model_dump().items():
        setattr(cliente, campo, valor)
    db.commit()
    db.refresh(cliente)
    return cliente


@router.delete("/clientes/{id_cliente}")
def eliminar_cliente(
    id_cliente: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    cliente = db.query(Cliente).filter(Cliente.id_cliente == id_cliente).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado.")
    cliente.activo = False
    db.commit()
    return {"mensaje": "Cliente desactivado correctamente."}
