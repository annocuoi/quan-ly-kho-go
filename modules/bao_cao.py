import streamlit as st
import pandas as pd
import io

from datetime import date
from utils.pdf_bao_cao import tao_pdf_bao_cao

from database.db import (
    lay_ds_khach_hang,
    lay_bao_cao_nhap
)


def show():

    st.header("📊 Báo cáo")

    tab_nhap, = st.tabs(["📥 Nhập hàng"])

    with tab_nhap:

        c1, c2, c3, c4 = st.columns([2, 2, 2, 1])

        with c1:
            tu_ngay = st.date_input("Từ ngày", value=date.today())

        with c2:
            den_ngay = st.date_input("Đến ngày", value=date.today())

        with c3:

            ds_kh = lay_ds_khach_hang()

            options = [{"id": None, "ten": "Tất cả"}]
            options.extend(ds_kh)

            ten_kh = st.selectbox(
                "Khách hàng",
                [x["ten"] for x in options]
            )

            khach_hang_id = next(
                x["id"] for x in options
                if x["ten"] == ten_kh
            )

        with c4:

            st.write("")
            st.write("")

            xem = st.button(
                "🔍 Xem",
                use_container_width=True,
                type="primary"
            )

        st.divider()

        if not xem:
            return

        ds = lay_bao_cao_nhap(
            tu_ngay,
            den_ngay,
            khach_hang_id
        )

        if not ds:
            st.warning("Không có dữ liệu.")
            return

        df = pd.DataFrame(ds)

        df.columns = [
            "Ngày",
            "Số phiếu",
            "Khách hàng",
            "Tên gỗ",
            "Ký hiệu",
            "Dày",
            "Rộng",
            "Dài",
            "Kg",
            "Thanh",
            "M³",
            "Đơn giá",
            "Thành tiền",
        ]

        df.insert(0, "STT", range(1, len(df) + 1))

        # =============================
        # TÍNH TỔNG (PHẢI LÀM TRƯỚC KHI FORMAT)
        # =============================

        tong_kg = df["Kg"].fillna(0).sum()
        tong_thanh = df["Thanh"].fillna(0).sum()
        tong_m3 = df["M³"].fillna(0).sum()
        tong_tien = df["Thành tiền"].fillna(0).sum()

        # =============================
        # ĐỊNH DẠNG HIỂN THỊ
        # =============================

        df["Ngày"] = pd.to_datetime(
            df["Ngày"]
        ).dt.strftime("%d/%m/%Y")

        for c in ["Dày", "Rộng", "Dài", "Thanh"]:
            df[c] = df[c].apply(
                lambda x: "" if pd.isna(x) else int(x)
            )

        df["Kg"] = df["Kg"].apply(
            lambda x: "" if pd.isna(x) else f"{x:,.0f}"
        )

        df["M³"] = df["M³"].apply(
            lambda x: "" if pd.isna(x) else f"{x:.3f}"
        )

        df["Đơn giá"] = df["Đơn giá"].apply(
            lambda x: f"{x:,.0f}"
        )

        df["Thành tiền"] = df["Thành tiền"].apply(
            lambda x: f"{x:,.0f}"
        )

        # =============================
        # DÒNG TỔNG
        # =============================

        df.loc[len(df)] = {
            "STT": "",
            "Ngày": "",
            "Số phiếu": "",
            "Khách hàng": "",
            "Tên gỗ": "TỔNG CỘNG",
            "Ký hiệu": "",
            "Dày": "",
            "Rộng": "",
            "Dài": "",
            "Kg": f"{tong_kg:,.0f}" if tong_kg else "",
            "Thanh": f"{tong_thanh:,.0f}" if tong_thanh else "",
            "M³": f"{tong_m3:.3f}" if tong_m3 else "",
            "Đơn giá": "",
            "Thành tiền": f"{tong_tien:,.0f}",
        }

        # =============================
        # PDF
        # =============================

        pdf = tao_pdf_bao_cao(
            df,
            tu_ngay,
            den_ngay,
            ten_kh
        )

        # =============================
        # EXCEL
        # =============================

        buffer = io.BytesIO()

        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(
                writer,
                index=False,
                sheet_name="Báo cáo nhập"
            )

        buffer.seek(0)

        c1, c2 = st.columns(2)

        with c1:
            st.download_button(
                "📄 Xuất PDF",
                data=pdf,
                file_name="Bao_cao_nhap_hang.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary"
            )

        with c2:
            st.download_button(
                "📊 Xuất Excel",
                data=buffer,
                file_name="Bao_cao_nhap_hang.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                type="primary"
            )
        st.markdown("""
        <style>
        div[data-testid="stDataFrame"] table {
            font-size: 15px !important;
        }

        div[data-testid="stDataFrame"] th {
            font-size: 15px !important;
            font-weight: 700 !important;
        }

        div[data-testid="stDataFrame"] td {
            font-size: 14px !important;
            font-weight: 500 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )