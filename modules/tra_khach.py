import streamlit as st
from database.db import (
    lay_ds_cho_tra,
    dua_vao_ham_lai,
    tra_khach
)


def show():

    st.header("📤 Trả khách")

    ds = lay_ds_cho_tra()

    if len(ds) == 0:

        st.info("Không có lô gỗ chờ trả.")

        return

    for dong in ds:

        with st.container(border=True):

            st.markdown(f"**👤 Khách hàng:** {dong['khach_hang']}")

            st.markdown(f"**🪵 Loại gỗ:** {dong['ma_go']} - {dong['ten_go']}")

            if dong["kieu_tinh"] == "M3":

                st.markdown(
                    f"**📦 Số lượng:** {dong['so_thanh']} thanh"
                )

            else:

                st.markdown(
                    f"**⚖️ Số lượng:** {dong['so_luong']} Kg"
                )

            st.markdown(
                f"**📅 Ngày nhận:** {dong['ngay']}"
            )
            st.markdown(
                f"**💰 Đơn giá:** {dong['don_gia']:,.0f} đ"
            )

            st.markdown(
                f"**💵 Thành tiền:** {dong['thanh_tien']:,.0f} đ"
            )

            c1, c2 = st.columns(2)

            with c1:

                if st.button(
                    "🔥 Đưa vào hầm lại",
                    key=f"hamlai_{dong['id']}",
                    width="stretch"
                ):

                    dua_vao_ham_lai(
                        dong["id"]
                    )

                    st.success("Đã chuyển về chờ vào hầm.")

                    st.rerun()

            with c2:

                if st.button(
                    "✅ Đã trả khách",
                    key=f"trakhach_{dong['id']}",
                    width="stretch"
                ):

                    tra_khach(
                        dong["id"]
                    )

                    st.success("Đã trả khách.")

                    st.rerun()