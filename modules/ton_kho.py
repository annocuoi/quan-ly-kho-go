import streamlit as st
import pandas as pd
from database.db import lay_ton_kho

def hien_thi(ds):

    if len(ds) == 0:
        st.info("Không có dữ liệu.")
        return

    du_lieu = []

    for row in ds:

        du_lieu.append({

            "Ngày nhận": row["ngay"].strftime("%d/%m/%Y"),

            "Khách hàng": row["khach_hang"],

            "Mã gỗ": row["ma_go"],

            "Tên gỗ": row["ten_go"],

            "Số thanh": row["so_thanh"],

            "Khối lượng": row["so_luong"],

            "Đơn vị": "m³" if row["kieu_tinh"] == "M3" else "Kg"

        })

    st.dataframe(
        pd.DataFrame(du_lieu),
        width="stretch",
        hide_index=True
    )
def show():

    st.header("📦 Tồn kho")
    tab_all, tab1, tab2, tab3 = st.tabs([
        "📦 Tất cả",
        "📥 Chờ vào hầm",
        "🔥 Đang sấy",
        "📤 Chờ trả khách"
    ])
    with tab_all:

        hien_thi(
            lay_ton_kho()
        )

    with tab1:

        hien_thi(
            lay_ton_kho("CHO_HAM")
        )

    with tab2:

        hien_thi(
            lay_ton_kho("DANG_SAY")
        )

    with tab3:

        hien_thi(
            lay_ton_kho("CHO_TRA")
        )