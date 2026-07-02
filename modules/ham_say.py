import streamlit as st
from datetime import date
from datetime import datetime
from database.db import (
    lay_ds_ham,
    lay_ds_trong_tat_ca_ham,
    lay_lo_go_chua_vao_ham,
    dua_vao_ham,
    ra_ham
)

@st.dialog("Đưa gỗ vào hầm")
def dialog_dua_vao_ham(ham):

    ds = lay_lo_go_chua_vao_ham()

    if len(ds) == 0:

        st.info("Không còn lô gỗ nào.")

        return

    ds_hien = [

        f'{row["ngay"]} | {row["khach_hang"]} | {row["ten_go"]}'

        for row in ds

    ]

    chon = st.selectbox(

        "Chọn lô gỗ",

        ds_hien

    )

    lo = next(

        row

        for row in ds

        if f'{row["ngay"]} | {row["khach_hang"]} | {row["ten_go"]}' == chon

    )

    if st.button(

        "Đưa vào hầm",

        width="stretch"

    ):

        dua_vao_ham(

            ham["id"],

            lo["id"],

            str(date.today())

        )

        st.success("Đã đưa vào hầm.")

        st.rerun()

def show():

    st.header("🔥 Hầm sấy")

    ds_ham = lay_ds_ham()
    ds_all = lay_ds_trong_tat_ca_ham()
    cols = st.columns(3)

    for i, ham in enumerate(ds_ham):

        with cols[i % 3]:

            ds = [
                row
                for row in ds_all
                if row["ham_id"] == ham["id"]
            ]

            st.subheader(
                f'{ham["ten_ham"]} ({len(ds)} lô)'
            )
            if st.button(

                "➕ Đưa vào hầm",

                key=f"dua_{ham['id']}",

                width="stretch"

            ):

                dialog_dua_vao_ham(ham)


            if len(ds) == 0:

                st.success("✅ Hầm đang trống")

            else:

                for dong in ds:

                    if isinstance(dong["ngay_vao"], str):
                        ngay_vao = datetime.strptime(
                            dong["ngay_vao"],
                            "%Y-%m-%d"
                        ).date()
                    else:
                        ngay_vao = dong["ngay_vao"]

                    so_ngay = (date.today() - ngay_vao).days

                    with st.container(border=True):

                        st.markdown(
                            f"**👤 Khách hàng:** {dong['khach_hang']}"
                        )

                        st.markdown(
                            f"**🪵 Loại gỗ:** {dong['ma_go']} - {dong['ten_go']}"
                        )

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
                            f"**🔥 Vào hầm:** {dong['ngay_vao']}"
                        )

                        st.markdown(
                            f"**⏳ Đã sấy:** {so_ngay} ngày"
                        )
                        if st.button(
                            "🚪 Ra hầm",
                            key=f"ra_{dong['id']}",
                            width="stretch"
                        ):

                            ra_ham(
                                dong["id"],
                                str(date.today())
                            )

                            st.success("Đã ra hầm.")

                            st.rerun()