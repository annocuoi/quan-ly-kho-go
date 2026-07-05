import streamlit as st
import sqlite3

from database.db import (
    lay_ds_loai_go,
    them_loai_go,
    sua_loai_go,
    xoa_loai_go
)


@st.dialog("➕ Thêm loại gỗ")
def them_dialog():

    ma_go = st.text_input("Mã gỗ")

    ten_go = st.text_input("Tên gỗ")

    kieu_hien_thi = st.selectbox(
        "Kiểu tính",
        [
            "📦 Tính theo khối (m³)",
            "⚖️ Tính theo trọng lượng"
        ]
    )

    kieu_tinh = (
        "M3"
        if kieu_hien_thi == "📦 Tính theo khối (m³)"
        else "TRONG_LUONG"
    )

    day = None
    rong = None
    dai = None

    if kieu_tinh == "M3":

        c1, c2, c3 = st.columns(3)

        with c1:
            day = st.number_input("Dày (mm)", min_value=0.0)

        with c2:
            rong = st.number_input("Rộng (mm)", min_value=0.0)

        with c3:
            dai = st.number_input("Dài (mm)", min_value=0.0)

    if st.button("💾 Lưu", width="stretch"):

        if ma_go.strip() == "":
            st.warning("Chưa nhập mã gỗ")
            return

        if ten_go.strip() == "":
            st.warning("Chưa nhập tên gỗ")
            return

        if kieu_tinh == "M3":

            if day <= 0:
                st.warning("Chưa nhập độ dày")
                return

            if rong <= 0:
                st.warning("Chưa nhập độ rộng")
                return

            if dai <= 0:
                st.warning("Chưa nhập chiều dài")
                return

        try:

            them_loai_go(
                ma_go.strip().upper(),
                ten_go.strip(),
                kieu_tinh,
                day,
                rong,
                dai
            )

            st.success("Đã thêm thành công")
            st.rerun()

        except sqlite3.IntegrityError:

            st.error("Mã gỗ đã tồn tại.")


@st.dialog("Sửa loại gỗ")
def sua_dialog(row):

    ma_go = st.text_input(
        "Mã gỗ",
        value=row["ma_go"]
    )

    ten_go = st.text_input(
        "Tên gỗ",
        value=row["ten_go"]
    )

    kieu_hien_thi = st.selectbox(
        "Kiểu tính",
        [
            "📦 Tính theo khối (m³)",
            "⚖️ Tính theo trọng lượng"
        ],
        index=0 if row["kieu_tinh"] == "M3" else 1
    )

    kieu_tinh = (
        "M3"
        if kieu_hien_thi == "📦 Tính theo khối (m³)"
        else "TRONG_LUONG"
    )

    day = row["day"]
    rong = row["rong"]
    dai = row["dai"]

    if kieu_tinh == "M3":

        c1, c2, c3 = st.columns(3)

        with c1:
            day = st.number_input(
                "Dày (mm)",
                value=float(row["day"] or 0)
            )

        with c2:
            rong = st.number_input(
                "Rộng (mm)",
                value=float(row["rong"] or 0)
            )

        with c3:
            dai = st.number_input(
                "Dài (mm)",
                value=float(row["dai"] or 0)
            )

    if st.button("💾 Cập nhật", width="stretch"):

        if ma_go.strip() == "" or ten_go.strip() == "":
            st.warning("Nhập đầy đủ thông tin.")
            return

        try:

            sua_loai_go(
                row["id"],
                ma_go.strip().upper(),
                ten_go.strip(),
                kieu_tinh,
                day,
                rong,
                dai
            )

            st.success("Đã cập nhật")
            st.rerun()

        except sqlite3.IntegrityError:

            st.error("Mã gỗ đã tồn tại.")


def show():

    st.header("🪵 Danh mục loại gỗ")

    if st.button("➕ Thêm loại gỗ", width="stretch"):
        them_dialog()

    st.divider()

    tu_khoa = st.text_input(
        "🔍 Tìm kiếm theo mã hoặc tên"
    )

    ds = lay_ds_loai_go(tu_khoa)

    st.subheader("Danh sách")

    if len(ds) == 0:
        st.info("Chưa có dữ liệu.")
        return

    cot1, cot2, cot3, cot4, cot5, cot6, cot7 = st.columns(
        [1, 2, 3, 2, 3, 1, 1]
    )

    cot1.write("STT")
    cot2.write("Mã")
    cot3.write("Tên")
    cot4.write("Kiểu")
    cot5.write("Quy cách")
    cot6.write("Sửa")
    cot7.write("Xóa")

    st.divider()

    for i, row in enumerate(ds, start=1):

        c1, c2, c3, c4, c5, c6, c7 = st.columns(
            [1, 2, 3, 2, 3, 1, 1]
        )

        c1.write(i)
        c2.write(row["ma_go"])
        c3.write(row["ten_go"])

        c4.write(
            "📦 Khối (m³)"
            if row["kieu_tinh"] == "M3"
            else "⚖️ Trọng lượng"
        )

        if row["kieu_tinh"] == "M3":
            quy_cach = (
                f'{int(row["day"])} × '
                f'{int(row["rong"])} × '
                f'{int(row["dai"])}'
            )
        else:
            quy_cach = "-"

        c5.write(quy_cach)

        if c6.button("✏️", key=f"sua_{row['id']}"):
            sua_dialog(row)

        if c7.button("🗑️", key=f"xoa_{row['id']}"):

            xoa_loai_go(row["id"])

            st.success("Đã xóa thành công")

            st.rerun()