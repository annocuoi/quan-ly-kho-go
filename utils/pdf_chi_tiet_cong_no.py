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
        leftMargin=10,
        rightMargin=10,
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

    elements.append(
        Paragraph(
            "CHI TIẾT PHIẾU CÔNG NỢ",
            title,
        )
    )

    elements.append(Spacer(1, 10))

    elements.append(
        Paragraph(
            f"<b>Số phiếu:</b> {phieu['so_phieu']}",
            styles["Normal"],
        )
    )

    elements.append(
        Paragraph(
            f"<b>Khách hàng:</b> {phieu['khach_hang']}",
            styles["Normal"],
        )
    )

    elements.append(
        Paragraph(
            f"<b>Ngày:</b> {phieu['ngay'].strftime('%d/%m/%Y')}",
            styles["Normal"],
        )
    )

    elements.append(
        Paragraph(
            f"<b>Ngày xuất:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            styles["Normal"],
        )
    )

    elements.append(Spacer(1, 12))
    # ==========================
    # BẢNG CHI TIẾT GỖ
    # ==========================

    data = [[
        "STT",
        "Tên gỗ",
        "Quy cách",
        "Kg",
        "Thanh",
        "m³",
        "Đơn giá",
        "Thành tiền",
    ]]

    tong_kg = 0
    tong_thanh = 0
    tong_m3 = 0
    tong_tien = 0

    for i, item in enumerate(ds_go, start=1):

        if item["kieu_tinh"] == "TRONG_LUONG":

            quy_cach = "-"

            kg = item["so_luong"]
            thanh = ""
            m3 = ""

        else:

            quy_cach = f'{int(item["day"])}x{int(item["rong"])}x{int(item["dai"])}'

            kg = ""
            thanh = f'{int(item["so_thanh"]):,}'
            m3 = f'{float(item["so_luong"]):.3f}'

        tong_kg += float(item["so_luong"] if item["kieu_tinh"] == "TRONG_LUONG" else 0)

        tong_thanh += int(item["so_thanh"] or 0)

        tong_m3 += float(item["so_luong"] if item["kieu_tinh"] == "M3" else 0)

        tong_tien += float(item["thanh_tien"])

        data.append([
            i,
            item["ten"],
            quy_cach,
            kg if kg == "" else f"{float(kg):,.0f}",
            thanh,
            m3,
            dinh_dang_tien(item["don_gia"]),
            dinh_dang_tien(item["thanh_tien"]),
        ])
    
    tong_tien = float(phieu["so_tien"])

    data.append([
        "",
        "",
        "TỔNG CỘNG",
        "" if tong_kg == 0 else f"{tong_kg:,.0f}",
        f"{tong_thanh:,}",
        "" if tong_m3 == 0 else f"{tong_m3:.3f}",
        "",
        dinh_dang_tien(tong_tien),
    ])

    table = Table(
        data,
        repeatRows=1,
        colWidths=[
            35,     # STT
            120,    # Tên gỗ
            90,     # Quy cách
            60,     # Kg
            55,     # Thanh
            60,     # m3
            90,     # Đơn giá
            100,    # Thành tiền
        ],
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

        ("ALIGN", (0, 1), (0, -2), "CENTER"),
        ("ALIGN", (1, 1), (2, -2), "LEFT"),
        ("ALIGN", (3, 1), (7, -2), "RIGHT"),

        ("ALIGN", (0, -1), (2, -1), "CENTER"),
        ("ALIGN", (3, -1), (7, -1), "RIGHT"),

        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#E8E8E8")),

    ]))

    elements.append(table)

    elements.append(Spacer(1, 15))
    # ==========================
    # LỊCH SỬ THANH TOÁN
    # ==========================

    elements.append(
        Paragraph(
            "LỊCH SỬ THANH TOÁN",
            heading2,
        )
    )
    elements.append(Spacer(1, 8)) 

    data_tt = [[
        "STT",
        "Ngày",
        "Nội dung",
        "Số tiền",
    ]]

    tong_da_thanh_toan = 0

    for i, item in enumerate(ds_tt, start=1):

        so_tien = float(item.get("so_tien") or 0)
        tong_da_thanh_toan += so_tien

        ngay = item.get("ngay")

        if ngay:
            try:
                ngay = ngay.strftime("%d/%m/%Y")
            except:
                ngay = str(ngay)
        else:
            ngay = ""

        noi_dung = item.get("ghi_chu") or f"Thanh toán lần {i}"

        data_tt.append([
            i,
            ngay,
            noi_dung,
            dinh_dang_tien(so_tien),
        ])

    table_tt = Table(
        data_tt,
        repeatRows=1,
        colWidths=[
            35,
            90,
            360,
            100,
        ],
    )

    table_tt.setStyle(TableStyle([

        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#4F81BD")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),

        ("GRID", (0,0), (-1,-1), 0.4, colors.grey),

        ("FONTNAME", (0,0), (-1,0), "DejaVu-Bold"),
        ("FONTNAME", (0,1), (-1,-1), "DejaVu"),

        ("FONTSIZE", (0,0), (-1,-1), 8),

        ("BOTTOMPADDING", (0,0), (-1,0), 6),
        ("TOPPADDING", (0,0), (-1,0), 6),

        ("ALIGN", (0,0), (-1,0), "CENTER"),
        ("ALIGN", (0,1), (1,-1), "CENTER"),
        ("ALIGN", (2,1), (2,-1), "LEFT"),
        ("ALIGN", (3,1), (3,-1), "RIGHT"),

        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),

    ]))

    elements.append(table_tt)

    elements.append(Spacer(1, 15))
    # ==========================
    # TỔNG KẾT
    # ==========================

    tong_con_lai = float(phieu.get("con_lai") or 0)

    data_tong = [
        [
            "Tổng tiền phiếu",
            dinh_dang_tien(tong_tien),
        ],
        [
            "Đã thanh toán",
            dinh_dang_tien(tong_da_thanh_toan),
        ],
        [
            "Còn lại",
            dinh_dang_tien(tong_con_lai),
        ],
    ]

    table_tong = Table(
        data_tong,
        colWidths=[
            180,
            130,
        ],
    )

    table_tong.setStyle(TableStyle([

        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),

        ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#F5F5F5")),

        ("FONTNAME", (0,0), (-1,-1), "DejaVu-Bold"),

        ("FONTSIZE", (0,0), (-1,-1), 9),

        ("ALIGN", (0,0), (0,-1), "LEFT"),
        ("ALIGN", (1,0), (1,-1), "RIGHT"),

        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 6),

    ]))

    table_tong.hAlign = "CENTER"
    elements.append(table_tong)

    elements.append(Spacer(1, 25))
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