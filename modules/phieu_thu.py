import streamlit as st
from datetime import date

from database.db import (
    lay_ds_cong_no,
    lay_con_no_khach,
    thu_tien
)


def show():

    st.header("💵 Phiếu thu")

    if "khach_thu" not in st.session_state:

        st.info("Chưa chọn khách hàng.")

        return

    ds = lay_ds_cong_no()

    khach = next(

        (
            x for x in ds
            if x["id"] == st.session_state.khach_thu
        ),

        None

    )

    if khach is None:

        st.error("Không tìm thấy khách hàng.")

        return

    con_no = lay_con_no_khach(
        khach["id"]
    )

    st.subheader(f"👤 {khach['ten']}")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Phát sinh",
        f"{khach['tong_no']:,.0f} đ"
    )

    c2.metric(
        "Đã thu",
        f"{khach['tong_thu']:,.0f} đ"
    )

    c3.metric(
        "Còn nợ",
        f"{con_no:,.0f} đ"
    )

    st.divider()

    ngay = st.date_input(
        "Ngày thu",
        value=date.today()
    )

    st.divider()
    so_tien = st.number_input(
        "Số tiền thu",
        min_value=0.0,
        max_value=float(con_no),
        step=1000.0,
        format="%.0f"
    )

    ghi_chu = st.text_input(
        "Ghi chú",
        value="Thu tiền"
    )

    st.divider()

    if "xac_nhan_phieu_thu" not in st.session_state:

        st.session_state.xac_nhan_phieu_thu = False

    if not st.session_state.xac_nhan_phieu_thu:

        c1, c2 = st.columns(2)

        with c1:

            if st.button(
                "❌ Hủy",
                width="stretch"
            ):

                st.session_state.pop(
                    "khach_thu",
                    None
                )

                st.session_state.pop(
                    "xac_nhan_phieu_thu",
                    None
                )

                st.session_state.page = "cong_no"

                st.rerun()
        with c2:

            if st.button(
                "💾 Tiếp tục",
                width="stretch",
                type="primary"
            ):

                if so_tien <= 0:

                    st.warning(
                        "Nhập số tiền."
                    )

                else:

                    st.session_state.xac_nhan_phieu_thu = True

                    st.session_state.so_tien_thu = so_tien

                    st.session_state.ghi_chu_thu = ghi_chu

                    st.session_state.ngay_thu = str(ngay)

                    st.rerun()

    else:

        st.subheader("✅ Xác nhận phiếu thu")

        st.info(
            "Kiểm tra lại thông tin trước khi lưu."
        )

        st.divider()

        st.markdown(f"""
        ### 👤 Khách hàng

        **{khach['ten']}**

        ### 💵 Số tiền thu

        **{st.session_state.so_tien_thu:,.0f} đ**

        ### 📝 Ghi chú

        {st.session_state.ghi_chu_thu}
        """)

        c1, c2 = st.columns(2)

        with c1:

            if st.button(
                "⬅ Quay lại",
                width="stretch"
            ):

                st.session_state.xac_nhan_phieu_thu = False

                st.rerun()

        with c2:
            if st.button(
                "✅ Lưu phiếu",
                width="stretch",
                type="primary"
            ):
                # Thêm spinner để người dùng biết app đang chạy, không bấm liên tục
                with st.spinner("Đang lưu phiếu thu..."):
                    ok = thu_tien(
                        khach["id"],
                        st.session_state.so_tien_thu,
                        st.session_state.ghi_chu_thu,
                        st.session_state.ngay_thu
                    )

                    if ok:
                        # Dọn dẹp session
                        st.session_state.pop("khach_thu", None)
                        st.session_state.pop("xac_nhan_phieu_thu", None)
                        st.session_state.pop("so_tien_thu", None)
                        st.session_state.pop("ghi_chu_thu", None)
                        st.session_state.pop("ngay_thu", None)

                        # Thông báo thành công
                        st.toast("Đã thu tiền thành công!", icon="✅")
                        st.session_state.page = "cong_no"
                        st.rerun()
                    else:
                        st.session_state.xac_nhan_phieu_thu = False
                        st.error("Thu tiền thất bại. Vui lòng kiểm tra lại dữ liệu.")
