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


def tao_pdf_cong_no(
    df,
    ten_khach_hang,
    tong_khach_no,
    tong_minh_no,
    tong_khach_tra
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
        Paragraph(
            "BÁO CÁO CÔNG NỢ",
            title
        )
    )

    elements.append(Spacer(1, 10))

    elements.append(
        Paragraph(
            f"Khách hàng: {ten_khach_hang}",
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
            60,
            220,
            80,
            80,
            80
        ]
    )

    table.setStyle(TableStyle([

        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4F81BD")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),

        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

        ("FONTNAME", (0, 0), (-1, 0), "DejaVu-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "DejaVu"),

        ("FONTSIZE", (0, 0), (-1, -1), 9),

        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("TOPPADDING", (0, 0), (-1, 0), 6),

    ]))

    elements.append(table)

    elements.append(Spacer(1, 15))

    tong_con_no = (
        tong_khach_no
        - tong_minh_no
        - tong_khach_tra
    )

    tong = Table(
        [
            [
                "Nợ Phải Thu",
                "Nợ Phải Trả",
                "Khách trả",
                "Còn nợ"
            ],
            [
                f"{tong_khach_no:,.0f}",
                f"{tong_minh_no:,.0f}",
                f"{tong_khach_tra:,.0f}",
                f"{tong_con_no:,.0f}"
            ]
        ],
        colWidths=[120, 120, 120, 120]
    )

    tong.setStyle(TableStyle([

        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4F81BD")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

        ("BACKGROUND", (0, 1), (-1, 1), colors.whitesmoke),

        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),

        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

        ("FONTNAME", (0, 0), (-1, 0), "DejaVu-Bold"),
        ("FONTNAME", (0, 1), (-1, 1), "DejaVu-Bold"),

        ("FONTSIZE", (0, 0), (-1, -1), 11),

        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),

    ]))

    elements.append(tong)

    doc.build(elements)

    buffer.seek(0)

    return buffer.getvalue()