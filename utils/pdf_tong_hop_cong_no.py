import io
import pandas as pd

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)
from datetime import datetime

from utils.pdf_font import dang_ky_font


def tao_pdf_tong_hop_cong_no(df):

    dang_ky_font()

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=35,
        rightMargin=35,
        topMargin=30,
        bottomMargin=30
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
            "BÁO CÁO TỔNG HỢP CÔNG NỢ",
            title
        )
    )

    elements.append(Spacer(1, 10))

    ngay_xuat = Table(
        [[Paragraph(
            f"<b>Ngày xuất:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            styles["Normal"]
        )]],
        colWidths=[455],
        hAlign="CENTER"
    )

    ngay_xuat.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))

    elements.append(ngay_xuat)

    elements.append(Spacer(1, 12))

    # =====================
    # Dữ liệu
    # =====================

    data = [list(df.columns)]

    for _, row in df.iterrows():

        dong = []

        for cot, x in zip(df.columns, row):

            if pd.isna(x):
                dong.append("")

            elif cot in ["Phải thu", "Phải trả", "Chênh lệch"]:
                dong.append(f"{float(x):,.0f}")

            else:
                dong.append(str(x))

        data.append(dong)

    data.append([
        "",
        "TỔNG CỘNG",
        f"{df['Phải thu'].sum():,.0f}",
        f"{df['Phải trả'].sum():,.0f}",
        f"{df['Chênh lệch'].sum():,.0f}",
    ])

    table = Table(
        data,
        repeatRows=1,
        colWidths=[
            30,
            170,
            85,
            85,
            85,
        ],
        hAlign="CENTER"
    )

    table.setStyle(TableStyle([

        # Header
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4F81BD")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

        # Grid
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),

        # Font
        ("FONTNAME", (0, 0), (-1, 0), "DejaVu-Bold"),
        ("FONTNAME", (0, 1), (-1, -2), "DejaVu"),
        ("FONTNAME", (0, -1), (-1, -1), "DejaVu-Bold"),

        ("FONTSIZE", (0, 0), (-1, -1), 8),

        # Padding
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("TOPPADDING", (0, 0), (-1, 0), 6),

        # Căn lề
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),   # Header
        ("ALIGN", (0, 1), (0, -2), "CENTER"),   # STT
        ("ALIGN", (1, 1), (1, -2), "LEFT"),     # Khách hàng
        ("ALIGN", (2, 1), (4, -2), "RIGHT"),    # Tiền

        # Dòng tổng
        ("ALIGN", (0, -1), (1, -1), "CENTER"),
        ("ALIGN", (2, -1), (4, -1), "RIGHT"),

        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

        # Dòng tổng
        ("BACKGROUND", (0, -1), (-1, -1), colors.lightgrey),

    ]))

    elements.append(table)

    elements.append(Spacer(1, 50))

    ky_ten = Table(
        [[
            Paragraph(
                "<b>Người lập biểu</b>",
                styles["Normal"]
            )
        ]],
        colWidths=[150],
        hAlign="RIGHT"
    )

    ky_ten.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, -1), "DejaVu-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 55),  # Chừa chỗ ký
    ]))

    elements.append(ky_ten)

    doc.build(elements)

    buffer.seek(0)

    return buffer