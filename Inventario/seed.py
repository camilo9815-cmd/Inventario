from database import SessionLocal, Base, engine
from models.rol import Rol
from models.usuario import Usuario
from core.security import hash_password

Base.metadata.create_all(bind=engine)

def create_roles(db):
    if not db.query(Rol).first():
        db.add_all([
            Rol(id_rol=1, nombre="Administrador", descripcion="Acceso total", activo=True),
            Rol(id_rol=2, nombre="Vendedor", descripcion="Acceso limitado", activo=True),
        ])
        db.commit()


def create_admin(db):
    if not db.query(Usuario).first():
        admin = Usuario(
                nombre="Administrador",
    usuario="admin",
    correo="admin@inventario.com",
    password_hash=hash_password("Colombia"),
    id_rol=1,
    activo=True
        )
        db.add(admin)
        db.commit()


def run():
    db = SessionLocal()
    create_roles(db)
    create_admin(db)
    db.close()

if __name__ == "__main__":
    run()