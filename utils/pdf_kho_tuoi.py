import io
import pandas as pd

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4, landscape
from datetime import datetime
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)

from utils.pdf_font import dang_ky_font


def tao_pdf_kho_tuoi(
    df,
    ten_kh,
    ten_go
):

    dang_ky_font()

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=10,
        rightMargin=10,
        topMargin=15,
        bottomMargin=15
    )

    styles = getSampleStyleSheet()

    styles["Normal"].fontName = "DejaVu"

    title = styles["Heading1"]
    title.fontName = "DejaVu-Bold"
    title.alignment = TA_CENTER

    elements = []

    # =====================
    # Tiêu đề
    # =====================

    elements.append(
        Paragraph(
            "KHO HÀNG TƯƠI",
            title
        )
    )

    elements.append(Spacer(1, 10))

    elements.append(
        Paragraph(
            f"<b>Khách hàng:</b> {ten_kh}",
            styles["Normal"]
        )
    )
    elements.append(
        Paragraph(
            f"<b>Loại gỗ:</b> {ten_go}",
            styles["Normal"]
        )
    )
    elements.append(
        Paragraph(
            f"<b>Ngày xuất:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 12))

    # =====================
    # Dữ liệu
    # =====================

    data = [list(df.columns)]

    for _, row in df.iterrows():

        data.append([
            "" if pd.isna(x) else str(x)
            for x in row
        ])

    table = Table(
        data,
        repeatRows=1,
        colWidths=[
            25,   # STT
            55,   # Ngày
            45,   # Phiếu
            80,   # Khách hàng
            90,   # Tên gỗ
            70,   # Ký hiệu
            35,   # Dày
            35,   # Rộng
            40,   # Dài
            60,   # Kg
            55,   # Thanh
            55,   # M3
        ]
    )

    table.setStyle(TableStyle([

        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4F81BD")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),

        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

        ("FONTNAME", (0, 0), (-1, 0), "DejaVu-Bold"),
        ("FONTNAME", (0, 1), (-1, -2), "DejaVu"),
        ("FONTNAME", (0, -1), (-1, -1), "DejaVu-Bold"),

        ("FONTSIZE", (0, 0), (-1, -1), 8),

        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("TOPPADDING", (0, 0), (-1, 0), 6),

        ("BACKGROUND", (0, -1), (-1, -1), colors.lightgrey),

    ]))

    elements.append(table)

    doc.build(elements)

    buffer.seek(0)

    return buffer