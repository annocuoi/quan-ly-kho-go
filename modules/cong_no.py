import streamlit as st

from database.db import (
    lay_ds_cong_no,
    lay_chi_tiet_cong_no,
    lay_lich_su_khach_hang,
    da_thanh_toan_het
)



@st.dialog("📄 Lịch sử khách hàng")
def dialog_lich_su(khach):

    ds = lay_lich_su_khach_hang(
        khach["id"]
    )

    if len(ds) == 0:

        st.info("Chưa có dữ liệu.")

        return

    for dong in ds:

        with st.container(border=True):

            st.write(f"📅 {dong['ngay']}")

            st.write(f"🪵 {dong['ten_go']}")

            if dong["kieu_tinh"] == "M3":

                st.write(
                    f"📦 {dong['so_thanh']} thanh"
                )

            else:

                st.write(
                    f"⚖️ {dong['so_luong']} kg"
                )

            st.write(
                f"💰 Đơn giá: {dong['don_gia']:,.0f} đ"
            )

            st.write(
                f"💵 Thành tiền: {dong['thanh_tien']:,.0f} đ"
            )

            st.write(
                f"📌 Trạng thái: {dong['trang_thai']}"
            )

def show():

    st.header("💰 Công nợ")

    ds = lay_ds_cong_no()

    if len(ds) == 0:

        st.info("Chưa có công nợ.")

        return

    for kh in ds:

        with st.expander(
            f"👤 {kh['ten']} | Còn nợ: {kh['con_no']:,.0f} đ"
        ):
            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Phát sinh",
                f"{kh['tong_no']:,.0f} đ"
            )

            c2.metric(
                "Đã thu",
                f"{kh['tong_thu']:,.0f} đ"
            )

            c3.metric(
                "Còn nợ",
                f"{kh['con_no']:,.0f} đ"
            )
            st.divider()

            c1, c2 = st.columns(2)

            with c1:

                if st.button(
                    "📄 Lịch sử",
                    key=f"ls_{kh['id']}",
                    width="stretch"
                ):

                    dialog_lich_su(kh)

            with c2:

                if not da_thanh_toan_het(
                    kh["id"]
                ):

                    if st.button(
                        "📝 Lập phiếu thu",
                        key=f"thu_{kh['id']}",
                        width="stretch"
                    ):

                        st.session_state.khach_thu = kh["id"]

                        st.session_state.page = "phieu_thu"

                        st.rerun()

            st.divider()

            if da_thanh_toan_het(
                kh["id"]
            ):

                st.success("🟢 Đã thanh toán")

            else:

                st.error("🔴 Còn công nợ")
            st.divider()

            ds_ct = lay_chi_tiet_cong_no(
                kh["id"]
            )

            for ct in ds_ct:

                c1, c2, c3 = st.columns([2,8,2])

                c1.write(ct["ngay"])

                c2.markdown(f"**{ct['dien_giai']}**")

                if ct["phat_sinh"] > 0:

                    c3.markdown(
                        f"🔺 **{ct['phat_sinh']:,.0f} đ**"
                    )

                else:

                    c3.markdown(
                        f"🔻 **{ct['da_thu']:,.0f} đ**"
                    )