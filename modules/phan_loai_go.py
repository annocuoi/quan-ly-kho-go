import streamlit as st

from database.db import (
    lay_ds_phan_loai_go,
    them_phan_loai_go,
    sua_phan_loai_go,
    xoa_phan_loai_go
)


@st.dialog("➕ Thêm phân loại")
def them_dialog():

    ten = st.text_input("Tên phân loại")


    if st.button(
        "💾 Lưu",
        use_container_width=True
    ):

        if ten.strip() == "":
            st.warning("Chưa nhập tên phân loại.")
            return

        try:

            them_phan_loai_go(
                ten.strip()
            )

            st.success("Đã thêm thành công.")
            st.rerun()

        except Exception as e:

            st.error(str(e))


@st.dialog("✏️ Sửa phân loại")
def sua_dialog(row):

    ten = st.text_input(
        "Tên phân loại",
        value=row["ten"]
    )


    if st.button(
        "💾 Cập nhật",
        use_container_width=True
    ):

        if ten.strip() == "":
            st.warning("Chưa nhập tên phân loại.")
            return

        sua_phan_loai_go(
            row["id"],
            ten.strip()
        )

        st.success("Đã cập nhật.")

        st.rerun()


def show():

    st.header("📦 Danh mục phân loại")

    if st.button(
        "➕ Thêm phân loại",
        use_container_width=True
    ):
        them_dialog()

    st.divider()

    ds = lay_ds_phan_loai_go()

    if len(ds) == 0:

        st.info("Chưa có dữ liệu.")

        return

    h1, h2, h3, h4 = st.columns(
        [1, 7, 1, 1]
    )

    h1.markdown("**STT**")
    h2.markdown("**Tên phân loại**")
    h3.markdown("**Sửa**")
    h4.markdown("**Xóa**")

    st.divider()

    for i, row in enumerate(ds, start=1):

        c1, c2, c3, c4 = st.columns(
            [1, 7, 1, 1]
        )

        c1.write(i)

        c2.write(row["ten"])


        if c3.button(
            "✏️",
            key=f"sua_{row['id']}"
        ):
            sua_dialog(row)

        if c4.button(
            "🗑️",
            key=f"xoa_{row['id']}"
        ):

            xoa_phan_loai_go(
                row["id"]
            )

            st.success("Đã xóa.")

            st.rerun()