import streamlit as st
from datetime import date

from database.db import (
    lay_cong_no,
    them_phat_sinh_cong_no,
    lay_lich_su_cong_no
)

@st.dialog("📜 Lịch sử công nợ", width="large")
def dialog_lich_su(khach):

    st.subheader(f"👤 {khach['ten']}")

    ds = lay_lich_su_cong_no(khach["id"])

    if not ds:
        st.info("Khách hàng chưa có công nợ.")
        return

    data = []

    tong_khach_no = 0
    tong_minh_no = 0
    tong_khach_tra = 0

    for row in ds:

        noi_dung = ""
        khach_no = "-"
        minh_no = "-"
        khach_tra = "-"

        if row["loai"] == "CONG_SAY":

            noi_dung = f"Công sấy - Phiếu {row['so_phieu']}"
            khach_no = f"{row['so_tien']:,.0f}"
            tong_khach_no += row["so_tien"]

        elif row["loai"] == "MUA_GO":

            noi_dung = f"Mua gỗ - Phiếu {row['so_phieu']}"
            minh_no = f"{row['so_tien']:,.0f}"
            tong_minh_no += row["so_tien"]

        elif row["loai"] == "THU_TIEN":

            noi_dung = row["ghi_chu"] or "Thu tiền"
            khach_tra = f"{row['so_tien']:,.0f}"
            tong_khach_tra += row["so_tien"]

        else:
            continue

        data.append({
            "Ngày": row["ngay"].strftime("%d/%m/%Y"),
            "Nội dung": noi_dung,
            "Khách nợ": khach_no,
            "Mình nợ": minh_no,
            "Khách trả": khach_tra
        })

    import pandas as pd

    df = pd.DataFrame(data)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Khách nợ", f"{tong_khach_no:,.0f}")
    c2.metric("Mình nợ", f"{tong_minh_no:,.0f}")
    c3.metric("Khách trả", f"{tong_khach_tra:,.0f}")
    c4.metric(
        "Còn nợ",
        f"{tong_khach_no - tong_minh_no - tong_khach_tra:,.0f}"
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

            them_phat_sinh_cong_no(
                khach_hang_id=khach["id"],
                ngay=str(ngay),
                loai="THU_TIEN",
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
    c1, c2, c3, c4, c5, c6, c7 = st.columns([4, 2, 2, 2, 2, 1, 1])

    c1.write("**Khách hàng**")
    c2.write("**Công sấy**")
    c3.write("**Mua gỗ**")
    c4.write("**Khách trả**")
    c5.write("**Còn nợ**")
    c6.write("👁")
    c7.write("💵")

    st.divider()

    # ===== Danh sách =====
    for row in ds:

        con_no = (
            row["cong_say"]
            - row["mua_go"]
            - row["thu_tien"]
        )

        c1, c2, c3, c4, c5, c6, c7 = st.columns([4, 2, 2, 2, 2, 1, 1])

        c1.write(row["ten"])
        c2.write(f'{row["cong_say"]:,.0f}')
        c3.write(f'{row["mua_go"]:,.0f}')
        c4.write(f'{row["thu_tien"]:,.0f}')
        c5.write(f'**{con_no:,.0f}**')

        if c6.button("👁", key=f"xem_{row['id']}"):
            dialog_lich_su(row)

        if c7.button("💵", key=f"thu_{row['id']}"):
            dialog_thu_tien(row)