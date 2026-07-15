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


def tao_pdf_no_phai_tra(
    df,
    tu_ngay,
    den_ngay,
    ten_kh
):

    dang_ky_font()

    buffer = io.BytesIO()

    # Chiều rộng bảng
    col_widths = [
        30,     # STT
        45,     # Phiếu
        60,     # Ngày
        160,    # Khách hàng
        75,     # Phải trả
        75,     # Đã trả
        75,     # Còn lại
    ]

    table_width = sum(col_widths)

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
            "BÁO CÁO NỢ PHẢI TRẢ",
            title
        )
    )

    elements.append(Spacer(1, 10))

    def dong_thong_tin(text):

        t = Table(
            [[Paragraph(text, styles["Normal"])]],
            colWidths=[table_width],
            hAlign="CENTER"
        )

        t.setStyle(TableStyle([
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))

        elements.append(t)

    dong_thong_tin(
        f"<b>Từ ngày:</b> {tu_ngay.strftime('%d/%m/%Y')}"
    )

    dong_thong_tin(
        f"<b>Đến ngày:</b> {den_ngay.strftime('%d/%m/%Y')}"
    )

    dong_thong_tin(
        f"<b>Khách hàng:</b> {ten_kh}"
    )

    dong_thong_tin(
        f"<b>Ngày xuất:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}"
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

            elif cot in ["Phải trả", "Đã trả", "Còn lại"]:
                dong.append(f"{float(x):,.0f}")

            else:
                dong.append(str(x))

        data.append(dong)

    tong_phai_tra = df["Phải trả"].sum()
    tong_da_tra = df["Đã trả"].sum()
    tong_con_lai = df["Còn lại"].sum()

    data.append([
        "",
        "",
        "",
        "TỔNG CỘNG",
        f"{tong_phai_tra:,.0f}",
        f"{tong_da_tra:,.0f}",
        f"{tong_con_lai:,.0f}",
    ])

    table = Table(
        data,
        repeatRows=1,
        colWidths=col_widths,
        hAlign="CENTER"
    )

    table.setStyle(TableStyle([

        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4F81BD")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),

        ("FONTNAME", (0, 0), (-1, 0), "DejaVu-Bold"),
        ("FONTNAME", (0, 1), (-1, -2), "DejaVu"),
        ("FONTNAME", (0, -1), (-1, -1), "DejaVu-Bold"),

        ("FONTSIZE", (0, 0), (-1, -1), 8),

        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("TOPPADDING", (0, 0), (-1, 0), 6),

        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("ALIGN", (0, 1), (2, -2), "CENTER"),
        ("ALIGN", (3, 1), (3, -2), "LEFT"),
        ("ALIGN", (4, 1), (6, -2), "RIGHT"),

        ("ALIGN", (0, -1), (3, -1), "CENTER"),
        ("ALIGN", (4, -1), (6, -1), "RIGHT"),

        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

        ("BACKGROUND", (0, -1), (-1, -1), colors.lightgrey),

    ]))

    elements.append(table)
    elements.append(Spacer(1, 50))

    ky_ten = Table(
        [[
            Paragraph(
                "<b>Người lập biểu</b><br/><br/><br/><br/>(Ký, ghi rõ họ tên)",
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