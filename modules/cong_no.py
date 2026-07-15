import streamlit as st
from datetime import date
import io
import pandas as pd


from database.db import (
    lay_no_phai_thu,
    lay_no_phai_tra,
    lay_tong_hop_cong_no,
    them_thanh_toan,
    lay_ds_thanh_toan,
    lay_chi_tiet_cong_no,
    lay_chi_tiet_phieu_cong_no,
    lay_chi_tiet_tong_hop,  
    lay_ds_khach_hang
)
from utils.pdf_no_phai_thu import tao_pdf_no_phai_thu
from utils.pdf_no_phai_tra import tao_pdf_no_phai_tra
from utils.pdf_tong_hop_cong_no import tao_pdf_tong_hop_cong_no
from utils.pdf_chi_tiet_cong_no import tao_pdf_chi_tiet_cong_no


@st.dialog("📄 Chi tiết phiếu", width="large")
def dialog_chi_tiet(cong_no_id):

    phieu = lay_chi_tiet_cong_no(cong_no_id)
    ds_go = lay_chi_tiet_phieu_cong_no(cong_no_id)
    ds_tt = lay_ds_thanh_toan(cong_no_id)
    pdf = tao_pdf_chi_tiet_cong_no(
        phieu,
        ds_go,
        ds_tt,
    )
    excel_buffer = io.BytesIO()

    rows = []

    tong_kg = 0
    tong_thanh = 0
    tong_m3 = 0
    tong_tien = 0
    tong_tt = 0

    # Hàng hóa
    for row in ds_go:

        kg = row["so_luong"] if row["kieu_tinh"] == "TRONG_LUONG" else ""
        thanh = row["so_thanh"] if row["kieu_tinh"] == "M3" else ""
        m3 = row["so_luong"] if row["kieu_tinh"] == "M3" else ""

        if row["kieu_tinh"] == "TRONG_LUONG":
            tong_kg += row["so_luong"]
        else:
            tong_thanh += row["so_thanh"]
            tong_m3 += row["so_luong"]

        tong_tien += row["thanh_tien"]

        rows.append({
            "Ngày": phieu["ngay"].strftime("%d/%m/%Y"),
            "Nội dung": row["ten"],
            "Quy cách": "" if row["day"] is None else f"{int(row['day'])}x{int(row['rong'])}x{int(row['dai'])}",
            "Kg": kg,
            "Thanh": thanh,
            "M3": m3,
            "Đơn giá": row["don_gia"],
            "Thành tiền": row["thanh_tien"],
            "Thanh toán": "",
            "Ghi chú": ""
        })

    # Thanh toán
    for i, row in enumerate(ds_tt, start=1):

        tong_tt += row["so_tien"]

        rows.append({
            "Ngày": row["ngay"].strftime("%d/%m/%Y"),
            "Nội dung": f"Thanh toán lần {i}",
            "Quy cách": "",
            "Kg": "",
            "Thanh": "",
            "M3": "",
            "Đơn giá": "",
            "Thành tiền": "",
            "Thanh toán": row["so_tien"],
            "Ghi chú": row.get("ghi_chu", "")
        })

    # Tổng cộng
    rows.append({
        "Ngày": "",
        "Nội dung": "TỔNG CỘNG",
        "Quy cách": "",
        "Kg": tong_kg,
        "Thanh": tong_thanh,
        "M3": tong_m3,
        "Đơn giá": "",
        "Thành tiền": tong_tien,
        "Thanh toán": tong_tt,
        "Ghi chú": ""
    })

    rows.append({
        "Ngày": "",
        "Nội dung": "CÒN PHẢI THU" if tong_tien >= tong_tt else "SỐ DƯ TẠM ỨNG",
        "Quy cách": "",
        "Kg": "",
        "Thanh": "",
        "M3": "",
        "Đơn giá": "",
        "Thành tiền": max(tong_tien - tong_tt, 0),
        "Thanh toán": max(tong_tt - tong_tien, 0),
        "Ghi chú": ""
    })

    df = pd.DataFrame(rows)

    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Chi tiết", index=False)

    excel_buffer.seek(0)

    c1, c2, c3 = st.columns([6,2,2])

    with c1:
        st.subheader(f"📄 Phiếu {phieu['so_phieu']}")

    with c2:
        st.download_button(
            "📄 Xuất PDF",
            data=pdf,
            file_name=f"Chi_tiet_{phieu['so_phieu']}.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary",
        )

    with c3:
        st.download_button(
            "📊 Xuất Excel",
            data=excel_buffer,
            file_name=f"Chi_tiet_{phieu['so_phieu']}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="primary",
        )

    c1, c2, c3 = st.columns(3)

    c1.write(f"**Khách hàng:** {phieu['khach_hang']}")
    c2.write(f"**Ngày:** {phieu['ngay'].strftime('%d/%m/%Y')}")
    c3.write(f"**Tổng tiền:** {phieu['so_tien']:,.0f}")

    st.divider()

    # ================= CHI TIẾT HÀNG =================

    c1, c2, c3, c4, c5, c6, c7, c8, c9, c10 = st.columns(
        [3,2,1,1,1,2,2,2,2,2]
    )

    c1.write("**Tên gỗ**")
    c2.write("**Phân loại**")
    c3.write("**Dày**")
    c4.write("**Rộng**")
    c5.write("**Dài**")
    c6.write("**Kg**")
    c7.write("**Thanh**")
    c8.write("**M³**")
    c9.write("**Đơn giá**")
    c10.write("**Thành tiền**")

    st.divider()

    tong_kg = 0
    tong_thanh = 0
    tong_m3 = 0
    tong_tien = 0

    for row in ds_go:

        kg = row["so_luong"] if row["kieu_tinh"] == "TRONG_LUONG" else ""
        thanh = row["so_thanh"] if row["kieu_tinh"] == "M3" else ""
        m3 = row["so_luong"] if row["kieu_tinh"] == "M3" else ""

        if row["kieu_tinh"] == "TRONG_LUONG":
            tong_kg += row["so_luong"]
        else:
            tong_thanh += row["so_thanh"]
            tong_m3 += row["so_luong"]

        tong_tien += row["thanh_tien"]

        c1, c2, c3, c4, c5, c6, c7, c8, c9, c10 = st.columns(
            [3,2,1,1,1,2,2,2,2,2]
        )

        c1.write(row["ten"])
        c2.write("")
        c3.write("" if row["day"] is None else int(row["day"]))
        c4.write("" if row["rong"] is None else int(row["rong"]))
        c5.write("" if row["dai"] is None else int(row["dai"]))
        c6.write("" if kg == "" else f"{kg:,.0f}")
        c7.write("" if thanh == "" else f"{thanh:,}")
        c8.write("" if m3 == "" else f"{m3:.3f}")
        c9.write(f"{row['don_gia']:,.0f}")
        c10.write(f"{row['thanh_tien']:,.0f}")

    st.divider()

    c1, c2, c3, c4, c5, c6, c7, c8, c9, c10 = st.columns(
        [3,2,1,1,1,2,2,2,2,2]
    )

    c1.write("")
    c2.write("**TỔNG CỘNG**")
    c3.write("")
    c4.write("")
    c5.write("")
    c6.write(f"**{tong_kg:,.0f}**" if tong_kg else "")
    c7.write(f"**{tong_thanh:,}**" if tong_thanh else "")
    c8.write(f"**{tong_m3:.3f}**" if tong_m3 else "")
    c9.write("")
    c10.write(f"**{tong_tien:,.0f}**")
    

    st.divider()

    for i, row in enumerate(ds_tt, start=1):

        c1, c2, c3, c4, c5, c6, c7, c8, c9, c10 = st.columns(
            [3,2,1,1,1,2,2,2,2,2]
        )

        c1.write(row["ngay"].strftime("%d/%m/%Y"))
        c2.write(f"Thanh toán lần {i}")
        c3.write("")
        c4.write("")
        c5.write("")
        c6.write("")
        c7.write("")
        c8.write("")
        c9.write("")
        c10.write(f"{row['so_tien']:,.0f}")

    st.divider()

    c1, c2, c3, c4, c5, c6, c7, c8, c9, c10 = st.columns(
        [3,2,1,1,1,2,2,2,2,2]
    )

    c1.write("")
    c2.write("**ĐÃ THANH TOÁN**")
    c3.write("")
    c4.write("")
    c5.write("")
    c6.write("")
    c7.write("")
    c8.write("")
    c9.write("")
    c10.write(f"**{phieu['da_thanh_toan']:,.0f}**")

    c1, c2, c3, c4, c5, c6, c7, c8, c9, c10 = st.columns(
        [3,2,1,1,1,2,2,2,2,2]
    )

    c1.write("")
    c2.write("**CÒN PHẢI THU**")
    c3.write("")
    c4.write("")
    c5.write("")
    c6.write("")
    c7.write("")
    c8.write("")
    c9.write("")
    c10.write(f"**{phieu['con_lai']:,.0f}**")

@st.dialog("📊 Chi tiết tổng hợp", width="large")
def dialog_tong_hop(khach_hang_id):

    ds = lay_chi_tiet_tong_hop(khach_hang_id)

    if not ds:
        st.info("Không có dữ liệu.")
        return

    st.subheader("📥 Nợ phải thu")

    tong_thu = 0

    for row in ds:

        if row["loai"] != "CONG_SAY":
            continue

        tong_thu += row["con_lai"]

        c1, c2, c3, c4 = st.columns([1,2,2,2])

        if c1.button(
            "👁",
            key=f"tonghop_thu_{row['id']}"
        ):
            st.session_state.mo_chi_tiet = row["id"]
            st.rerun()

        c2.write(f"Phiếu {row['so_phieu']}")

        c3.write(
            row["ngay"].strftime("%d/%m/%Y")
        )

        c4.write(f"{row['con_lai']:,.0f}")

    st.divider()

    c1, c2 = st.columns([6,2])

    c1.write("**Tổng phải thu**")
    c2.write(f"**{tong_thu:,.0f}**")

    st.divider()

    st.subheader("📤 Nợ phải trả")

    tong_tra = 0

    for row in ds:

        if row["loai"] != "MUA_GO":
            continue

        tong_tra += row["con_lai"]

        c1, c2, c3, c4 = st.columns([1,2,2,2])

        if c1.button(
            "👁",
            key=f"tonghop_tra_{row['id']}"
        ):
            st.session_state.mo_chi_tiet = row["id"]
            st.rerun()

        c2.write(f"Phiếu {row['so_phieu']}")

        c3.write(
            row["ngay"].strftime("%d/%m/%Y")
        )

        c4.write(f"{row['con_lai']:,.0f}")

    st.divider()

    c1, c2 = st.columns([6,2])

    c1.write("**Tổng phải trả**")
    c2.write(f"**{tong_tra:,.0f}**")

    st.divider()

    c1, c2 = st.columns([6,2])

    c1.write("**Chênh lệch**")
    c2.write(f"**{tong_thu - tong_tra:,.0f}**")
@st.dialog("💵 Thanh toán")
def dialog_thanh_toan(cong_no_id, loai):

    phieu = lay_chi_tiet_cong_no(cong_no_id)

    if loai == "THU":
        st.subheader("💵 Thu tiền")
    else:
        st.subheader("💸 Trả tiền")
        
    st.write(f"Phiếu: {cong_no_id}")
    st.write(f"**Số phiếu:** {phieu['so_phieu']}")
    st.write(f"**Khách hàng:** {phieu['khach_hang']}")
    st.write(f"**Còn lại:** {phieu['con_lai']:,.0f}")

    st.divider()

    ngay = st.date_input("Ngày")

    so_tien = st.number_input(
        "Số tiền",
        min_value=0.0,
        step=1000.0,
        format="%.0f"
    )

    ghi_chu = st.text_input("Ghi chú")

    if st.button("💾 Lưu", use_container_width=True):
        
        if so_tien <= 0:
            st.warning("Nhập số tiền lớn hơn 0.")
            st.stop()

        them_thanh_toan(
            cong_no_id=cong_no_id,
            ngay=str(ngay),
            so_tien=so_tien,
            ghi_chu=ghi_chu
        )

        st.success("Đã lưu.")
        st.rerun()


def tab_no_phai_thu():

    st.subheader("📥 Nợ phải thu")
    # ==========================
    # Hàng 1: Từ ngày - Đến ngày
    # ==========================

    col1, col2 = st.columns(2)

    with col1:
        tu_ngay = st.date_input(
            "📅 Từ ngày",
            value=date.today().replace(day=1),
            format="DD/MM/YYYY"
        )

    with col2:
        den_ngay = st.date_input(
            "📅 Đến ngày",
            value=date.today(),
            format="DD/MM/YYYY"
        )

    # ==========================
    # Hàng 2: Khách hàng
    # ==========================

    
    col1, col2 = st.columns([2,3])

    with col1:
        ds_khach = ["Tất cả"] + [kh["ten"] for kh in lay_ds_khach_hang()]
        khach_chon = st.selectbox(
            "👤 Khách hàng",
            ds_khach
        )

    with col2:
        tu_khoa = st.text_input(
            "🔍 Tìm kiếm",
            placeholder="Phiếu, khách hàng, số tiền..."
        )

    st.divider()

    ds = lay_no_phai_thu(
        khach_hang=None if khach_chon == "Tất cả" else khach_chon,
        tu_ngay=tu_ngay,
        den_ngay=den_ngay
    )
    if tu_khoa:

        tk = tu_khoa.replace(",", "").strip().lower()

        ds = [
            row for row in ds
            if (
                tk in str(row["so_phieu"]).lower()
                or tk in row["khach_hang"].lower()
                or tk in str(int(row["so_tien"]))
                or tk in str(int(row["da_thanh_toan"]))
                or tk in str(int(row["con_lai"]))
            )
        ]

    if not ds:
        st.info("Không có dữ liệu.")
        return
    
    df = pd.DataFrame([
        {
            "STT": i,
            "Phiếu": row["so_phieu"],
            "Ngày": row["ngay"].strftime("%d/%m/%Y") if row["ngay"] else "",
            "Khách hàng": row["khach_hang"],
            "Phải thu": row["so_tien"],
            "Đã thu": row["da_thanh_toan"],
            "Còn lại": row["con_lai"],
        }
        for i, row in enumerate(ds, start=1)
    ])
    pdf = tao_pdf_no_phai_thu(
        df,
        tu_ngay,
        den_ngay,
        khach_chon
    )

    buffer = io.BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="No phai thu")

    buffer.seek(0)

    c1, c2 = st.columns(2)

    with c1:
        st.download_button(
            "📄 Xuất PDF",
            data=pdf,
            file_name="No_phai_thu.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary",
        )

    with c2:
        st.download_button(
            "📊 Xuất Excel",
            data=buffer,
            file_name="No_phai_thu.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="primary",
        )

    c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns(
        [1, 2, 2, 3, 2, 2, 2, 1, 1]
    )

    c1.write("**STT**")
    c2.write("**Phiếu**")
    c3.write("**Ngày**")
    c4.write("**Khách hàng**")
    c5.write("**Phải thu**")
    c6.write("**Đã thu**")
    c7.write("**Còn lại**")
    c8.write("👁")
    c9.write("💵")

    st.divider()

    tong_phai_thu = 0
    tong_con_lai = 0

    for i, row in enumerate(ds, start=1):

        tong_phai_thu += row["so_tien"]
        tong_con_lai += row["con_lai"]

        c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns(
            [1, 2, 2, 3, 2, 2, 2, 1, 1]
        )

        c1.write(i)

        c2.write(row["so_phieu"] or "")

        c3.write(
            row["ngay"].strftime("%d/%m/%Y")
            if row["ngay"] else ""
        )

        c4.write(row["khach_hang"])

        c5.write(f"{row['so_tien']:,.0f}")

        c6.write(f"{row['da_thanh_toan']:,.0f}")

        if row["con_lai"] > 0:
            c7.write(f"**{row['con_lai']:,.0f}**")
        else:
            c7.success("Đã thu")

        if c8.button(
            "👁",
            key=f"xem_thu_{row['id']}"
        ):
            dialog_chi_tiet(row["id"])

        if c9.button(
            "💵",
            key=f"thu_{row['id']}",
            disabled=row["con_lai"] <= 0
        ):
            dialog_thanh_toan(
                row["id"],
                "THU"
            )

    st.divider()

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Tổng phải thu",
        f"{tong_phai_thu:,.0f}"
    )

    c2.metric(
        "Đã thu",
        f"{tong_phai_thu - tong_con_lai:,.0f}"
    )

    c3.metric(
        "Còn phải thu",
        f"{tong_con_lai:,.0f}"
    )

def tab_no_phai_tra():

    st.subheader("📤 Nợ phải trả")
    # ==========================
    # Hàng 1: Từ ngày - Đến ngày
    # ==========================

    col1, col2 = st.columns(2)

    with col1:
        tu_ngay = st.date_input(
            "📅 Từ ngày",
            value=date.today().replace(day=1),
            format="DD/MM/YYYY",
            key="tra_tu_ngay"
        )

    with col2:
        den_ngay = st.date_input(
            "📅 Đến ngày",
            value=date.today(),
            format="DD/MM/YYYY",
            key="tra_den_ngay"
        )

    # ==========================
    # Hàng 2
    # ==========================

    col1, col2 = st.columns([1, 2])

    with col1:
        ds_khach = ["Tất cả"] + [kh["ten"] for kh in lay_ds_khach_hang()]

        khach_chon = st.selectbox(
            "👤 Khách hàng",
            ds_khach,
            key="tra_khach_hang"
        )

    with col2:
        tu_khoa = st.text_input(
            "🔍 Tìm kiếm",
            placeholder="Phiếu, khách hàng, số tiền...",
            key="tra_tim_kiem"
        )

    st.divider()

    ds = lay_no_phai_tra(
        khach_hang=None if khach_chon == "Tất cả" else khach_chon,
        tu_ngay=tu_ngay,
        den_ngay=den_ngay
    )
    if tu_khoa:

        tk = tu_khoa.replace(",", "").strip().lower()

        ds = [
            row for row in ds
            if (
                tk in str(row["so_phieu"]).lower()
                or tk in row["khach_hang"].lower()
                or tk in str(int(row["so_tien"]))
                or tk in str(int(row["da_thanh_toan"]))
                or tk in str(int(row["con_lai"]))
            )
        ]

    if not ds:
        st.info("Không có dữ liệu.")
        return

    df = pd.DataFrame([
        {
            "STT": i,
            "Phiếu": row["so_phieu"],
            "Ngày": row["ngay"].strftime("%d/%m/%Y") if row["ngay"] else "",
            "Khách hàng": row["khach_hang"],
            "Phải trả": row["so_tien"],
            "Đã trả": row["da_thanh_toan"],
            "Còn lại": row["con_lai"],
        }
        for i, row in enumerate(ds, start=1)
    ])

    pdf = tao_pdf_no_phai_tra(
        df,
        tu_ngay,
        den_ngay,
        khach_chon
    )

    buffer = io.BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="No phai tra")

    buffer.seek(0)

    c1, c2 = st.columns(2)

    with c1:
        st.download_button(
            "📄 Xuất PDF",
            data=pdf,
            file_name="No_phai_tra.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary",
        )

    with c2:
        st.download_button(
            "📊 Xuất Excel",
            data=buffer,
            file_name="No_phai_tra.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="primary",
        )


    c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns(
        [1, 2, 2, 3, 2, 2, 2, 1, 1]
    )

    c1.write("**STT**")
    c2.write("**Phiếu**")
    c3.write("**Ngày**")
    c4.write("**Khách hàng**")
    c5.write("**Phải trả**")
    c6.write("**Đã trả**")
    c7.write("**Còn lại**")
    c8.write("👁")
    c9.write("💸")

    st.divider()

    tong_phai_tra = 0
    tong_con_lai = 0

    for i, row in enumerate(ds, start=1):

        tong_phai_tra += row["so_tien"]
        tong_con_lai += row["con_lai"]

        c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns(
            [1, 2, 2, 3, 2, 2, 2, 1, 1]
        )

        c1.write(i)

        c2.write(row["so_phieu"] or "")

        c3.write(
            row["ngay"].strftime("%d/%m/%Y")
            if row["ngay"] else ""
        )

        c4.write(row["khach_hang"])

        c5.write(f"{row['so_tien']:,.0f}")

        c6.write(f"{row['da_thanh_toan']:,.0f}")

        if row["con_lai"] > 0:
            c7.write(f"**{row['con_lai']:,.0f}**")
        else:
            c7.success("Đã trả")

        if c8.button(
            "👁",
            key=f"xem_tra_{row['id']}"
        ):
            dialog_chi_tiet(row["id"])

        if c9.button(
            "💸",
            key=f"tra_{row['id']}",
            disabled=row["con_lai"] <= 0
        ):
            dialog_thanh_toan(
                row["id"],
                "TRA"
            )

    st.divider()

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Tổng phải trả",
        f"{tong_phai_tra:,.0f}"
    )

    c2.metric(
        "Đã trả",
        f"{tong_phai_tra - tong_con_lai:,.0f}"
    )

    c3.metric(
        "Còn phải trả",
        f"{tong_con_lai:,.0f}"
    )


def tab_tong_hop():

    st.subheader("📊 Tổng hợp")
    col1, col2 = st.columns(2)

    with col1:
        tu_ngay = st.date_input(
            "📅 Từ ngày",
            value=date.today().replace(day=1),
            key="tonghop_tungay",
        )

    with col2:
        den_ngay = st.date_input(
            "📅 Đến ngày",
            value=date.today(),
            key="tonghop_denngay",
        )

    col1, col2 = st.columns(2)

    with col1:

        ds_kh = lay_ds_khach_hang()

        chon_kh = st.selectbox(
            "👤 Khách hàng",
            ["Tất cả"] + [x["ten"] for x in ds_kh],
            key="tonghop_khachhang",
        )

    with col2:

        tu_khoa = st.text_input(
            "🔍 Tìm kiếm",
            placeholder="Muốn kiếm gì kiếm...",
            key="tonghop_timkiem",
        )

    khach_hang = None if chon_kh == "Tất cả" else chon_kh

    ds = lay_tong_hop_cong_no(
        tu_ngay,
        den_ngay,
        khach_hang,
    )
    if tu_khoa:

        tk = tu_khoa.replace(",", "").strip().lower()

        ds = [
            row for row in ds
            if (
                tk in row["ten"].lower()
                or tk in str(int(row["no_phai_thu"]))
                or tk in str(int(row["no_phai_tra"]))
                or tk in str(int(row["chenh_lech"]))
            )
        ]
    if not ds:
        st.info("Không có dữ liệu.")
        return

    df = pd.DataFrame([
        {
            "STT": i,
            "Khách hàng": row["ten"],
            "Phải thu": row["no_phai_thu"],
            "Phải trả": row["no_phai_tra"],
            "Chênh lệch": row["chenh_lech"],
        }
        for i, row in enumerate(ds, start=1)
    ])

    

    pdf = tao_pdf_tong_hop_cong_no(df)
    buffer = io.BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Tong hop")

    buffer.seek(0)

    c1, c2 = st.columns(2)

    with c1:
        st.download_button(
            "📄 Xuất PDF",
            pdf,
            "Tong_hop_cong_no.pdf",
            "application/pdf",
            use_container_width=True,
            type="primary",
        )

    with c2:
        st.download_button(
            "📊 Xuất Excel",
            buffer,
            "Tong_hop_cong_no.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="primary",
        )
    
    c1, c2, c3, c4, c5 = st.columns([3,2,2,2,1])

    c1.write("**Khách hàng**")
    c2.write("**Phải thu**")
    c3.write("**Phải trả**")
    c4.write("**Chênh lệch**")
    #c5.write("👁")

    st.divider()

    tong_thu = 0
    tong_tra = 0
    tong_chenh = 0

    for row in ds:

        tong_thu += row["no_phai_thu"]
        tong_tra += row["no_phai_tra"]
        tong_chenh += row["chenh_lech"]

        c1, c2, c3, c4, c5 = st.columns([3,2,2,2,1])

        c1.write(row["ten"])
        c2.write(f"{row['no_phai_thu']:,.0f}")
        c3.write(f"{row['no_phai_tra']:,.0f}")
        c4.write(f"**{row['chenh_lech']:,.0f}**")
        #if c5.button(
            #"👁",
            #key=f"xem_tonghop_{row['id']}"
        #):
            #dialog_tong_hop(row["id"])

    st.divider()

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Tổng phải thu",
        f"{tong_thu:,.0f}"
    )

    c2.metric(
        "Tổng phải trả",
        f"{tong_tra:,.0f}"
    )

    c3.metric(
        "Chênh lệch",
        f"{tong_chenh:,.0f}"
    )


def show():

    st.header("💰 Thanh toán")

    tab1, tab2, tab3 = st.tabs([
        "📥 Nợ phải thu",
        "📤 Nợ phải trả",
        "📊 Tổng hợp"
    ])

    with tab1:
        tab_no_phai_thu()

    with tab2:
        tab_no_phai_tra()

    with tab3:
        tab_tong_hop()

    if "mo_chi_tiet" in st.session_state:

        cong_no_id = st.session_state.pop("mo_chi_tiet")

        dialog_chi_tiet(cong_no_id)
