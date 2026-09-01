from sqlalchemy import create_engine, text

DATABASE_URL =  "postgresql://parquesur:P*Sur.AMIGO_2022@192.168.150.5:5432/inventario_db"

engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT current_database();"))
        print("Base de datos:", result.scalar())

    print("Conexion exitosa")
except Exception as e:
    print("Error:", e)