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


def tao_pdf_kho_da_phan_loai(
    df,
    ten_kh,
    ten_go,
    ten_phan_loai
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
            "KHO KHÔ ĐÃ PHÂN LOẠI",
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
            f"<b>Phân loại:</b> {ten_phan_loai}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"<b>Ngày xuất báo cáo:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}",
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

    # Có cột Phân loại hay không
    if "Phân loại" in df.columns:

        col_widths = [
            25,   # STT
            55,   # Ngày
            45,   # Phiếu
            80,   # Khách
            90,   # Gỗ
            75,   # Ký hiệu
            75,   # Phân loại
            35,   # Dày
            35,   # Rộng
            40,   # Dài
            55,   # Kg
            55,   # Thanh
            55,   # M3
        ]

    else:

        col_widths = [
            25,
            55,
            45,
            80,
            100,
            80,
            35,
            35,
            40,
            60,
            60,
            60,
        ]

    table = Table(
        data,
        repeatRows=1,
        colWidths=col_widths
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