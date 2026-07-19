import streamlit as st
import pandas as pd
import io
from openpyxl import Workbook

from database.db import (
    lay_so_phieu_xuat_moi,
    lay_ds_khach_hang,
    lay_kho_da_phan_loai,
    luu_phieu_xuat,
    lay_ds_phieu_xuat,
    lay_chi_tiet_phieu_xuat,
    lay_phieu_xuat
)
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
import os

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

pdfmetrics.registerFont(
    TTFont("DejaVu", os.path.join(BASE_DIR, "fonts", "DejaVuSans.ttf"))
)

pdfmetrics.registerFont(
    TTFont("DejaVu-Bold", os.path.join(BASE_DIR, "fonts", "DejaVuSans-Bold.ttf"))
)

registerFontFamily(
    "DejaVu",
    normal="DejaVu",
    bold="DejaVu-Bold",
    italic="DejaVu",
    boldItalic="DejaVu-Bold",
)



def tao_excel_xuat(phieu, df):

    wb = Workbook()
    ws = wb.active
    ws.title = "Phiếu xuất"

    ws.append(["PHIẾU XUẤT HÀNG"])
    ws.append([])

    ws.append(["Số phiếu", phieu["so_phieu"]])
    ws.append(["Ngày", phieu["ngay"].strftime("%d/%m/%Y")])
    ws.append(["Khách hàng", phieu["khach_hang"]])
    ws.append(["Ghi chú", phieu["ghi_chu"] or ""])
    ws.append([])

    ws.append(list(df.columns))

    for row in df.values.tolist():
        ws.append(row)

    buffer = io.BytesIO()

    wb.save(buffer)

    buffer.seek(0)

    return buffer

def tao_pdf(phieu, rows):
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    styles["Title"].fontName = "DejaVu-Bold"
    styles["Title"].leading = 28

    styles["Normal"].fontName = "DejaVu"
    styles["Normal"].leading = 18

    from reportlab.lib.enums import TA_CENTER

    center = styles["Heading2"]
    center.fontName = "DejaVu-Bold"
    center.alignment = TA_CENTER

    elements = []

    # ======= PHẦN ĐẦU =======

    elements.append(Paragraph("CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM", center))
    elements.append(Paragraph("Độc lập - Tự do - Hạnh phúc", center))
    elements.append(Paragraph("--------------------------------", center))

    elements.append(Spacer(1, 15))

    

    elements.append(Spacer(1, 10))

    elements.append(
        Paragraph("PHIẾU XUẤT HÀNG", styles["Title"])
    )
    elements.append(
        Paragraph(
            "<b>CÔNG TY:</b> ........................................................",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 15))

    elements.append(
        Paragraph(f"Số phiếu: {phieu['so_phieu']}", styles["Normal"])
    )

    elements.append(
        Paragraph(
            f"Ngày: {phieu['ngay'].strftime('%d/%m/%Y')}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"Khách hàng: <b>{phieu['khach_hang']}</b>",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 10))

    elements.append(
        Paragraph(
            (
                f"Hôm nay, ngày {phieu['ngay'].strftime('%d')} "
                f"tháng {phieu['ngay'].strftime('%m')} "
                f"năm {phieu['ngay'].strftime('%Y')}."
            ),
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 15))

    # ======= BẢNG =======

    data = [[
        "STT",
        "Loại gỗ",
        "Phân loại",
        "Dày",
        "Rộng",
        "Dài",
        "Kg",
        "Thanh",
        "M³",
        "Đơn giá bán",
        "Thành tiền"
    ]]

    tong_kg = 0
    tong_m3 = 0
    tong_tien = 0

    

    cell_style = ParagraphStyle(
        "Cell",
        parent=styles["Normal"],
        fontName="DejaVu",
        fontSize=8,
        leading=10,
        alignment=1,
    )
    tong_style = ParagraphStyle(
        "TongStyle",
        parent=cell_style,
        fontName="DejaVu-Bold",
        fontSize=8,      # nhỏ hơn (có thể thử 7.5 nếu muốn)
        leading=10,
        alignment=1,
    )
    for r in rows:


        data.append([
            Paragraph(str(r["STT"]), cell_style),
            Paragraph(str(r["Loại gỗ"]), cell_style),
            Paragraph(str(r["Phân loại"]), cell_style),
            Paragraph(str(r["Dày"]), cell_style),
            Paragraph(str(r["Rộng"]), cell_style),
            Paragraph(str(r["Dài"]), cell_style),
            Paragraph(str(r["Kg"]), cell_style),
            Paragraph(str(r["Thanh"]), cell_style),
            Paragraph(str(r["M³"]), cell_style),
            Paragraph(str(r["Đơn giá"]), cell_style),
            Paragraph(str(r["Thành tiền"]).replace(" đ", ""), cell_style),
        ])

        # Tổng Kg
        if r["Kg"] != "":
            tong_kg += float(str(r["Kg"]).replace(",", ""))

        # Tổng M3
        if r["M³"] != "":
            tong_m3 += float(r["M³"])

        # Tổng tiền
        tong_tien += float(
            str(r["Thành tiền"])
            .replace(" đ", "")
            .replace(",", "")
        )

    # ======= DÒNG TỔNG =======

    data.append([
        Paragraph("", tong_style),
        Paragraph("TỔNG CỘNG", tong_style),
        Paragraph("", tong_style),
        Paragraph("", tong_style),
        Paragraph("", tong_style),
        Paragraph("", tong_style),
        Paragraph(f"{tong_kg:,.0f}" if tong_kg else "", tong_style),
        Paragraph("", tong_style),
        Paragraph(f"{tong_m3:.3f}" if tong_m3 else "", tong_style),
        Paragraph("", tong_style),
        Paragraph(f"{tong_tien:,.0f}", tong_style),
    ])

    table = Table(
        data,
        colWidths=[
            25,   # STT
            65,   # Loại gỗ
            55,   # Phân loại
            30,   # Dày
            35,   # Rộng
            40,   # Dài
            45,   # Kg
            45,   # Thanh
            45,   # M3
            60,   # Đơn giá
            80    # Thành tiền
        ]
    )

    table.setStyle(TableStyle([

        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),

        ("BACKGROUND", (0, -1), (-1, -1), colors.lightgrey),

        ("GRID", (0, 0), (-1, -1), 1, colors.black),

        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

        ("FONTNAME", (0, 0), (-1, 0), "DejaVu-Bold"),
        ("FONTNAME", (0, 1), (-1, -2), "DejaVu"),
        ("FONTNAME", (0, -1), (-1, -1), "DejaVu-Bold"),

        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),

    ]))

    elements.append(table)

    elements.append(Spacer(1, 70))

    # ======= CHỮ KÝ =======

    ky = Table([
        [
            "Người lập phiếu",
            "Khách hàng"
        ],
        [
            "(Ký, ghi rõ họ tên)",
            "(Ký, ghi rõ họ tên)"
        ]
    ], colWidths=[260, 260])

    ky.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, -1), "DejaVu"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))

    elements.append(ky)

    doc.build(elements)

    buffer.seek(0)

    return buffer


def show():

    if st.session_state.get("xem_phieu_xuat") is not None:

        phieu = lay_phieu_xuat(
            st.session_state.xem_phieu_xuat
        )

        ct = lay_chi_tiet_phieu_xuat(
            st.session_state.xem_phieu_xuat
        )

        st.header("🧾 PHIẾU XUẤT HÀNG")

        if st.button("⬅ Quay lại"):

            del st.session_state["xem_phieu_xuat"]
            st.session_state.tab_xuat = "lich_su"
            st.rerun()

        st.write(f"**Số phiếu:** {phieu['so_phieu']}")
        st.write(f"**Ngày:** {phieu['ngay'].strftime('%d/%m/%Y')}")
        st.write(f"**Khách hàng:** {phieu['khach_hang']}")
        st.write(f"**Ghi chú:** {phieu['ghi_chu'] or ''}")

        df = pd.DataFrame(ct)
        rows = []

        for i, dong in enumerate(ct, start=1):

            if dong["kieu_tinh"] == "M3":

                ten_go = dong["ten"]

                kg = ""
                thanh = int(dong["so_thanh"])
                m3 = f'{dong["m3"]:.3f}'

            else:

                ten_go = dong["ten"]

                kg = f'{dong["kg"]:,.0f}'
                thanh = ""
                m3 = ""

            rows.append({

                "STT": i,

                "Loại gỗ": ten_go,

                "Phân loại": dong["phan_loai"],

                "Dày": "" if dong["day"] is None else int(dong["day"]),

                "Rộng": "" if dong["rong"] is None else int(dong["rong"]),

                "Dài": "" if dong["dai"] is None else int(dong["dai"]),

                "Kg": kg,

                "Thanh": thanh,

                "M³": m3,

                "Đơn giá": f'{dong["don_gia_ban"]:,.0f}',

                "Thành tiền": f'{dong["thanh_tien"]:,.0f} đ'

            })

        df = df.rename(columns={
            "id": "Mã",
            "ten": "Tên gỗ",
            "kieu_tinh": "Kiểu tính",
            "day": "Dày",
            "rong": "Rộng",
            "dai": "Dài",
            "phan_loai": "Phân loại",
            "so_thanh": "Số thanh",
            "kg": "Kg",
            "m3": "m³",
            "don_gia_ban": "Đơn giá",
            "thanh_tien": "Thành tiền"
        })

        tong = {
            "Mã": "",
            "Tên gỗ": "TỔNG CỘNG",
            "Kiểu tính": "",
            "Dày": "",
            "Rộng": "",
            "Dài": "",
            "Phân loại": "",
            "Số thanh": df["Số thanh"].fillna(0).sum(),
            "Kg": df["Kg"].fillna(0).sum(),
            "m³": df["m³"].fillna(0).sum(),
            "Đơn giá": "",
            "Thành tiền": df["Thành tiền"].fillna(0).sum()
        }

        df.loc[len(df)] = tong
        df = df.fillna("")

        excel = tao_excel_xuat(
            phieu,
            df
        )
        pdf = tao_pdf(
            phieu,
            rows
        )

        c1, c2 = st.columns([1,1])

        with c1:

            st.download_button(

                "📊 Xuất Excel",

                data=excel,

                file_name=f'Phieu_Xuat_{phieu["so_phieu"]}.xlsx',

                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",

                use_container_width=True

            )

        with c2:

            st.download_button(

                "📄 Xuất PDF",

                data=pdf,

                file_name=f'Phieu_Xuat_{phieu["so_phieu"]}.pdf',

                mime="application/pdf",

                use_container_width=True

            )

        st.divider()

        st.dataframe(

            df,

            use_container_width=True,

            hide_index=True

        )

        return

    st.header("🚚 Xuất hàng")

    if "ds_xuat" not in st.session_state:
        st.session_state.ds_xuat = []

    if "tab_xuat" not in st.session_state:
        st.session_state.tab_xuat = "lap"

    if st.session_state.tab_xuat == "lap":
        type_lap = "primary"
        type_ls = "secondary"
    else:
        type_lap = "secondary"
        type_ls = "primary"

    c1, c2 = st.columns(2)

    with c1:
        if st.button(
            "📝 Lập phiếu",
            use_container_width=True,
            type=type_lap
        ):
            st.session_state.tab_xuat = "lap"
            st.rerun()

    with c2:
        if st.button(
            "📜 Lịch sử",
            use_container_width=True,
            type=type_ls
        ):
            st.session_state.tab_xuat = "lich_su"
            st.rerun()

    if st.session_state.tab_xuat == "lap":

        col1, col2 = st.columns(2)

        with col1:
            so_phieu = lay_so_phieu_xuat_moi()

            st.text_input(
                "Số phiếu",
                value=so_phieu,
                disabled=True
            )

        with col2:
            ngay = st.date_input(
                "Ngày xuất"
            )

        ds_kh = lay_ds_khach_hang()

        kh = st.selectbox(
            "Khách hàng",
            ds_kh,
            format_func=lambda x: x["ten"]
        )
        # Khóa danh sách xuất theo khách hàng
        if "kh_xuat" not in st.session_state:
            st.session_state.kh_xuat = kh["id"]

        if st.session_state.kh_xuat != kh["id"]:

            st.session_state.kh_xuat = kh["id"]
            st.session_state.ds_xuat = []

            st.rerun()

        ghi_chu = st.text_area("Ghi chú")
        st.divider()

        st.subheader("📦 Kho đã phân loại")

        ds_kho = lay_kho_da_phan_loai(
            khach_hang_id=kh["id"]
        )

        if ds_kho:

            df = pd.DataFrame(ds_kho)

            df["Nguồn"] = df["loai_nhap"].map({
                "TUOI": "🌲 Gia công",
                "KHO": "📦 Hàng mua"
            })

            df = df.rename(columns={
                "ten": "Loại gỗ",
                "phan_loai": "Phân loại",
                "day": "Dày",
                "rong": "Rộng",
                "dai": "Dài",
                "thanh": "Thanh",
                "m3": "m³",
                "kg": "Kg"
            })
            df = df.fillna("")

            st.dataframe(
                df[
                    [
                        "Nguồn",
                        "Loại gỗ",
                        "Phân loại",
                        "Dày",
                        "Rộng",
                        "Dài",
                        "Thanh",
                        "m³",
                        "Kg"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )
            lo = st.selectbox(
                "Lô gỗ",
                ds_kho,
                key="lo_xuat",
                format_func=lambda x: (
                    f'{"📦 Hàng mua" if x["loai_nhap"]=="KHO" else "🌲 Gia công"} | '
                    f'{x["ten"]} | {x["phan_loai"]} | '
                    f'{int(x["day"])}x{int(x["rong"])}x{int(x["dai"])}'
                    if x["kieu_tinh"] == "M3"
                    else
                    f'{"📦 Hàng mua" if x["loai_nhap"]=="KHO" else "🌲 Gia công"} | '
                    f'{x["ten"]} | {x["phan_loai"]} | Kg'
                )
            )
            # Số lượng đã chọn xuất của lô này
            thanh_da_chon = 0
            m3_da_chon = 0.0

            for item in st.session_state.ds_xuat:

                if item["kho_phan_loai_id"] == lo["kho_phan_loai_id"]:

                    thanh_da_chon = item["so_thanh"]
                    m3_da_chon = item["so_luong"]
                    break

            if lo["kieu_tinh"] == "M3":
                thanh_con = lo["thanh"] - thanh_da_chon
                m3_con = lo["m3"] - m3_da_chon
            else:
                thanh_con = 0
                m3_con = 0

            col1, col2 = st.columns(2)

            with col1:
                if lo["kieu_tinh"] == "M3":
                    st.metric(
                        "Thanh còn",
                        int(thanh_con)
                    )                                 
                else:
                    st.metric(
                        "Kg còn",
                        round(lo["kg"], 3)
                    )

            with col2:
                if lo["kieu_tinh"] == "M3":
                    st.metric(
                        "m³ còn",
                        round(m3_con, 3)
                    )

            st.divider()
            co_the_them = True

            if lo["kieu_tinh"] == "M3":

                if thanh_con <= 0:

                    st.warning("Lô này đã hết.")
                    co_the_them = False

                else:

                    so_thanh = st.number_input(
                        "Số thanh xuất",
                        min_value=1,
                        max_value=int(thanh_con),
                        value=1,
                        step=1
                    )

                    so_luong = (
                        float(lo["m3"])
                        * so_thanh
                        / float(lo["thanh"])
                    )

            else:

                if lo["kg"] <= 0:

                    st.warning("Lô này đã hết.")
                    co_the_them = False

                else:

                    so_thanh = 0

                    so_luong = st.number_input(
                        "Kg xuất",
                        min_value=0.0,
                        max_value=float(lo["kg"]),
                        value=0.0,
                        step=1.0
                    )
            
            if lo["loai_nhap"] == "KHO":

                don_gia_ban = st.number_input(
                    "Đơn giá bán",
                    min_value=0.0,
                    value=float(lo["don_gia"]),
                    step=1000.0
                )

            else:

                don_gia_ban = 0

            if co_the_them and st.button(
                "➕ Thêm vào phiếu",
                use_container_width=True
            ):

                da_co = False

                for item in st.session_state.ds_xuat:

                    if item["kho_phan_loai_id"] != lo["kho_phan_loai_id"]:
                        continue

                    if lo["kieu_tinh"] == "M3":

                        thanh_moi = item["so_thanh"] + so_thanh

                        if thanh_moi > lo["thanh"]:
                            st.error("Xuất vượt số thanh còn.")
                            st.stop()

                        item["so_thanh"] = thanh_moi

                        item["so_luong"] = (
                            float(lo["m3"])
                            * item["so_thanh"]
                            / float(lo["thanh"])
                        )

                    else:

                        kg_moi = item["so_luong"] + so_luong

                        if kg_moi > lo["kg"]:
                            st.error("Xuất vượt số kg còn.")
                            st.stop()

                        item["so_luong"] = kg_moi
    
                    if lo["loai_nhap"] == "KHO":
                        item["don_gia_ban"] = don_gia_ban
                        item["thanh_tien"] = item["so_luong"] * don_gia_ban

                    da_co = True
                    break
                
                if not da_co:

                    item = {

                        "kho_phan_loai_id": lo["kho_phan_loai_id"],

                        "ten": lo["ten"],

                        "phan_loai": lo["phan_loai"],

                        "day": lo["day"],

                        "rong": lo["rong"],

                        "dai": lo["dai"],

                        "so_thanh": so_thanh,

                        "so_luong": so_luong,

                        "loai_nhap": lo["loai_nhap"]

                    }

                    if lo["loai_nhap"] == "KHO":

                        item["don_gia_ban"] = don_gia_ban

                        if lo["kieu_tinh"] == "M3":
                            item["thanh_tien"] = so_luong * don_gia_ban
                        else:
                            item["thanh_tien"] = so_luong * don_gia_ban
                    st.session_state.ds_xuat.append(item)

                st.rerun()
        
            st.divider()

            st.subheader("📋 Các mặt hàng sẽ xuất")

            if st.session_state.ds_xuat:

                for i, item in enumerate(st.session_state.ds_xuat):

                    c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(
                        [3,2,1,1,1,1.2,1.2,0.8]
                    )

                    with c1:
                        st.write(item["ten"])

                    with c2:
                        st.write(item["phan_loai"])

                    with c3:
                        if item["day"] is not None:
                            st.write(
                                f'{int(item["day"])}x{int(item["rong"])}x{int(item["dai"])}'
                            )
                        else:
                            st.write("Kg")

                    with c4:
                        if item["day"] is not None:
                            st.write(f'{item["so_thanh"]} thanh')
                        else:
                            st.write("-")

                    with c5:
                        if item["day"] is not None:
                            st.write(f'{item["so_luong"]:.3f} m³')
                        else:
                            st.write(f'{item["so_luong"]:.3f} kg')

                    with c6:

                        if item["loai_nhap"] == "KHO":
                            st.write(f'{item["don_gia_ban"]:,.0f}')
                        else:
                            st.write("-")

                    with c7:

                        if item["loai_nhap"] == "KHO":
                            st.write(f'{item["thanh_tien"]:,.0f}')
                        else:
                            st.write("-")

                    with c8:

                        if st.button(
                            "❌",
                            key=f"xoa_{i}",
                            use_container_width=True
                        ):

                            st.session_state.ds_xuat.pop(i)

                            st.rerun()

            else:

                st.info("Chưa có mặt hàng nào.")

            if st.session_state.ds_xuat:

                col1, col2 = st.columns(2)

                with col1:

                    if st.button(
                        "💾 Lưu phiếu xuất",
                        use_container_width=True,
                        type="primary"
                    ):

                        try:

                            luu_phieu_xuat(

                                so_phieu=so_phieu,

                                ngay=ngay,

                                khach_hang_id=kh["id"],

                                ghi_chu=ghi_chu,

                                ds_hang=st.session_state.ds_xuat

                            )

                            st.session_state.ds_xuat = []
                            # Xóa lựa chọn lô
                            if "lo_xuat" in st.session_state:
                                del st.session_state["lo_xuat"]

                            st.success("Đã lưu phiếu xuất.")

                            st.rerun()

                        except Exception as e:

                            st.error(str(e))

                with col2:

                    if st.button(
                        "🗑 Xóa danh sách",
                        use_container_width=True
                    ):

                        st.session_state.ds_xuat = []

                        st.rerun()
        

        else:

            st.info("Khách hàng chưa có hàng trong kho đã phân loại.")

    elif st.session_state.tab_xuat == "lich_su":

        ds = lay_ds_phieu_xuat()

        if len(ds) == 0:

            st.info("Chưa có phiếu xuất.")

        else:

            c1, c2, c3, c4, c5, c6, c7 = st.columns(
                [1, 2, 4, 2, 1, 1, 1]
            )

            c1.write("Số phiếu")
            c2.write("Ngày xuất")
            c3.write("Khách hàng")
            c4.write("Mặt hàng")
            c5.write("👁")
            c6.write("✏️")
            c7.write("🗑")

            st.divider()

            for row in ds:

                c1, c2, c3, c4, c5, c6, c7 = st.columns(
                    [1, 2, 4, 2, 1, 1, 1]
                )

                c1.write(row["so_phieu"])
                c2.write(row["ngay"].strftime("%d/%m/%Y"))
                c3.write(row["khach_hang"])
                c4.write(row["so_mat_hang"])

                if c5.button(
                    "👁",
                    key=f"xem_xuat_{row['id']}"
                ):
                    st.session_state.xem_phieu_xuat = row["id"]
                    st.session_state.tab_xuat = "lich_su"
                    st.rerun()

                if c6.button(
                    "✏️",
                    key=f"sua_xuat_{row['id']}"
                ):
                    st.session_state.sua_phieu_xuat = row["id"]
                    st.info("Chức năng sửa sẽ làm tiếp.")

                if c7.button(
                    "🗑",
                    key=f"xoa_xuat_{row['id']}"
                ):
                    st.warning("Chưa làm chức năng xóa.")
            