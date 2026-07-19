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
    lay_phieu_xuat,
    sua_phieu_xuat,
    xoa_chi_tiet_phieu_xuat,
    xoa_phieu_xuat,
    hoan_kho_phieu_xuat,
    xoa_cong_no
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

if "xac_nhan_xoa_xuat" not in st.session_state:
    st.session_state.xac_nhan_xoa_xuat = None

# Khởi tạo biến lưu trữ dòng đang sửa trên Form giống bên Nhập hàng
if "dong_sua_xuat" not in st.session_state:
    st.session_state.dong_sua_xuat = None

@st.dialog("🗑 Xóa phiếu xuất")
def dialog_xoa_xuat(id):
    st.warning("Bạn có chắc muốn xóa phiếu xuất này không?")
    c1, c2 = st.columns(2)
    if c1.button("🗑 Xóa", use_container_width=True, type="primary"):
        hoan_kho_phieu_xuat(id)
        xoa_cong_no(phieu_xuat_id=id)
        xoa_chi_tiet_phieu_xuat(id)
        xoa_phieu_xuat(id)
        st.session_state.xac_nhan_xoa_xuat = None
        st.success("Đã xóa phiếu xuất.")
        st.rerun()
    if c2.button("Hủy", use_container_width=True):
        st.session_state.xac_nhan_xoa_xuat = None
        st.rerun()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pdfmetrics.registerFont(TTFont("DejaVu", os.path.join(BASE_DIR, "fonts", "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", os.path.join(BASE_DIR, "fonts", "DejaVuSans-Bold.ttf")))
registerFontFamily("DejaVu", normal="DejaVu", bold="DejaVu-Bold", italic="DejaVu", boldItalic="DejaVu-Bold")

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

    center = styles["Heading2"]
    center.fontName = "DejaVu-Bold"
    center.alignment = TA_CENTER

    elements = []
    elements.append(Paragraph("CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM", center))
    elements.append(Paragraph("Độc lập - Tự do - Hạnh phúc", center))
    elements.append(Paragraph("--------------------------------", center))
    elements.append(Spacer(1, 15))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("PHIẾU XUẤT HÀNG", styles["Title"]))
    elements.append(Paragraph("<b>CÔNG TY:</b> ........................................................", styles["Normal"]))
    elements.append(Spacer(1, 15))
    elements.append(Paragraph(f"Số phiếu: {phieu['so_phieu']}", styles["Normal"]))
    elements.append(Paragraph(f"Ngày: {phieu['ngay'].strftime('%d/%m/%Y')}", styles["Normal"]))
    elements.append(Paragraph(f"Khách hàng: <b>{phieu['khach_hang']}</b>", styles["Normal"]))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"Hôm nay, ngày {phieu['ngay'].strftime('%d')} tháng {phieu['ngay'].strftime('%m')} năm {phieu['ngay'].strftime('%Y')}.", styles["Normal"]))
    elements.append(Spacer(1, 15))

    data = [["STT", "Loại gỗ", "Phân loại", "Dày", "Rộng", "Dài", "Kg", "Thanh", "M³", "Đơn giá bán", "Thành tiền"]]
    tong_kg, tong_m3, tong_tien = 0, 0, 0

    cell_style = ParagraphStyle("Cell", parent=styles["Normal"], fontName="DejaVu", fontSize=8, leading=10, alignment=1)
    tong_style = ParagraphStyle("TongStyle", parent=cell_style, fontName="DejaVu-Bold", fontSize=8, leading=10, alignment=1)

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
        if r["Kg"] != "": tong_kg += float(str(r["Kg"]).replace(",", ""))
        if r["M³"] != "": tong_m3 += float(r["M³"])
        tong_tien += float(str(r["Thành tiền"]).replace(" đ", "").replace(",", ""))

    data.append([
        Paragraph("", tong_style), Paragraph("TỔNG CỘNG", tong_style), Paragraph("", tong_style),
        Paragraph("", tong_style), Paragraph("", tong_style), Paragraph("", tong_style),
        Paragraph(f"{tong_kg:,.0f}" if tong_kg else "", tong_style), Paragraph("", tong_style),
        Paragraph(f"{tong_m3:.3f}" if tong_m3 else "", tong_style), Paragraph("", tong_style),
        Paragraph(f"{tong_tien:,.0f}", tong_style),
    ])

    table = Table(data, colWidths=[25, 65, 55, 30, 35, 40, 45, 45, 45, 60, 80])
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

    ky = Table([["Người lập phiếu", "Khách hàng"], ["(Ký, ghi rõ họ tên)", "(Ký, ghi rõ họ tên)"]], colWidths=[260, 260])
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
        phieu = lay_phieu_xuat(st.session_state.xem_phieu_xuat)
        ct = lay_chi_tiet_phieu_xuat(st.session_state.xem_phieu_xuat)

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
                kg, thanh, m3 = "", int(dong["so_thanh"]), f'{dong["m3"]:.3f}'
            else:
                ten_go = dong["ten"]
                kg, thanh, m3 = f'{dong["kg"]:,.0f}', "", ""

            rows.append({
                "STT": i, "Loại gỗ": ten_go, "Phân loại": dong["phan_loai"],
                "Dày": "" if dong["day"] is None else int(dong["day"]),
                "Rộng": "" if dong["rong"] is None else int(dong["rong"]),
                "Dài": "" if dong["dai"] is None else int(dong["dai"]),
                "Kg": kg, "Thanh": thanh, "M³": m3,
                "Đơn giá": f'{dong["don_gia_ban"]:,.0f}',
                "Thành tiền": f'{dong["thanh_tien"]:,.0f} đ'
            })

        df = df.rename(columns={
            "id": "Mã", "ten": "Tên gỗ", "kieu_tinh": "Kiểu tính", "day": "Dày", "rong": "Rộng", "dai": "Dài",
            "phan_loai": "Phân loại", "so_thanh": "Số thanh", "kg": "Kg", "m3": "m³", "don_gia_ban": "Đơn giá", "thanh_tien": "Thành tiền"
        })

        tong = {
            "Mã": "", "Tên gỗ": "TỔNG CỘNG", "Kiểu tính": "", "Dày": "", "Rộng": "", "Dài": "", "Phân loại": "",
            "Số thanh": df["Số thanh"].fillna(0).sum(), "Kg": df["Kg"].fillna(0).sum(), "m³": df["m³"].fillna(0).sum(),
            "Đơn giá": "", "Thành tiền": df["Thành tiền"].fillna(0).sum()
        }
        df.loc[len(df)] = tong
        df = df.fillna("")

        excel = tao_excel_xuat(phieu, df)
        pdf = tao_pdf(phieu, rows)

        c1, c2 = st.columns([1,1])
        with c1:
            st.download_button("📊 Xuất Excel", data=excel, file_name=f'Phieu_Xuat_{phieu["so_phieu"]}.xlsx', mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        with c2:
            st.download_button("📄 Xuất PDF", data=pdf, file_name=f'Phieu_Xuat_{phieu["so_phieu"]}.pdf', mime="application/pdf", use_container_width=True)

        st.divider()
        st.dataframe(df, use_container_width=True, hide_index=True)
        return

    st.header("🚚 Xuất hàng")

    if "ds_xuat" not in st.session_state: st.session_state.ds_xuat = []
    if "tab_xuat" not in st.session_state: st.session_state.tab_xuat = "lap"

    type_lap = "primary" if st.session_state.tab_xuat == "lap" else "secondary"
    type_ls = "secondary" if st.session_state.tab_xuat == "lap" else "primary"

    c1, c2 = st.columns(2)
    with c1:
        if st.button("📝 Lập phiếu", use_container_width=True, type=type_lap):
            st.session_state.tab_xuat = "lap"
            st.rerun()
    with c2:
        if st.button("📜 Lịch sử phiếu", use_container_width=True, type=type_ls):
            st.session_state.tab_xuat = "lich_su"
            st.rerun()

    if st.session_state.tab_xuat == "lap":
        # KHAI BÁO BIẾN MẶC ĐỊNH Ở ĐÂY ĐỂ ĐẬP TAN LỖI UNBOUNDLOCALERROR
        phieu_sua = None 

        # --- CHUẨN HÓA LOGIC LOAD DỮ LIỆU SỬA PHIẾU CŨ ĐỒNG BỘ GIAO DIỆN ---
        if st.session_state.get("sua_phieu_xuat") is not None:
            phieu_sua = lay_phieu_xuat(st.session_state["sua_phieu_xuat"])
            st.info(f"✏️ Đang sửa phiếu số: {phieu_sua['so_phieu']}")
            
            if st.button("❌ Thoát chế độ sửa phiếu (Xuất mới)", type="secondary"):
                del st.session_state["sua_phieu_xuat"]
                st.session_state.ds_xuat = []
                st.session_state.dong_sua_xuat = None
                st.rerun()

            key_da_load = f"loaded_xuat_{st.session_state.sua_phieu_xuat}"
            if not st.session_state.get(key_da_load, False):
                ct_sua = lay_chi_tiet_phieu_xuat(st.session_state["sua_phieu_xuat"])
                st.session_state.ds_xuat = [] 
                for dong in ct_sua:
                    kieu_tinh = "KG" if (dong.get("kg") is not None and dong["kg"] > 0) else "M3"
                    item = {
                        "kho_phan_loai_id": dong["kho_phan_loai_id"],
                        "ten": dong["ten"],
                        "phan_loai": dong["phan_loai"],
                        "day": dong["day"],
                        "rong": dong["rong"],
                        "dai": dong["dai"],
                        "so_thanh": 0 if dong["so_thanh"] is None else int(dong["so_thanh"]),
                        "so_luong": float(dong["kg"]) if kieu_tinh == "KG" else float(dong["m3"]),
                        "loai_nhap": dong["loai_nhap"],
                        "kieu_tinh": kieu_tinh
                    }

                    if dong["loai_nhap"] == "KHO":
                        item["don_gia_ban"] = float(dong["don_gia_ban"]) if dong["don_gia_ban"] is not None else 0.0
                        item["thanh_tien"] = float(dong["thanh_tien"]) if dong["thanh_tien"] is not None else 0.0

                    st.session_state.ds_xuat.append(item)
                
                st.session_state[key_da_load] = True

        col1, col2 = st.columns(2)
        with col1:
            so_phieu = phieu_sua["so_phieu"] if phieu_sua else lay_so_phieu_xuat_moi()
            st.text_input("Số phiếu", value=so_phieu, disabled=True)
        with col2:
            ngay_mac_dinh = phieu_sua["ngay"].date() if phieu_sua else None
            ngay = st.date_input("Ngày xuất", value=ngay_mac_dinh)

        ds_kh = lay_ds_khach_hang()
        index_kh = next((i for i, x in enumerate(ds_kh) if x["id"] == phieu_sua["khach_hang_id"]), 0) if phieu_sua else 0
        kh = st.selectbox("Khách hàng", ds_kh, index=index_kh, format_func=lambda x: x["ten"])

        if "kh_xuat" not in st.session_state: st.session_state.kh_xuat = kh["id"]
        if st.session_state.get("sua_phieu_xuat") is None and st.session_state.kh_xuat != kh["id"]:
            st.session_state.kh_xuat = kh["id"]
            st.session_state.ds_xuat = []
            st.rerun()

        ghi_chu = st.text_area("Ghi chú", value=(phieu_sua["ghi_chu"] if phieu_sua else ""))
        st.divider()

        ds_kho = lay_kho_da_phan_loai(khach_hang_id=kh["id"])

        if ds_kho:
            df_sua = None
            index_mac_dinh_lo = 0
            
            if st.session_state.dong_sua_xuat is not None:
                if st.session_state.dong_sua_xuat < len(st.session_state.ds_xuat):
                    df_sua = st.session_state.ds_xuat[st.session_state.dong_sua_xuat]
                    for vi_tri, x in enumerate(ds_kho):
                        if x["kho_phan_loai_id"] == df_sua["kho_phan_loai_id"]:
                            index_mac_dinh_lo = vi_tri
                            break

            lo = st.selectbox(
                "Lô gỗ",
                ds_kho,
                index=index_mac_dinh_lo,
                key="lo_xuat",
                format_func=lambda x: (
                    f'{"📦 Hàng mua" if x["loai_nhap"]=="KHO" else "🌲 Gia công"} | {x["ten"]} | {x["phan_loai"]} | {int(x["day"])}x{int(x["rong"])}x{int(x["dai"])}'
                    if x["kieu_tinh"] == "M3" else
                    f'{"📦 Hàng mua" if x["loai_nhap"]=="KHO" else "🌲 Gia công"} | {x["ten"]} | {x["phan_loai"]} | Kg'
                )
            )

            thanh_da_chon = 0
            m3_da_chon = 0.0
            for idx, item in enumerate(st.session_state.ds_xuat):
                if st.session_state.dong_sua_xuat == idx:
                    continue
                if item["kho_phan_loai_id"] == lo["kho_phan_loai_id"]:
                    thanh_da_chon += item["so_thanh"]
                    m3_da_chon += item["so_luong"]

            kieu_tinh_hien_tai = lo["kieu_tinh"]
            thanh_con = lo["thanh"] - thanh_da_chon if kieu_tinh_hien_tai == "M3" else 0
            m3_con = lo["m3"] - m3_da_chon if kieu_tinh_hien_tai == "M3" else 0
            kg_con = lo["kg"] - m3_da_chon if kieu_tinh_hien_tai != "M3" else 0

            col1, col2 = st.columns(2)
            with col1:
                if kieu_tinh_hien_tai == "M3":
                    st.metric("Thanh còn lại", int(thanh_con))
                else:
                    st.metric("Kg còn lại", round(kg_con, 3))
            with col2:
                if kieu_tinh_hien_tai == "M3":
                    st.metric("m³ còn lại", round(m3_con, 3))

            st.divider()

            val_so_thanh = 1
            val_so_luong = 0.0
            val_don_gia = float(lo["don_gia"]) if lo["loai_nhap"] == "KHO" else 0.0

            if df_sua is not None:
                val_so_thanh = int(df_sua["so_thanh"])
                val_so_luong = float(df_sua["so_luong"])
                if "don_gia_ban" in df_sua:
                    val_don_gia = float(df_sua["don_gia_ban"])

            co_the_thao_tac = True
            if kieu_tinh_hien_tai == "M3":
                if thanh_con <= 0 and df_sua is None:
                    st.warning("Lô gỗ này trong kho đã được chọn hết!")
                    co_the_thao_tac = False
                else:
                    max_thanh = int(thanh_con) + (int(df_sua["so_thanh"]) if df_sua else 0)
                    so_thanh = st.number_input("Số thanh xuất", min_value=1, max_value=max_thanh, value=min(val_so_thanh, max_thanh), step=1)
                    so_luong = float(lo["m3"]) * so_thanh / float(lo["thanh"])
            else:
                if kg_con <= 0 and df_sua is None:
                    st.warning("Lô gỗ tính KG này trong kho đã hết!")
                    co_the_thao_tac = False
                else:
                    so_thanh = 0
                    max_kg = float(kg_con) + (float(df_sua["so_luong"]) if df_sua else 0.0)
                    so_luong = st.number_input("Kg xuất", min_value=0.0, max_value=max_kg, value=min(val_so_luong, max_kg), step=1.0)
            
            if lo["loai_nhap"] == "KHO":
                don_gia_ban = st.number_input("Đơn giá bán", min_value=0.0, value=val_don_gia, step=1000.0)
            else:
                don_gia_ban = 0.0

            if co_the_thao_tac:
                if st.session_state.dong_sua_xuat is not None:
                    c_nut1, c_nut2 = st.columns(2)
                    with c_nut1:
                        if st.button("💾 Cập nhật dòng", use_container_width=True, type="primary"):
                            df_sua["kho_phan_loai_id"] = lo["kho_phan_loai_id"]
                            df_sua["ten"] = lo["ten"]
                            df_sua["phan_loai"] = lo["phan_loai"]
                            df_sua["day"] = lo["day"]
                            df_sua["rong"] = lo["rong"]
                            df_sua["dai"] = lo["dai"]
                            df_sua["so_thanh"] = so_thanh
                            df_sua["so_luong"] = so_luong
                            df_sua["loai_nhap"] = lo["loai_nhap"]
                            df_sua["kieu_tinh"] = kieu_tinh_hien_tai
                            
                            if lo["loai_nhap"] == "KHO":
                                df_sua["don_gia_ban"] = don_gia_ban
                                df_sua["thanh_tien"] = so_luong * don_gia_ban
                            else:
                                df_sua["don_gia_ban"] = 0.0
                                df_sua["thanh_tien"] = 0.0
                                
                            st.session_state.dong_sua_xuat = None
                            st.rerun()
                    with c_nut2:
                        if st.button("❌ Hủy sửa dòng", use_container_width=True):
                            st.session_state.dong_sua_xuat = None
                            st.rerun()
                else:
                    if st.button("➕ Thêm vào phiếu", use_container_width=True, type="primary"):
                        da_co = False
                        for item in st.session_state.ds_xuat:
                            if item["kho_phan_loai_id"] == lo["kho_phan_loai_id"]:
                                if kieu_tinh_hien_tai == "M3":
                                    item["so_thanh"] += so_thanh
                                    item["so_luong"] = float(lo["m3"]) * item["so_thanh"] / float(lo["thanh"])
                                else:
                                    item["so_luong"] += so_luong
                                
                                if lo["loai_nhap"] == "KHO":
                                    item["don_gia_ban"] = don_gia_ban
                                    item["thanh_tien"] = item["so_luong"] * don_gia_ban
                                da_co = True
                                break
                        
                        if not da_co:
                            item = {
                                "kho_phan_loai_id": lo["kho_phan_loai_id"], "ten": lo["ten"], "phan_loai": lo["phan_loai"],
                                "day": lo["day"], "rong": lo["rong"], "dai": lo["dai"], "so_thanh": so_thanh,
                                "so_luong": so_luong, "loai_nhap": lo["loai_nhap"], "kieu_tinh": kieu_tinh_hien_tai
                            }
                            if lo["loai_nhap"] == "KHO":
                                item["don_gia_ban"] = don_gia_ban
                                item["thanh_tien"] = so_luong * don_gia_ban
                            st.session_state.ds_xuat.append(item)
                        st.rerun()
        
            st.divider()
            st.subheader("📋 Các mặt hàng sẽ xuất")

            if st.session_state.ds_xuat:
                h1, h2, h3, h4, h5, h6, h7, h8, h9 = st.columns([2.5, 1.5, 1.2, 1, 1, 1.2, 1.2, 0.6, 0.6])
                h1.write("**Tên gỗ**")
                h2.write("**Phân loại**")
                h3.write("**Quy cách**")
                h4.write("**Thanh**")
                h5.write("**Số lượng**")
                h6.write("**Đơn giá**")
                h7.write("**Thành tiền**")
                h8.write("**✏️**")
                h9.write("**❌**")

                tong_tien_phieu = 0.0
                for i, item in enumerate(st.session_state.ds_xuat):
                    c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns([2.5, 1.5, 1.2, 1, 1, 1.2, 1.2, 0.6, 0.6])
                    
                    prefix = "👉 " if st.session_state.dong_sua_xuat == i else ""
                    c1.write(f"{prefix}{item['ten']}")
                    c2.write(item["phan_loai"])
                    c3.write(f'{int(item["day"])}x{int(item["rong"])}x{int(item["dai"])}' if item["day"] is not None else "Kg")
                    c4.write(f'{item["so_thanh"]}' if item["day"] is not None else "-")
                    c5.write(f'{item["so_luong"]:.3f} m³' if item["day"] is not None else f'{item["so_luong"]:.3f} kg')
                    c6.write(f'{item["don_gia_ban"]:,.0f}' if item["loai_nhap"] == "KHO" else "-")
                    c7.write(f'{item["thanh_tien"]:,.0f} đ' if item["loai_nhap"] == "KHO" else "-")
                    
                    if item["loai_nhap"] == "KHO":
                        tong_tien_phieu += item["thanh_tien"]
                    
                    with c8:
                        if st.button("✏️", key=f"sua_item_{i}", use_container_width=True):
                            st.session_state.dong_sua_xuat = i
                            st.rerun()
                    with c9:
                        if st.button("❌", key=f"xoa_{i}", use_container_width=True):
                            st.session_state.ds_xuat.pop(i)
                            if st.session_state.dong_sua_xuat == i:
                                st.session_state.dong_sua_xuat = None
                            st.rerun()
                
                st.write(f"### Tổng tiền: {tong_tien_phieu:,.0f} đ")
            else:
                st.info("Chưa có mặt hàng nào.")

            if st.session_state.ds_xuat:
                st.divider()
                ten_nut_luu = "💾 Cập nhật phiếu cũ" if st.session_state.get("sua_phieu_xuat") is not None else "💾 Lưu phiếu xuất"
                
                if st.button(ten_nut_luu, use_container_width=True, type="primary"):
                    try:
                        if st.session_state.get("sua_phieu_xuat") is not None:
                            phieu_id = st.session_state.sua_phieu_xuat
                            hoan_kho_phieu_xuat(phieu_id)
                            xoa_cong_no(phieu_xuat_id=phieu_id)
                            xoa_chi_tiet_phieu_xuat(phieu_id)
                            sua_phieu_xuat(phieu_id, ngay, kh["id"], ghi_chu)
                            luu_phieu_xuat(so_phieu=so_phieu, ngay=ngay, khach_hang_id=kh["id"], ghi_chu=ghi_chu, ds_hang=st.session_state.ds_xuat, phieu_xuat_id=phieu_id)
                            
                            del st.session_state["sua_phieu_xuat"]
                            key_da_load = f"loaded_xuat_{phieu_id}"
                            if key_da_load in st.session_state:
                                del st.session_state[key_da_load]
                        else:
                            luu_phieu_xuat(so_phieu=so_phieu, ngay=ngay, khach_hang_id=kh["id"], ghi_chu=ghi_chu, ds_hang=st.session_state.ds_xuat)

                        st.session_state.ds_xuat = []
                        st.session_state.dong_sua_xuat = None
                        if "lo_xuat" in st.session_state: del st.session_state["lo_xuat"]
                        st.success("Đã xử lý phiếu xuất thành công.")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
        else:
            st.info("Khách hàng chưa có hàng trong kho đã phân loại.")

    elif st.session_state.tab_xuat == "lich_su":
        ds = lay_ds_phieu_xuat()
        if len(ds) == 0:
            st.info("Chưa có phiếu xuất.")
        else:
            c1, c2, c3, c4, c5, c6, c7 = st.columns([1, 2, 4, 2, 1, 1, 1])
            c1.write("Số phiếu")
            c2.write("Ngày xuất")
            c3.write("Khách hàng")
            c4.write("Mặt hàng")
            c5.write("👁")
            c6.write("✏️")
            c7.write("🗑")
            st.divider()

            for row in ds:
                c1, c2, c3, c4, c5, c6, c7 = st.columns([1, 2, 4, 2, 1, 1, 1])
                c1.write(row["so_phieu"])
                c2.write(row["ngay"].strftime("%d/%m/%Y"))
                c3.write(row["khach_hang"])
                c4.write(row["so_mat_hang"])

                if c5.button("👁", key=f"xem_xuat_{row['id']}"):
                    st.session_state.xem_phieu_xuat = row["id"]
                    st.session_state.tab_xuat = "lich_su"
                    st.rerun()

                if c6.button("✏️", key=f"sua_xuat_{row['id']}"):
                    st.session_state.sua_phieu_xuat = row["id"]
                    st.session_state.tab_xuat = "lap"
                    st.session_state.dong_sua_xuat = None
                    key_da_load = f"loaded_xuat_{row['id']}"
                    if key_da_load in st.session_state:
                        del st.session_state[key_da_load]
                    st.rerun()

                if c7.button("🗑", key=f"xoa_xuat_{row['id']}"):
                    st.session_state.xac_nhan_xoa_xuat = row["id"]

                if st.session_state.xac_nhan_xoa_xuat == row["id"]:
                    dialog_xoa_xuat(row["id"])