from database import SessionLocal

from models.producto import Producto
from models.compra import Compra
from models.detalle_compra import DetalleCompra


db = SessionLocal()

try:

    print("=" * 70)
    print("RECALCULANDO COSTOS DEL INVENTARIO")
    print("=" * 70)

    productos = (
        db.query(Producto)
        .join(
            DetalleCompra,
            Producto.id_producto == DetalleCompra.id_producto
        )
        .distinct()
        .all()
    )

    for producto in productos:

        stock = 0
        costo_promedio = 0
        ultimo_costo = 0

        compras = (
            db.query(DetalleCompra)
            .join(
                Compra,
                Compra.id_compra == DetalleCompra.id_compra
            )
            .filter(
                DetalleCompra.id_producto == producto.id_producto
            )
            .order_by(
                Compra.fecha.asc(),
                DetalleCompra.id_detalle_compra.asc()
            )
            .all()
        )

        for detalle in compras:

            cantidad = float(detalle.cantidad)
            costo = float(detalle.costo_unitario)

            if stock == 0:

                costo_promedio = costo

            else:

                costo_promedio = (
                    (stock * costo_promedio)
                    +
                    (cantidad * costo)
                ) / (stock + cantidad)

            stock += cantidad
            ultimo_costo = costo

        producto.stock_actual = stock
        producto.costo_promedio = costo_promedio
        producto.ultimo_costo = ultimo_costo

        print(
            f"[{producto.codigo}] {producto.nombre}"
        )
        print(
            f"   Stock.............: {stock}"
        )
        print(
            f"   Último costo......: {ultimo_costo:,.2f}"
        )
        print(
            f"   Costo promedio....: {costo_promedio:,.2f}"
        )
        print("-" * 70)

    db.commit()

    print("=" * 70)
    print("PROCESO FINALIZADO CORRECTAMENTE")
    print("=" * 70)

except Exception as e:

    db.rollback()

    print("ERROR:", e)

finally:

    db.close()