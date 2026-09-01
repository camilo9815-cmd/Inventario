from database import Base, engine

# IMPORTAR TODOS LOS MODELOS
from models.rol import Rol
from models.usuario import Usuario
from models.producto import Producto

Base.metadata.create_all(bind=engine)

print("Tablas creadas correctamente")