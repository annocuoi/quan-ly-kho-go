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


def tao_pdf_bao_cao(
    df,
    tu_ngay,
    den_ngay,
    ten_kh,
    ten_go="Tất cả",
    loai_nhap="Tất cả"
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

    elements.append(
        Paragraph(
            f"Tên gỗ: {ten_go}",
            styles["Normal"]
        )
    )
    elements.append(
        Paragraph(
            f"Loại phiếu: {loai_nhap}",
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
            22,   # STT
            52,   # Ngày
            38,   # Phiếu
            70,   # Khách hàng
            45,   # Loại
            60,   # Tên gỗ
            60,   # Phân loại
            30,   # Dày
            30,   # Rộng
            30,   # Dài
            40,   # Kg
            40,   # Thanh
            40,   # M3
            55,   # Đơn giá
            60,   # Thành tiền
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

        ("FONTSIZE", (0, 0), (-1, -1), 7),

        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("TOPPADDING", (0, 0), (-1, 0), 6),

        ("BACKGROUND", (0, -1), (-1, -1), colors.lightgrey),

    ]))

    elements.append(table)

    doc.build(elements)

    buffer.seek(0)

    return buffer