import streamlit as st
from datetime import date

from database.db import (
    lay_cong_no,
    them_thanh_toan,
    lay_lich_su_cong_no
)

@st.dialog("💵 Thu tiền")
def dialog_thu_tien(khach):

    st.write(f"**Khách hàng:** {khach['ten']}")

    ngay = st.date_input(
        "Ngày",
        value=date.today(),
        format="DD/MM/YYYY",
        key=f"ngay_thu_{khach['id']}"
    )

    so_tien = st.number_input(
        "Số tiền",
        min_value=0.0,
        step=1000.0,
        format="%.0f",
        key=f"sotien_thu_{khach['id']}"
    )

    ghi_chu = st.text_input(
        "Ghi chú",
        placeholder="Ví dụ: Chuyển khoản, tiền mặt...",
        key=f"ghichu_thu_{khach['id']}"
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Lưu", use_container_width=True, type="primary"):

            if so_tien <= 0:
                st.warning("Vui lòng nhập số tiền lớn hơn 0.")
                st.stop()

            them_thanh_toan(
                khach_hang_id=khach["id"],
                ngay=str(ngay),
                so_tien=so_tien,
                ghi_chu=ghi_chu
            )

            st.success("Đã thu tiền thành công.")
            st.rerun()

    with col2:
        st.button("Đóng", use_container_width=True)
        
def show():

    st.header("💰 Công nợ khách hàng")

    ds = lay_cong_no()

    if not ds:
        st.info("Chưa có dữ liệu.")
        return

    # ===== Header =====
    c1, c2, c3, c4, c5, c6 = st.columns([4, 2, 2, 2, 1, 1])

    c1.write("**Khách hàng**")
    c2.write("**Phát sinh**")
    c3.write("**Đã trả**")
    c4.write("**Còn nợ**")
    c5.write("👁")
    c6.write("💵")

    st.divider()

    # ===== Danh sách =====
    for row in ds:

        con_no = row["phat_sinh"] - row["da_tra"]

        c1, c2, c3, c4, c5, c6 = st.columns([4, 2, 2, 2, 1, 1])

        c1.write(row["ten"])
        c2.write(f'{row["phat_sinh"]:,.0f}')
        c3.write(f'{row["da_tra"]:,.0f}')
        c4.write(f'**{con_no:,.0f}**')

        if c5.button("👁", key=f"xem_{row['id']}"):
            st.info(f"Xem lịch sử công nợ của {row['ten']} (đang làm)")

        if c6.button("💵", key=f"thu_{row['id']}"):
            dialog_thu_tien(row)