from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)


def moneda(valor):

    return "${:,.0f}".format(float(valor))


def generar_pdf(compra):

    buffer = BytesIO()

    pdf = SimpleDocTemplate(

        buffer,

        pagesize=letter

    )

    estilos = getSampleStyleSheet()

    elementos = []

    elementos.append(

        Paragraph(

            "<b>INVENTARIO JF</b>",

            estilos["Title"]

        )

    )

    elementos.append(

        Paragraph(

            "Detalle de Compra",

            estilos["Heading2"]

        )

    )

    elementos.append(Spacer(1, 20))

    datos = [

        ["Compra", compra["id_compra"]],

        ["Proveedor", compra["proveedor"]],

        ["Factura", compra["factura"]],

        ["Fecha", str(compra["fecha"])],

        ["Medio Pago", compra["medio_pago"]]

    ]

    tabla = Table(datos, colWidths=[120,320])

    tabla.setStyle(TableStyle([

        ("GRID",(0,0),(-1,-1),0.5,colors.grey),

        ("BACKGROUND",(0,0),(0,-1),colors.lightgrey),

        ("FONTNAME",(0,0),(-1,-1),"Helvetica"),

        ("BOTTOMPADDING",(0,0),(-1,-1),8)

    ]))

    elementos.append(tabla)

    elementos.append(Spacer(1,20))

    detalle = [

        [

            "Código",

            "Producto",

            "Cant.",

            "Costo",

            "IVA",

            "Total"

        ]

    ]

    for item in compra["detalle"]:

        detalle.append([

            item["codigo"],

            item["nombre"],

            item["cantidad"],

            moneda(item["costo_unitario"]),

            moneda(item["iva"]),

            moneda(item["total"])

        ])

    tabla_detalle = Table(detalle)

    tabla_detalle.setStyle(TableStyle([

        ("GRID",(0,0),(-1,-1),0.5,colors.grey),

        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#0d6efd")),

        ("TEXTCOLOR",(0,0),(-1,0),colors.white),

        ("ALIGN",(2,1),(-1,-1),"RIGHT"),

        ("BOTTOMPADDING",(0,0),(-1,0),8)

    ]))

    elementos.append(tabla_detalle)

    elementos.append(Spacer(1,20))

    resumen = [

        ["Subtotal", moneda(compra["subtotal"])],

        ["IVA", moneda(compra["iva"])],

        ["TOTAL", moneda(compra["total"])]

    ]

    tabla_total = Table(resumen, colWidths=[120,120])

    tabla_total.setStyle(TableStyle([

        ("GRID",(0,0),(-1,-1),0.5,colors.black),

        ("BACKGROUND",(0,2),(-1,2),colors.lightgrey),

        ("ALIGN",(1,0),(1,-1),"RIGHT")

    ]))

    elementos.append(tabla_total)

    pdf.build(elementos)

    buffer.seek(0)

    return buffer