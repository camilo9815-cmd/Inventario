from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import SessionLocal
from models.usuario import Usuario
from core.security import verify_password, create_access_token
from models.producto import Producto
from schemas.producto import ProductoCreate
from routers.auth import router as auth_router
from routers.productos import router as productos_router
from routers.proveedor import router as proveedor_router
from routers.compras import router as compras_router
from routers.medio_pago import router as medio_pago_router
from routers.ventas import router as ventas_router
from routers.clientes import router as clientes_router
from routers.gastos import router as gastos_router
from routers.recibos_caja import router as recibos_caja_router
from routers.comprobantes_egreso import router as comprobantes_egreso_router
from routers.punto_equilibrio import router  as punto_equilibrio_router
from routers import dashboard
from models.compra import Compra
from models.detalle_compra import DetalleCompra
from models.venta import Venta
from models.detalle_venta import DetalleVenta
from models.gasto import Gasto




from dependencies import get_current_user, require_admin
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
          "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(productos_router)
app.include_router(proveedor_router)
app.include_router(medio_pago_router)
app.include_router(compras_router)
app.include_router(ventas_router)
app.include_router(clientes_router)
app.include_router(gastos_router)
app.include_router(recibos_caja_router)
app.include_router(comprobantes_egreso_router)
app.include_router(punto_equilibrio_router)
app.include_router(
    dashboard.router,
    tags=["Dashboard"]
)


