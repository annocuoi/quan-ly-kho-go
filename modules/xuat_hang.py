import streamlit as st


def show():

    st.header("🚚 Xuất hàng")

    tab1, tab2 = st.tabs([
        "📝 Lập phiếu xuất",
        "📜 Lịch sử xuất"
    ])

    with tab1:
        st.info("Đang phát triển...")

    with tab2:
        st.info("Đang phát triển...")