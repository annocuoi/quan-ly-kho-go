import streamlit as st
import pandas as pd
import io
import os
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Spacer
from reportlab.lib.styles import ParagraphStyle


from database.db import (
    lay_ds_loai_go,
    lay_ds_khach_hang,
    lay_so_phieu_moi,
    them_phieu_nhap,
    them_chi_tiet_phieu_nhap,
    lay_ds_phieu_nhap,
    lay_chi_tiet_phieu_nhap,
    lay_phieu_nhap,
    sua_phieu_nhap,
    xoa_chi_tiet_phieu,
    xoa_phieu_nhap,
    them_cong_no,
    sua_cong_no,
    xoa_cong_no,
    lay_ds_phan_loai,
    them_chi_tiet_nhap_hang_kho,
    lay_chi_tiet_nhap_hang_kho
)

if "xac_nhan_xoa" not in st.session_state:
    st.session_state.xac_nhan_xoa = None


@st.dialog("🗑 Xóa phiếu")
def dialog_xoa(id):
    st.warning("Bạn có chắc muốn xóa phiếu này không?")
    c1, c2 = st.columns(2)

    if c1.button("🗑 Xóa", width="stretch", type="primary"):

        xoa_chi_tiet_phieu(id)

        xoa_cong_no(id)

        xoa_phieu_nhap(id)

        st.session_state.xac_nhan_xoa = None

        st.success("Đã xóa phiếu.")

        st.rerun()

    if c2.button("Hủy", width="stretch"):
        st.session_state.xac_nhan_xoa = None
        st.rerun()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

pdfmetrics.registerFont(
    TTFont("DejaVu", os.path.join(BASE_DIR, "fonts", "DejaVuSans.ttf"))
)

pdfmetrics.registerFont(
    TTFont("DejaVu-Bold", os.path.join(BASE_DIR, "fonts", "DejaVuSans-Bold.ttf"))
)
from reportlab.pdfbase.pdfmetrics import registerFontFamily

registerFontFamily(
    "DejaVu",
    normal="DejaVu",
    bold="DejaVu-Bold",
    italic="DejaVu",
    boldItalic="DejaVu-Bold",
)
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
        Paragraph("PHIẾU NHẬP HÀNG", styles["Title"])
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
        "Dày",
        "Rộng",
        "Dài",
        "Kg",
        "Thanh",
        "M³",
        "Đơn giá",
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
        fontSize=8,      
        leading=10,
        alignment=1,
    )
    for r in rows:


        data.append([
            Paragraph(str(r["STT"]), cell_style),
            Paragraph(str(r["Loại gỗ"]), cell_style),
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
            70,   # Loại gỗ
            33,   # Dày
            37,   # Rộng
            40,   # Dài
            45,   # Kg
            45,   # Thanh
            50,   # M³
            60,   # Đơn giá
            90    # Thành tiền
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
            "Bên Giao",
            "Bên Nhận"
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
    if "tab_chuyen_doi" in st.session_state:
        del st.session_state["tab_chuyen_doi"]

    if "phieu_nhap_tam" not in st.session_state:
        st.session_state.phieu_nhap_tam = []

    if "phieu_nhap_kho_tam" not in st.session_state:
        st.session_state.phieu_nhap_kho_tam = []

    if "dong_sua_kho" not in st.session_state:
        st.session_state.dong_sua_kho = None

    if "version_selectbox_kho" not in st.session_state:
        st.session_state.version_selectbox_kho = 0

    if "kh_mac_dinh_kho" not in st.session_state:
        st.session_state.kh_mac_dinh_kho = ""

    if "dong_sua" not in st.session_state:
        st.session_state.dong_sua = None

    if "id_phieu_dang_sua" not in st.session_state:
        st.session_state.id_phieu_dang_sua = None

    if "so_phieu_hien_tai" not in st.session_state:
        st.session_state.so_phieu_hien_tai = ""

    if "version_selectbox" not in st.session_state:
        st.session_state.version_selectbox = 0
    
    if "xem_phieu" not in st.session_state:
        st.session_state.xem_phieu = None
    
    if "tab_hien_tai" not in st.session_state:
        st.session_state.tab_hien_tai = "📥 Nhập hàng"

    if "tab_nhap_hang" not in st.session_state:
        st.session_state.tab_nhap_hang = "🌲 Nhập hàng tươi"

    # Lấy sẵn danh mục gỗ từ đầu để đối chiếu
    ds_go = lay_ds_loai_go()

    # XEM CHI TIẾT PHIẾU
    if st.session_state.xem_phieu is not None:
        phieu = lay_phieu_nhap(st.session_state.xem_phieu)
        ct = lay_chi_tiet_phieu_nhap(st.session_state.xem_phieu)

        rows = []
        for i, dong in enumerate(ct, start=1):
            if dong["kieu_tinh"] == "M3":
                day = int(dong["day"]) if dong.get("day") is not None else 0
                rong = int(dong["rong"]) if dong.get("rong") is not None else 0
                dai = int(dong["dai"]) if dong.get("dai") is not None else 0
                kg = ""
                thanh = int(dong["so_thanh"]) if dong.get("so_thanh") is not None else 0
                m3 = f"{dong['so_luong']:.3f}"
                ten_go = f'{dong["ten"]} - {day}×{rong}×{dai}'
            else:
                day = ""
                rong = ""
                dai = ""
                kg = f"{dong['so_luong']:,.0f}"
                thanh = ""
                m3 = ""
                ten_go = f'{dong["ten"]} (KG)'

            rows.append({
                "STT": i,
                "Loại gỗ": ten_go,
                "Dày": day,
                "Rộng": rong,
                "Dài": dai,
                "Kg": kg,
                "Thanh": thanh,
                "M³": m3,
                "Đơn giá": f"{dong['don_gia']:,.0f}",
                "Thành tiền": f"{dong['thanh_tien']:,.0f} đ"
            })
        df = pd.DataFrame(rows)
        tong_kg = 0
        tong_thanh = 0
        tong_m3 = 0

        for d in ct:

            if d["kieu_tinh"] == "M3":
                tong_thanh += d["so_thanh"] if d.get("so_thanh") is not None else 0
                tong_m3 += d["so_luong"] if d.get("so_luong") is not None else 0
            else:
                tong_kg += d["so_luong"] if d.get("so_luong") is not None else 0

        df.loc[len(df)] = {
            "STT": "",
            "Loại gỗ": "TỔNG CỘNG",
            "Dày": "",
            "Rộng": "",
            "Dài": "",
            "Kg": f"{tong_kg:,.0f}" if tong_kg else "",
            "Thanh": f"{tong_thanh:,.0f}" if tong_thanh else "",
            "M³": f"{tong_m3:.3f}" if tong_m3 else "",
            "Đơn giá": "",
            "Thành tiền": f"{phieu['tong_tien']:,.0f} đ"
        }
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("⬅ Quay lại", use_container_width=True):
                st.session_state.xem_phieu = None
                st.session_state.tab_hien_tai = "📋 Lịch sử phiếu"
        with c2:

            df_excel = pd.DataFrame([{
                "STT": r["STT"],
                "Loại gỗ": r["Loại gỗ"],
                "Dày": r["Dày"],
                "Rộng": r["Rộng"],
                "Dài": r["Dài"],
                "Kg": d["so_luong"] if d["kieu_tinh"] != "M3" else "",
                "Thanh": r["Thanh"],
                "M³": d["so_luong"] if d["kieu_tinh"] == "M3" else "",
                "Đơn giá": d["don_gia"],
                "Thành tiền": d["thanh_tien"]
            } for r, d in zip(rows, ct)])

            df_excel.loc[len(df_excel)] = {
                "STT": "",
                "Loại gỗ": "TỔNG CỘNG",
                "Dày": "",
                "Rộng": "",
                "Dài": "",
                "Kg": tong_kg if tong_kg else "",
                "Thanh": tong_thanh if tong_thanh else "",
                "M³": round(tong_m3, 3) if tong_m3 else "",
                "Đơn giá": "",
                "Thành tiền": phieu["tong_tien"]
            }

            buffer = io.BytesIO()

            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df_excel.to_excel(
                    writer,
                    index=False,
                    sheet_name="ChiTietNhap"
                )

            buffer.seek(0)

            st.download_button(
                label="📊 Xuất Excel",
                data=buffer,
                file_name=f"Phieu_Nhap_{phieu['so_phieu']}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                type="primary"
            )

        with c3:
            pdf_buffer = tao_pdf(phieu, rows)

            st.download_button(
                label="📄 Xuất PDF",
                data=pdf_buffer,
                file_name=f"Phieu_Nhap_{phieu['so_phieu']}.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="secondary"
            )

        st.header("🧾 PHIẾU NHẬP HÀNG")
        c1, c2 = st.columns(2)
        with c1:
            st.write(f"**Số phiếu:** {phieu['so_phieu']}")
            st.write(f"**Ngày:** {phieu['ngay'].strftime('%d/%m/%Y') if hasattr(phieu['ngay'], 'strftime') else phieu['ngay']}")
        with c2:
            st.write(f"**Khách hàng:** {phieu['khach_hang']}")
            st.write(f"**Tổng tiền:** {phieu['tong_tien']:,.0f} đ")

        st.divider()
        def in_dam_tong(row):
            if row["Loại gỗ"] == "TỔNG CỘNG":
                return ["font-weight: bold"] * len(row)
            return [""] * len(row)

        st.table(
            df.style.apply(in_dam_tong, axis=1)
        )
        return

    # --- ĐIỀU HƯỚNG TAB CHÍNH ---
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("📥 Nhập hàng", type="primary" if st.session_state.tab_hien_tai == "📥 Nhập hàng" else "secondary", use_container_width=True):
            st.session_state.tab_hien_tai = "📥 Nhập hàng"
            st.rerun()
    with col2:
        if st.button("📋 Lịch sử phiếu", type="primary" if st.session_state.tab_hien_tai == "📋 Lịch sử phiếu" else "secondary", use_container_width=True):
            st.session_state.tab_hien_tai = "📋 Lịch sử phiếu"
            st.rerun()

    lua_chon = st.session_state.tab_hien_tai
    if lua_chon == "📥 Nhập hàng":

        index_radio_mac_dinh = 1 if st.session_state.tab_nhap_hang == "🪵 Nhập hàng khô" else 0

        lua_chon_nhap = st.radio(
            "",
            ["🌲 Nhập hàng tươi", "🪵 Nhập hàng khô"],
            horizontal=True,
            index=index_radio_mac_dinh,
            key="loai_hang_radio"
        )
        st.session_state.tab_nhap_hang = lua_chon_nhap

        if lua_chon_nhap == "🌲 Nhập hàng tươi":
            if st.session_state.id_phieu_dang_sua is None:
                so_phieu = str(lay_so_phieu_moi())
            else:
                st.info(f"✏️ Đang sửa phiếu số: {st.session_state.so_phieu_hien_tai}")
                so_phieu = st.session_state.so_phieu_hien_tai
                if st.button("❌ Thoát chế độ sửa phiếu (Nhập mới)", key="thoat_sua_tuoi"):
                    st.session_state.id_phieu_dang_sua = None
                    st.session_state.phieu_nhap_tam = []
                    st.session_state.dong_sua = None
                    st.session_state.version_selectbox += 1
                    st.rerun()

            c1, c2, c3 = st.columns(3)
            with c1: st.text_input("Số phiếu", value=so_phieu, disabled=True)
            with c2: ngay = st.date_input("Ngày")
            with c3:
                ds_kh = lay_ds_khach_hang()
                if not ds_kh: st.warning("Chưa có khách hàng."); st.stop()
                index_kh_mac_dinh = 0
                if "kh_mac_dinh" in st.session_state and st.session_state.id_phieu_dang_sua is not None:
                    ten_kh_list = [x["ten"] for x in ds_kh]
                    if st.session_state.kh_mac_dinh in ten_kh_list: index_kh_mac_dinh = ten_kh_list.index(st.session_state.kh_mac_dinh)
                ten_kh = st.selectbox("Khách hàng", [x["ten"] for x in ds_kh], index=index_kh_mac_dinh)
                khach_hang = next(x for x in ds_kh if x["ten"] == ten_kh)

            st.divider()
            if not ds_go: st.warning("Chưa có loại gỗ."); st.stop()
            ds_ten_go = ["-- Chọn loại gỗ --"]

            for x in ds_go:
                if x["kieu_tinh"] == "M3":
                    ds_ten_go.append(f'{x["ten"]} - {int(x["day"])}×{int(x["rong"])}×{int(x["dai"])}')
                else:
                    ds_ten_go.append(f'{x["ten"]} (KG)')

            index_mac_dinh = 0
            df_sua = None

            if st.session_state.dong_sua is not None:
                df_sua = st.session_state.phieu_nhap_tam[st.session_state.dong_sua]
                if df_sua["kieu_tinh"] == "M3":
                    ten_go_sua = f'{df_sua["ten"]} - {int(df_sua["day"])}×{int(df_sua["rong"])}×{int(df_sua["dai"])}'
                else:
                    ten_go_sua = f'{df_sua["ten"]} (KG)'
                if ten_go_sua in ds_ten_go:
                    index_mac_dinh = ds_ten_go.index(ten_go_sua)

            ten_go = st.selectbox(
                "Loại gỗ",
                ds_ten_go,
                index=index_mac_dinh,
                key=f"go_select_tuoi_{st.session_state.version_selectbox}"
            )
            
            if ten_go != "-- Chọn loại gỗ --":
                loai_go = next(
                    x
                    for x in ds_go
                    if (
                        f'{x["ten"]} - {int(x["day"])}×{int(x["rong"])}×{int(x["dai"])}'
                        if x["kieu_tinh"] == "M3"
                        else f'{x["ten"]} (KG)'
                    ) == ten_go
                )
                gia_tri_don_gia = float(df_sua["don_gia"]) if df_sua else 0.0
                gia_tri_thanh = int(df_sua["so_thanh"]) if df_sua else 1
                gia_tri_kg = float(df_sua["so_luong"]) if (df_sua and df_sua["kieu_tinh"] != "M3") else 0.0

                don_gia = st.number_input("Đơn giá", min_value=0.0, step=1000.0, format="%.0f", value=gia_tri_don_gia)

                if loai_go["kieu_tinh"] == "M3":
                    st.info(f'Quy cách: {int(loai_go["day"])} × {int(loai_go["rong"])} × {int(loai_go["dai"])}')
                    so_thanh = st.number_input("Số thanh", min_value=1, step=1, value=gia_tri_thanh)
                    so_luong = round((loai_go["day"] * loai_go["rong"] * loai_go["dai"] * so_thanh) / 1000000000, 4)
                else:
                    so_luong = st.number_input("Khối lượng (Kg)", min_value=0.0, step=1.0, value=gia_tri_kg)
                    so_thanh = 0

                if st.session_state.dong_sua is None:
                    if st.button("➕ Thêm vào phiếu", key="them_phieu_tuoi", use_container_width=True):
                        st.session_state.phieu_nhap_tam.append({
                            "loai_go_id": loai_go["id"],
                            "ten": loai_go["ten"],
                            "day": loai_go["day"],
                            "rong": loai_go["rong"],
                            "dai": loai_go["dai"],
                            "kieu_tinh": loai_go["kieu_tinh"],
                            "so_thanh": so_thanh,
                            "so_luong": so_luong,
                            "don_gia": don_gia,
                            "thanh_tien": so_luong * don_gia
                        })
                        st.session_state.version_selectbox += 1
                        st.rerun()
                else:
                    col_cap_nhat, col_huy = st.columns(2)
                    with col_cap_nhat:
                        if st.button("💾 Cập nhật dòng", key="cap_nhat_dong_tuoi", type="primary", use_container_width=True):
                            st.session_state.phieu_nhap_tam[st.session_state.dong_sua] = {
                                "loai_go_id": loai_go["id"],
                                "ten": loai_go["ten"],
                                "day": loai_go["day"],
                                "rong": loai_go["rong"],
                                "dai": loai_go["dai"],
                                "kieu_tinh": loai_go["kieu_tinh"],
                                "so_thanh": so_thanh,
                                "so_luong": so_luong,
                                "don_gia": don_gia,
                                "thanh_tien": so_luong * don_gia
                            }
                            st.session_state.dong_sua = None
                            st.session_state.version_selectbox += 1
                            st.rerun()
                    with col_huy:
                        if st.button("❌ Hủy sửa dòng", key="huy_sua_dong_tuoi", use_container_width=True):
                            st.session_state.dong_sua = None
                            st.session_state.version_selectbox += 1
                            st.rerun()

                st.divider()

            tong_tien = 0
            if not st.session_state.phieu_nhap_tam:
                st.info("Chưa có gỗ trong danh sách.")
            else:
                c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([4, 4, 2, 2, 2, 3, 1, 1])
                c1.write("**Loại gỗ**")
                c2.write("**Quy cách**")
                c3.write("**Thanh**")
                c4.write("**SL**")
                c5.write("**Đơn giá**")
                c6.write("**Thành tiền**")
                c7.write("✏️")
                c8.write("🗑")
                st.divider()

                for i, dong in enumerate(st.session_state.phieu_nhap_tam):
                    c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([4, 4, 2, 2, 2, 3, 1, 1])
                    prefix = "👉 " if st.session_state.dong_sua == i else ""

                    if dong["kieu_tinh"] == "M3":
                        ten_go = dong["ten"]
                        quy_cach = f'{int(dong["day"]) if dong.get("day") is not None else 0} × {int(dong["rong"]) if dong.get("rong") is not None else 0} × {int(dong["dai"]) if dong.get("dai") is not None else 0}'
                        thanh = str(dong["so_thanh"])
                        so_luong = f'{dong["so_luong"]:.4f} m³'
                    else:
                        ten_go = dong["ten"]
                        quy_cach = "KG"
                        thanh = "-"
                        so_luong = f'{dong["so_luong"]:,.0f} Kg'

                    c1.write(prefix + ten_go)
                    c2.write(quy_cach)
                    c3.write(thanh)
                    c4.write(so_luong)
                    c5.write(f'{dong["don_gia"]:,.0f}')
                    c6.write(f'{dong["thanh_tien"]:,.0f} đ')

                    tong_tien += dong["thanh_tien"]

                    if c7.button("✏️", key=f"sua_dong_{i}"):
                        st.session_state.dong_sua = i
                        st.session_state.version_selectbox += 1
                        st.rerun()

                    if c8.button("🗑", key=f"xoa_{i}"):
                        if st.session_state.dong_sua == i:
                            st.session_state.dong_sua = None
                            st.session_state.version_selectbox += 1
                        st.session_state.phieu_nhap_tam.pop(i)
                        st.rerun()

                st.divider()
                st.metric("Tổng tiền", f"{tong_tien:,.0f}")
                st.divider()
                ten_nut_luu = "💾 Lưu phiếu mới" if st.session_state.id_phieu_dang_sua is None else "💾 Cập nhật phiếu cũ"

                if st.button(ten_nut_luu, key="luu_phieu_tuoi", type="primary", width="stretch"):
                    if not st.session_state.phieu_nhap_tam:
                        st.warning("Chưa có dữ liệu.")
                    else:
                        if st.session_state.id_phieu_dang_sua is None:
                            id_phieu = them_phieu_nhap(so_phieu, str(ngay), khach_hang["id"], tong_tien)
                            them_cong_no(
                                khach_hang_id=khach_hang["id"],
                                ngay=str(ngay),
                                loai="CONG_SAY",
                                so_tien=tong_tien,
                                phieu_nhap_id=id_phieu,
                                ghi_chu=f"Phiếu nhập {so_phieu}"
                            )
                        else:
                            id_phieu = st.session_state.id_phieu_dang_sua
                            sua_phieu_nhap(id_phieu, str(ngay), khach_hang["id"], tong_tien)
                            sua_cong_no(
                                phieu_nhap_id=id_phieu,
                                khach_hang_id=khach_hang["id"],
                                ngay=str(ngay),
                                loai="CONG_SAY",
                                so_tien=tong_tien,
                                ghi_chu=f"Phiếu nhập {so_phieu}"
                            )
                            xoa_chi_tiet_phieu(id_phieu)

                        for dong in st.session_state.phieu_nhap_tam:
                            them_chi_tiet_phieu_nhap(
                                id_phieu,
                                dong["loai_go_id"],
                                dong["so_thanh"],
                                dong["so_luong"],
                                dong["don_gia"],
                                dong["thanh_tien"]
                            )

                        st.session_state.phieu_nhap_tam.clear()
                        st.session_state.dong_sua = None
                        st.session_state.id_phieu_dang_sua = None
                        st.session_state.version_selectbox += 1
                        st.success("Đã ghi nhận thay đổi thành công!")
                        st.rerun()

        if lua_chon_nhap == "🪵 Nhập hàng khô":
            if st.session_state.id_phieu_dang_sua is None:
                so_phieu = str(lay_so_phieu_moi())
            else:
                st.info(f"✏️ Đang sửa phiếu số: {st.session_state.so_phieu_hien_tai}")
                so_phieu = st.session_state.so_phieu_hien_tai
                if st.button("❌ Thoát chế độ sửa phiếu (Nhập mới)", key="thoat_sua_kho"):
                    st.session_state.id_phieu_dang_sua = None
                    st.session_state.phieu_nhap_kho_tam.clear()
                    st.session_state.dong_sua_kho = None
                    st.session_state.tab_hien_tai = "📥 Nhập hàng"
                    st.rerun()

            c1, c2, c3 = st.columns(3)
            with c1: st.text_input("Số phiếu", value=so_phieu, disabled=True, key="so_phieu_kho")
            with c2: ngay = st.date_input("Ngày", key="ngay_kho")
            with c3:
                ds_kh = lay_ds_khach_hang()
                if not ds_kh: st.warning("Chưa có khách hàng."); st.stop()
                index_kh_mac_dinh = 0
                if "kh_mac_dinh" in st.session_state and st.session_state.id_phieu_dang_sua is not None:
                    ten_kh_list = [x["ten"] for x in ds_kh]
                    if st.session_state.kh_mac_dinh in ten_kh_list: index_kh_mac_dinh = ten_kh_list.index(st.session_state.kh_mac_dinh)
                ten_kh = st.selectbox("Khách hàng", [x["ten"] for x in ds_kh], index=index_kh_mac_dinh, key="khach_hang_kho")
                khach_hang = next(x for x in ds_kh if x["ten"] == ten_kh)

            st.divider()
            if not ds_go: st.warning("Chưa có loại gỗ."); st.stop()
            ds_ten_go = ["-- Chọn loại gỗ --"]

            for x in ds_go:
                if x["kieu_tinh"] == "M3":
                    ds_ten_go.append(f'{x["ten"]} - {int(x["day"])}×{int(x["rong"])}×{int(x["dai"])}')
                else:
                    ds_ten_go.append(f'{x["ten"]} (KG)')

            index_mac_dinh = 0
            df_sua = None

            if st.session_state.dong_sua_kho is not None:
                df_sua = st.session_state.phieu_nhap_kho_tam[st.session_state.dong_sua_kho]
                
                for vi_tri, x in enumerate(ds_go):
                    if x.get("id") == df_sua.get("loai_go_id"):
                        index_mac_dinh = vi_tri + 1
                        break
            ten_go = st.selectbox(
                "Loại gỗ",
                ds_ten_go,
                index=index_mac_dinh,
                key=f"go_select_kho_{st.session_state.version_selectbox_kho}"
            )

            if ten_go != "-- Chọn loại gỗ --" or df_sua is not None:
                loai_go = None
                
                if ten_go != "-- Chọn loại gỗ --":
                    loai_go = next(
                        (x for x in ds_go if (f'{x["ten"]} - {int(x["day"])}×{int(x["rong"])}×{int(x["dai"])}' if x["kieu_tinh"] == "M3" else f'{x["ten"]} (KG)') == ten_go),
                        None
                    )
                
                if loai_go is None and df_sua is not None:
                    loai_go = next((x for x in ds_go if x["id"] == df_sua["loai_go_id"]), None)
                
                if loai_go is None and df_sua is not None:
                    loai_go = {
                        "id": df_sua["loai_go_id"],
                        "ten": df_sua["ten"],
                        "day": df_sua.get("day") if df_sua.get("day") is not None else 0,
                        "rong": df_sua.get("rong") if df_sua.get("rong") is not None else 0,
                        "dai": df_sua.get("dai") if df_sua.get("dai") is not None else 0,
                        "kieu_tinh": df_sua.get("kieu_tinh", "M3")
                    }

                ds_phan_loai = lay_ds_phan_loai()
                index_pl = 0
                if df_sua:
                    for i, x in enumerate(ds_phan_loai):
                        if x["id"] == df_sua["phan_loai_go_id"]:
                            index_pl = i
                            break

                phan_loai = st.selectbox(
                    "Phân loại",
                    ds_phan_loai,
                    index=index_pl,
                    format_func=lambda x: x["ten"],
                    key=f"phan_loai_kho_{st.session_state.version_selectbox_kho}"
                )

                gia_tri_don_gia = float(df_sua["don_gia"]) if df_sua else 0.0
                gia_tri_thanh = int(df_sua["so_thanh"]) if df_sua else 1
                gia_tri_kg = float(df_sua["so_luong"]) if (df_sua and df_sua["kieu_tinh"] != "M3") else 0.0

                don_gia = st.number_input(
                    "Đơn giá",
                    min_value=0.0,
                    step=1000.0,
                    format="%.0f",
                    value=gia_tri_don_gia,
                    key=f"don_gia_kho_{st.session_state.version_selectbox_kho}"
                )

                if loai_go["kieu_tinh"] == "M3":
                    g_day = float(loai_go.get("day") if loai_go.get("day") is not None else 0)
                    g_rong = float(loai_go.get("rong") if loai_go.get("rong") is not None else 0)
                    g_dai = float(loai_go.get("dai") if loai_go.get("dai") is not None else 0)

                    st.info(f'Quy cách: {int(g_day)} × {int(g_rong)} × {int(g_dai)}')
                    so_thanh = st.number_input(
                        "Số thanh",
                        min_value=1,
                        step=1,
                        value=gia_tri_thanh,
                        key=f"so_thanh_kho_{st.session_state.version_selectbox_kho}"
                    )
                    so_luong = round((g_day * g_rong * g_dai * so_thanh) / 1000000000, 4)
                else:
                    so_luong = st.number_input(
                        "Khối lượng (Kg)",
                        min_value=0.0,
                        step=1.0,
                        value=gia_tri_kg,
                        key=f"kg_kho_{st.session_state.version_selectbox_kho}"
                    )
                    so_thanh = 0

                if st.session_state.dong_sua_kho is None:
                    if st.button("➕ Thêm vào phiếu", key="them_phieu_kho", width="stretch"):
                        st.session_state.phieu_nhap_kho_tam.append({
                            "loai_go_id": loai_go["id"],
                            "ten": loai_go["ten"],
                            "phan_loai_go_id": phan_loai["id"],
                            "phan_loai": phan_loai["ten"],
                            "day": loai_go.get("day", 0),    
                            "rong": loai_go.get("rong", 0),  
                            "dai": loai_go.get("dai", 0),    
                            "kieu_tinh": loai_go["kieu_tinh"],
                            "so_thanh": so_thanh,
                            "so_luong": so_luong,
                            "don_gia": don_gia,
                            "thanh_tien": so_luong * don_gia
                        })
                        st.session_state.version_selectbox_kho += 1
                        st.rerun()
                else:
                    col_cap_nhat, col_huy = st.columns(2)
                    with col_cap_nhat:
                        if st.button("💾 Cập nhật dòng", key="cap_nhat_dong_kho", width="stretch", type="primary"):
                            st.session_state.phieu_nhap_kho_tam[st.session_state.dong_sua_kho] = {
                                "loai_go_id": loai_go["id"],
                                "ten": loai_go["ten"],
                                "phan_loai_go_id": phan_loai["id"],
                                "phan_loai": phan_loai["ten"],
                                "day": loai_go.get("day", 0),    
                                "rong": loai_go.get("rong", 0),  
                                "dai": loai_go.get("dai", 0),    
                                "kieu_tinh": loai_go["kieu_tinh"],
                                "so_thanh": so_thanh,
                                "so_luong": so_luong,
                                "don_gia": don_gia,
                                "thanh_tien": so_luong * don_gia
                            }
                            st.session_state.dong_sua_kho = None
                            st.session_state.version_selectbox_kho += 1
                            st.rerun()
                    with col_huy:
                        if st.button("❌ Hủy sửa dòng", key="huy_sua_dong_kho", width="stretch"):
                            st.session_state.dong_sua_kho = None
                            st.session_state.version_selectbox_kho += 1
                            st.rerun()

                st.divider()

            tong_tien = 0

            if not st.session_state.phieu_nhap_kho_tam:
                st.info("Chưa có gỗ trong danh sách.")
            else:
                c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns([4, 2, 4, 2, 2, 2, 3, 1, 1])
                c1.write("**Loại gỗ**")
                c2.write("**Phân loại**")
                c3.write("**Quy cách**")
                c4.write("**Thanh**")
                c5.write("**SL**")
                c6.write("**Đơn giá**")
                c7.write("**Thành tiền**")
                c8.write("✏️")
                c9.write("🗑")
                st.divider()

                for i, dong in enumerate(st.session_state.phieu_nhap_kho_tam):
                    c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns([4, 2, 4, 2, 2, 2, 3, 1, 1])
                    prefix = "👉 " if st.session_state.dong_sua_kho == i else ""

                    if dong["kieu_tinh"] == "M3":
                        ten_go = dong["ten"]
                        
                        # Tự đối chiếu danh mục gốc để lấy lại kích thước thực tế nếu database trả về 0 hoặc khuyết thiếu
                        chuan = next((x for x in ds_go if x["id"] == dong["loai_go_id"]), None)
                        d_day = int(dong.get("day") if dong.get("day") else (chuan["day"] if chuan else 0))
                        d_rong = int(dong.get("rong") if dong.get("rong") else (chuan["rong"] if chuan else 0))
                        d_dai = int(dong.get("dai") if dong.get("dai") else (chuan["dai"] if chuan else 0))
                        
                        quy_cach = f'{d_day} × {d_rong} × {d_dai}'
                        thanh = str(dong["so_thanh"])
                        so_luong = f'{dong["so_luong"]:.4f} m³'
                    else:
                        ten_go = dong["ten"]
                        quy_cach = "KG"
                        thanh = "-"
                        so_luong = f'{dong["so_luong"]:,.0f} Kg'

                    c1.write(prefix + ten_go)
                    c2.write(dong["phan_loai"])
                    c3.write(quy_cach)
                    c4.write(thanh)
                    c5.write(so_luong)
                    c6.write(f'{dong["don_gia"]:,.0f}')
                    c7.write(f'{dong["thanh_tien"]:,.0f} đ')

                    tong_tien += dong["thanh_tien"]

                    if c8.button("✏️", key=f"sua_kho_{i}"):
                        st.session_state.dong_sua_kho = i
                        st.session_state.version_selectbox_kho += 1
                        st.rerun()

                    if c9.button("🗑", key=f"xoa_kho_{i}"):
                        if st.session_state.dong_sua_kho == i:
                            st.session_state.dong_sua_kho = None
                            st.session_state.version_selectbox_kho += 1
                        st.session_state.phieu_nhap_kho_tam.pop(i)
                        st.rerun()

                st.divider()
                st.metric("Tổng tiền", f"{tong_tien:,.0f}")
                st.divider()
                ten_nut_luu = "💾 Lưu phiếu mới" if st.session_state.id_phieu_dang_sua is None else "💾 Cập nhật phiếu cũ"

                if st.button(ten_nut_luu, key="luu_phieu_kho", type="primary", width="stretch"):
                    if not st.session_state.phieu_nhap_kho_tam:
                        st.warning("Chưa có dữ liệu.")
                    else:
                        if st.session_state.id_phieu_dang_sua is None:
                            id_phieu = them_phieu_nhap(so_phieu, str(ngay), khach_hang["id"], tong_tien, "KHO")
                            them_cong_no(
                                khach_hang_id=khach_hang["id"],
                                ngay=str(ngay),
                                loai="MUA_GO",
                                so_tien=tong_tien,
                                phieu_nhap_id=id_phieu,
                                ghi_chu=f"Phiếu nhập {so_phieu}"
                            )
                        else:
                            id_phieu = st.session_state.id_phieu_dang_sua
                            sua_phieu_nhap(id_phieu, str(ngay), khach_hang["id"], tong_tien)
                            sua_cong_no(
                                phieu_nhap_id=id_phieu,
                                khach_hang_id=khach_hang["id"],
                                ngay=str(ngay),
                                loai="MUA_GO",
                                so_tien=tong_tien,
                                ghi_chu=f"Phiếu nhập {so_phieu}"
                            )
                            xoa_chi_tiet_phieu(id_phieu)

                        for dong in st.session_state.phieu_nhap_kho_tam:
                            them_chi_tiet_nhap_hang_kho(
                                id_phieu,
                                dong["loai_go_id"],
                                dong["phan_loai_go_id"],
                                dong["day"],
                                dong["rong"],
                                dong["dai"],
                                dong["so_thanh"],
                                dong["so_luong"],
                                dong["don_gia"],
                                dong["thanh_tien"]
                            )

                        st.session_state.phieu_nhap_kho_tam.clear()
                        st.session_state.dong_sua_kho = None
                        st.session_state.id_phieu_dang_sua = None
                        st.session_state.version_selectbox_kho += 1
                        st.success("Đã ghi nhận thay đổi thành công!")
                        st.rerun()

    if lua_chon == "📋 Lịch sử phiếu":
        st.header("📋 Lịch sử phiếu nhập")
        loc_loai = st.radio("Loại phiếu", ["Tất cả", "🌲 Hàng tươi", "🪵 Hàng khô"], horizontal=True)

        if loc_loai == "🌲 Hàng tươi":
            ds = lay_ds_phieu_nhap("TUOI")
        elif loc_loai == "🪵 Hàng khô":
            ds = lay_ds_phieu_nhap("KHO")
        else:
            ds = lay_ds_phieu_nhap()

        if len(ds) == 0:
            st.info("Chưa có phiếu.")
        else:
            c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([1, 2, 2, 4, 2, 1, 1, 1])
            c1.write("Số")
            c2.write("Ngày")
            c3.write("Loại")
            c4.write("Khách hàng")
            c5.write("Tổng tiền")
            c6.write("👁")
            c7.write("✏️")
            c8.write("🗑")
            st.divider()

            for row in ds:
                c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([1, 2, 2, 4, 2, 1, 1, 1])
                loai = "🌲 Tươi" if row["loai_nhap"] == "TUOI" else "🪵 Khô"

                c1.write(row["so_phieu"])
                c2.write(str(row["ngay"]))
                c3.write(loai)
                c4.write(row["khach_hang"])
                c5.write(f'{row["tong_tien"]:,.0f}')

                if c6.button("👁", key=f"xem_{row['id']}"):
                    st.session_state.xem_phieu = row["id"]
                    st.rerun()

                if c7.button("✏️", key=f"sua_{row['id']}"):
                    st.session_state.id_phieu_dang_sua = row["id"]
                    st.session_state.so_phieu_hien_tai = row["so_phieu"]
                    st.session_state.kh_mac_dinh = row["khach_hang"]

                    if row["loai_nhap"] == "KHO":
                        st.session_state.tab_nhap_hang = "🪵 Nhập hàng khô"
                        ct_go_cu = lay_chi_tiet_nhap_hang_kho(row["id"])
                        st.session_state.phieu_nhap_kho_tam = []

                        for dong in ct_go_cu:
                            # Khôi phục kích thước dựa trên cấu hình gốc để đẩy vào session_state tránh mang giá trị 0
                            chuan = next((x for x in ds_go if x["id"] == dong["loai_go_id"]), None)
                            d_day = dong["day"] if dong.get("day") else (chuan["day"] if chuan else 0)
                            d_rong = dong["rong"] if dong.get("rong") else (chuan["rong"] if chuan else 0)
                            d_dai = dong["dai"] if dong.get("dai") else (chuan["dai"] if chuan else 0)

                            st.session_state.phieu_nhap_kho_tam.append({
                                "loai_go_id": dong["loai_go_id"],
                                "ten": dong["ten"],
                                "phan_loai_go_id": dong["phan_loai_go_id"],
                                "phan_loai": dong["ten_phan_loai"],
                                "day": d_day,
                                "rong": d_rong,
                                "dai": d_dai,
                                "kieu_tinh": dong["kieu_tinh"],
                                "so_thanh": dong["so_thanh"],
                                "so_luong": dong["so_luong"],
                                "don_gia": dong["don_gia"],
                                "thanh_tien": dong["thanh_tien"]
                            })
                    else:
                        st.session_state.tab_nhap_hang = "🌲 Nhập hàng tươi"
                        ct_go_cu = lay_chi_tiet_phieu_nhap(row["id"])
                        st.session_state.phieu_nhap_tam = []

                        for dong in ct_go_cu:
                            st.session_state.phieu_nhap_tam.append({
                                "loai_go_id": dong["loai_go_id"],
                                "ten": dong["ten"],
                                "day": dong["day"],
                                "rong": dong["rong"],
                                "dai": dong["dai"],
                                "kieu_tinh": dong["kieu_tinh"],
                                "so_thanh": dong["so_thanh"],
                                "so_luong": dong["so_luong"],
                                "don_gia": dong["don_gia"],
                                "thanh_tien": dong["thanh_tien"]
                            })
                    st.session_state.tab_hien_tai = "📥 Nhập hàng"

                    if row["loai_nhap"] == "TUOI":
                        if st.session_state.phieu_nhap_tam:
                            st.session_state.dong_sua = 0
                    else:
                        if st.session_state.phieu_nhap_kho_tam:
                            st.session_state.dong_sua_kho = 0

                    st.session_state.version_selectbox += 1
                    st.session_state.version_selectbox_kho += 1
                    st.rerun()

                if c8.button("🗑", key=f"xoa_{row['id']}"):
                    dialog_xoa(row["id"])