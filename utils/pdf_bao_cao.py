import io
import pandas as pd

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)

from utils.pdf_font import dang_ky_font


def tao_pdf_bao_cao(df, tu_ngay, den_ngay, ten_kh):

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

    elements.append(
        Paragraph("BÁO CÁO NHẬP HÀNG", title)
    )

    elements.append(Spacer(1, 10))

    elements.append(
        Paragraph(
            f"Từ ngày: {tu_ngay.strftime('%d/%m/%Y')} &nbsp;&nbsp;&nbsp;&nbsp; "
            f"Đến ngày: {den_ngay.strftime('%d/%m/%Y')}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"Khách hàng: {ten_kh}",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 12))

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
            40,   # Số phiếu
            65,   # Khách hàng
            70,   # Tên gỗ
            60,   # Ký hiệu
            35,   # Dày
            35,   # Rộng
            40,   # Dài
            55,   # Kg
            55,   # Thanh
            45,   # M3
            55,   # Đơn giá
            65,   # Thành tiền
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

        ("FONTSIZE", (0,0), (-1,-1), 7),

        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("TOPPADDING", (0, 0), (-1, 0), 6),

        ("BACKGROUND", (0, -1), (-1, -1), colors.lightgrey),

    ]))

    elements.append(table)

    doc.build(elements)

    buffer.seek(0)

    return buffer