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
from datetime import datetime

from utils.pdf_font import dang_ky_font


def tao_pdf_no_phai_thu(
    df,
    tu_ngay,
    den_ngay,
    ten_kh
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
            "BÁO CÁO NỢ PHẢI THU",
            title
        )
    )

    elements.append(Spacer(1, 10))

    elements.append(
        Paragraph(
            f"<b>Từ ngày:</b> {tu_ngay.strftime('%d/%m/%Y')}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"<b>Đến ngày:</b> {den_ngay.strftime('%d/%m/%Y')}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"<b>Khách hàng:</b> {ten_kh}",
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

        dong = []

        for cot, x in zip(df.columns, row):

            if pd.isna(x):
                dong.append("")

            elif cot in ["Phải thu", "Đã thu", "Còn lại"]:
                dong.append(f"{float(x):,.0f}")

            else:
                dong.append(str(x))

        data.append(dong)

    tong_phai_thu = df["Phải thu"].sum()
    tong_da_thu = df["Đã thu"].sum()
    tong_con_lai = df["Còn lại"].sum()

    data.append([
        "",
        "",
        "",
        "TỔNG CỘNG",
        f"{tong_phai_thu:,.0f}",
        f"{tong_da_thu:,.0f}",
        f"{tong_con_lai:,.0f}",
    ])

    table = Table(
        data,
        repeatRows=1,
        colWidths=[
            30,     # STT
            45,     # Phiếu
            60,     # Ngày
            180,    # Khách hàng
            90,     # Phải thu
            90,     # Đã thu
            90,     # Còn lại
        ]
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

        # Header căn giữa
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),

        # STT - Phiếu - Ngày
        ("ALIGN", (0, 1), (2, -2), "CENTER"),

        # Khách hàng
        ("ALIGN", (3, 1), (3, -2), "LEFT"),

        # Tiền
        ("ALIGN", (4, 1), (6, -2), "RIGHT"),

        # Dòng tổng
        ("ALIGN", (0, -1), (3, -1), "CENTER"),
        ("ALIGN", (4, -1), (6, -1), "RIGHT"),

        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

        # Dòng tổng màu xám
        ("BACKGROUND", (0, -1), (-1, -1), colors.lightgrey),

    ]))

    elements.append(table)

    doc.build(elements)

    buffer.seek(0)

    return buffer