import io

from datetime import datetime
from reportlab.lib.styles import ParagraphStyle

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    SimpleDocTemplate,
)

from utils.pdf_font import dang_ky_font


def dinh_dang_tien(value):
    try:
        return f"{float(value):,.0f}"
    except:
        return "0"


def tao_pdf_chi_tiet_cong_no(
    phieu,
    ds_go,
    ds_tt,
):

    dang_ky_font()

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=45,      # đổi từ 10 -> 45
        rightMargin=45,
        topMargin=15,
        bottomMargin=15,
    )

    styles = getSampleStyleSheet()

    styles["Normal"].fontName = "DejaVu"
    heading2 = ParagraphStyle(
        "HeadingVN",
        parent=styles["Normal"],
        fontName="DejaVu-Bold",
        fontSize=12,
    )

    title = styles["Heading1"]
    title.fontName = "DejaVu-Bold"
    title.alignment = TA_CENTER

    elements = []

    if phieu["loai"] == "CONG_SAY":
        tieu_de = "PHIẾU NỢ PHẢI THU"
    else:
        tieu_de = "PHIẾU NỢ PHẢI TRẢ"

    elements.append(
        Paragraph(
            tieu_de,
            title,
        )
    )

    elements.append(Spacer(1, 10))

    info = Table(
        [[Paragraph(f"<b>Số phiếu:</b> {phieu['so_phieu']}", styles["Normal"])],
        [Paragraph(f"<b>Khách hàng:</b> {phieu['khach_hang']}", styles["Normal"])],
        [Paragraph(f"<b>Ngày:</b> {phieu['ngay'].strftime('%d/%m/%Y')}", styles["Normal"])],
        [Paragraph(f"<b>Ngày in:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles["Normal"])]],
        colWidths=[300]
    )

    info.hAlign = "LEFT"

    info.setStyle(TableStyle([
        ("LEFTPADDING", (0,0), (-1,-1), 0),      # <-- đổi 80 thành 0
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ("TOPPADDING", (0,0), (-1,-1), 0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 1),
    ]))

    elements.append(info)
    elements.append(Spacer(1, 12))
    # ==========================
    # BẢNG CÔNG NỢ
    # ==========================

    data = [[
        "STT",
        "Ngày",
        "Nội dung",
        "Quy cách",
        "Kg",
        "Thanh",
        "m³",
        "Đơn giá",
        "Thành tiền",
        "Thanh toán",
        "Ghi chú",
    ]]

    tong_kg = 0
    tong_thanh = 0
    tong_m3 = 0
    tong_tien = 0
    tong_thanh_toan = 0

    stt = 1

    for item in ds_go:

        if item["kieu_tinh"] == "TRONG_LUONG":

            quy_cach = ""
            kg = float(item["so_luong"])
            thanh = ""
            m3 = ""

        else:

            quy_cach = f'{int(item["day"])}x{int(item["rong"])}x{int(item["dai"])}'
            kg = ""
            thanh = int(item["so_thanh"])
            m3 = f'{float(item["so_luong"]):.3f}'

        tong_kg += float(item["so_luong"] if item["kieu_tinh"] == "TRONG_LUONG" else 0)
        tong_thanh += int(item["so_thanh"] or 0)
        tong_m3 += float(item["so_luong"] if item["kieu_tinh"] == "M3" else 0)
        tong_tien += float(item["thanh_tien"])

        data.append([
            stt,
            phieu["ngay"].strftime("%d/%m/%Y"),
            item["ten"],
            quy_cach,
            "" if kg == "" else f"{kg:,.0f}",
            thanh,
            m3,
            dinh_dang_tien(item["don_gia"]),
            dinh_dang_tien(item["thanh_tien"]),
            "",
            "",
        ])

        stt += 1

    lan_tt = 1

    for item in ds_tt:

        so_tien = float(item["so_tien"])
        tong_thanh_toan += so_tien

        data.append([
            stt,
            item["ngay"].strftime("%d/%m/%Y"),
            item.get("ghi_chu") or f"Thanh toán lần {lan_tt}",
            "",
            "",
            "",
            "",
            "",
            "",
            dinh_dang_tien(so_tien),
            "",
        ])

        stt += 1
        lan_tt += 1

    data.append([
        "",
        "",
        "Tổng cộng",
        "",
        "" if tong_kg == 0 else f"{tong_kg:,.0f}",
        f"{tong_thanh:,}",
        "" if tong_m3 == 0 else f"{tong_m3:.3f}",
        "",
        dinh_dang_tien(tong_tien),
        dinh_dang_tien(tong_thanh_toan),
        "",
    ])
    chenh_lech = tong_tien - tong_thanh_toan

    if chenh_lech >= 0:
        data.append([
            "",
            "",
            "Còn nợ chưa thanh toán",
            "",
            "",
            "",
            "",
            "",
            dinh_dang_tien(chenh_lech),   # Thành tiền
            "",
            "",
        ])
    else:
        data.append([
            "",
            "",
            "Số dư tạm ứng",
            "",
            "",
            "",
            "",
            "",
            "",                            # Thành tiền để trống
            dinh_dang_tien(abs(chenh_lech)),  # Hiện ở cột Thanh toán
            "",
        ])

    table = Table(
        data,
        repeatRows=1,
        colWidths=[
            35,   # STT
            60,   # Ngày
            140,  # Nội dung
            80,   # Quy cách
            45,   # Kg
            45,   # Thanh
            45,   # m3
            70,   # Đơn giá
            80,   # Thành tiền
            80,   # Thanh toán
            70,   # Ghi chú
        ],
    )
    table.hAlign = "LEFT" 

    table.setStyle(TableStyle([

        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4F81BD")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),

        ("FONTNAME", (0, 0), (-1, 0), "DejaVu-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "DejaVu"),

        ("FONTSIZE", (0, 0), (-1, -1), 8),

        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("TOPPADDING", (0, 0), (-1, 0), 6),

        ("ALIGN", (0, 0), (-1, 0), "CENTER"),

        ("ALIGN", (0, 1), (1, -1), "CENTER"),
        ("ALIGN", (2, 1), (3, -1), "LEFT"),
        ("ALIGN", (4, 1), (9, -1), "RIGHT"),

        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

        ("BACKGROUND", (0, -2), (-1, -1), colors.HexColor("#F2F2F2")),

        ("FONTNAME", (0, -2), (-1, -1), "DejaVu-Bold"),

    ]))

    elements.append(table)
    elements.append(Spacer(1,20))
    # ==========================
    # CHỮ KÝ
    # ==========================

    ky = Table(
        [[
            "Người lập phiếu",
            "",
            "Khách hàng",
        ]],
        colWidths=[
            250,
            80,
            250,
        ]
    )

    ky.setStyle(TableStyle([

        ("FONTNAME", (0,0), (-1,-1), "DejaVu-Bold"),

        ("ALIGN", (0,0), (-1,-1), "CENTER"),

        ("TOPPADDING", (0,0), (-1,-1), 40),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),

    ]))

    elements.append(ky)

    doc.build(elements)

    buffer.seek(0)

    return buffer