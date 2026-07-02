import streamlit as st
import sqlite3

from database.db import (
    lay_ds_khach_hang,
    them_khach_hang,
    sua_khach_hang,
    xoa_khach_hang
)

@st.dialog("Sửa khách hàng")
def sua_dialog(row):

    ten = st.text_input(
        "Tên Khách Hàng",
        value=row["ten"]
    )

    dien_thoai = st.text_input(
        "Điện thoại",
        value=row["dien_thoai"] or ""
    )

    dia_chi = st.text_area(
        "Địa chỉ",
        value=row["dia_chi"] or ""
    )

    if st.button("💾 Cập nhật", width="stretch"):

        if ten.strip() == "":

            st.warning("Chưa nhập tên.")

            return

        sua_khach_hang(
            row["id"],
            ten.strip(),
            dien_thoai.strip(),
            dia_chi.strip()
        )

        st.success("Đã cập nhật")

        st.rerun()

def show():

    st.header("👤 Danh mục khách hàng")

    with st.form("them_khach_hang", clear_on_submit=True):

        ten = st.text_input("Tên Khách Hàng")

        dien_thoai = st.text_input("Điện thoại")

        dia_chi = st.text_area("Địa chỉ")

        luu = st.form_submit_button("💾 Lưu")

        if luu:

            if ten.strip() == "":

                st.warning("Nhập đầy đủ thông tin.")

            else:

                try:

                    them_khach_hang(
                        ten.strip(),
                        dien_thoai.strip(),
                        dia_chi.strip()
                    )

                    st.success("Đã thêm thành công")

                    st.rerun()

                except sqlite3.IntegrityError:

                    st.error("Không thể thêm nhà cung cấp.")

    st.divider()

    st.subheader("Danh sách")

    ds = lay_ds_khach_hang()

    if len(ds) == 0:

        st.info("Chưa có dữ liệu.")

        return

    cot1, cot2, cot3, cot4, cot5, cot6 = st.columns([1,4,2,4,1,1])

    cot1.write("STT")
    cot2.write("Tên")
    cot3.write("Điện thoại")
    cot4.write("Địa chỉ")
    cot5.write("Sửa")
    cot6.write("Xóa")

    st.divider()

    for i, row in enumerate(ds, start=1):

        c1, c2, c3, c4, c5, c6 = st.columns([1,4,2,4,1,1])

        c1.write(i)

        c2.write(row["ten"])

        c3.write(row["dien_thoai"])

        c4.write(row["dia_chi"])

        if c5.button("✏️", key=f"sua_{row['id']}"):

            sua_dialog(row)
        if c6.button("🗑️", key=f"xoa_{row['id']}"):

            xoa_khach_hang(row["id"])

            st.success("Đã xóa thành công")

            st.rerun()