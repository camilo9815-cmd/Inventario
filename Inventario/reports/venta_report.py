from io import BytesIO
import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image
)


def moneda(valor):
    return "${:,.0f}".format(float(valor))


def generar_pdf(venta):

    buffer = BytesIO()

    pdf = SimpleDocTemplate(
        buffer,
        pagesize=letter
    )

    estilos = getSampleStyleSheet()

    elementos = []

    # ==========================================================
    # LOGO
    # ==========================================================

    base_dir = os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )

    logo_path = os.path.join(
        os.path.dirname(base_dir),
        "frontend",
        "src",
        "assets",
        "logo.png"
    )

    if os.path.exists(logo_path):

        logo = Image(
            logo_path,
            width=360,
            height=180,
            kind="proportional"
        )

        encabezado = Table(
            [[logo]],
            colWidths=[500]
        )

        encabezado.setStyle(
            TableStyle([
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER"
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    5
                ),
            ])
        )

        # IMPORTANTE: agregar el encabezado al PDF
        elementos.append(encabezado)

    # ==========================================================
    # TITULO
    # ==========================================================

    elementos.append(
        Paragraph(
            "<b>INVENTARIO JF</b>",
            estilos["Title"]
        )
    )

    elementos.append(
        Paragraph(
            "Detalle de Venta",
            estilos["Heading2"]
        )
    )

    elementos.append(
        Spacer(1, 20)
    )

    # ==========================================================
    # INFORMACION DE LA VENTA
    # ==========================================================

    datos = [
        ["Venta", venta["id_venta"]],
        ["Cliente", venta["cliente"]],
        ["Factura", venta["factura"] or ""],
        ["Fecha", str(venta["fecha"])],
        ["Medio Pago", venta["medio_pago"]],
    ]

    tabla = Table(
        datos,
        colWidths=[120, 320]
    )

    tabla.setStyle(
        TableStyle([
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),
            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                colors.lightgrey
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, -1),
                "Helvetica"
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                8
            ),
        ])
    )

    elementos.append(tabla)

    elementos.append(
        Spacer(1, 20)
    )

    # ==========================================================
    # DETALLE
    # ==========================================================

    detalle = [
        [
            "Codigo",
            "Producto",
            "Cant.",
            "Precio",
            "IVA",
            "Total"
        ]
    ]

    for item in venta["detalle"]:

        detalle.append([
            item["codigo"],
            item["nombre"],
            item["cantidad"],
            moneda(item["precio_unitario"]),
            moneda(item["iva"]),
            moneda(item["total"]),
        ])

    tabla_detalle = Table(detalle)

    tabla_detalle.setStyle(
        TableStyle([
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#198754")
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "ALIGN",
                (2, 1),
                (-1, -1),
                "RIGHT"
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, 0),
                8
            ),
        ])
    )

    elementos.append(tabla_detalle)

    elementos.append(
        Spacer(1, 20)
    )

    # ==========================================================
    # TOTALES
    # ==========================================================

    resumen = [
        [
            "Subtotal",
            moneda(venta["subtotal"])
        ],
        [
            "IVA",
            moneda(venta["iva"])
        ],
        [
            "TOTAL",
            moneda(venta["total"])
        ],
    ]

    tabla_total = Table(
        resumen,
        colWidths=[120, 120]
    )

    tabla_total.setStyle(
        TableStyle([
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.black
            ),
            (
                "BACKGROUND",
                (0, 2),
                (-1, 2),
                colors.lightgrey
            ),
            (
                "ALIGN",
                (1, 0),
                (1, -1),
                "RIGHT"
            ),
        ])
    )

    elementos.append(tabla_total)

    # ==========================================================
    # GENERAR PDF
    # ==========================================================

    pdf.build(elementos)

    buffer.seek(0)

    return buffer