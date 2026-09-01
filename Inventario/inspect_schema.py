from sqlalchemy import create_engine, inspect
DATABASE_URL = "postgresql://parquesur:P*Sur.AMIGO_2022@192.168.150.5:5432/inventario_db"
engine = create_engine(DATABASE_URL)
try:
    inspector = inspect(engine)
    print("Tablas en la DB:", inspector.get_table_names())
except Exception as e:
    print("Error conectando:", e)
