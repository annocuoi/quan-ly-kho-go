import streamlit as st
import pandas as pd
import io
from zoneinfo import ZoneInfo
from utils.pdf_kho_kho import tao_pdf_kho_kho

from utils.pdf_kho_tuoi import tao_pdf_kho_tuoi

from database.db import (
    lay_ds_khach_hang,
    lay_ds_loai_go,
    lay_kho_tuoi,
    lay_kho_kho
)

def show():

    if "tab_kho" not in st.session_state:
        st.session_state.tab_kho = "tuoi"

    st.header("🏬 Kho")

    c1, c2 = st.columns(2)

    with c1:
        if st.button(
            "🟢 Kho hàng tươi",
            type="primary" if st.session_state.tab_kho == "tuoi" else "secondary",
            use_container_width=True
        ):
            st.session_state.tab_kho = "tuoi"
            st.rerun()

    with c2:
        if st.button(
            "🔥 Kho hàng khô",
            type="primary" if st.session_state.tab_kho == "kho" else "secondary",
            use_container_width=True
        ):
            st.session_state.tab_kho = "kho"
            st.rerun()

    st.divider()

    if st.session_state.tab_kho == "tuoi":

        st.subheader("🟢 Kho hàng tươi")

        c1, c2 = st.columns(2)

        # ==========================
        # Khách hàng
        # ==========================
        with c1:

            ds_kh = lay_ds_khach_hang()

            options = [{"id": None, "ten": "Tất cả"}]
            options.extend(ds_kh)

            ten_kh = st.selectbox(
                "Khách hàng",
                [x["ten"] for x in options]
            )

            khach_hang_id = next(
                x["id"]
                for x in options
                if x["ten"] == ten_kh
            )

        # ==========================
        # Loại gỗ
        # ==========================
        with c2:

            ds_go = lay_ds_loai_go()

            options_go = [{"id": None, "ten_go": "Tất cả"}]
            options_go.extend(ds_go)

            ten_go = st.selectbox(
                "Loại gỗ",
                [x["ten_go"] for x in options_go]
            )

            loai_go_id = next(
                x["id"]
                for x in options_go
                if x["ten_go"] == ten_go
            )

        ds = lay_kho_tuoi(
            khach_hang_id,
            loai_go_id
        )

        if len(ds) == 0:
            st.info("Kho tươi đang trống.")
            return

        df = pd.DataFrame(ds)

        df.columns = [
            "ID",
            "Ngày nhập",
            "Số phiếu",
            "Khách hàng",
            "Tên gỗ",
            "Ký hiệu",
            "Dày",
            "Rộng",
            "Dài",
            "Kg",
            "Thanh",
            "M³"
        ]

        df.drop(columns=["ID"], inplace=True)

        df.insert(0, "STT", range(1, len(df) + 1))

        df["Ngày nhập"] = pd.to_datetime(
            df["Ngày nhập"]
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

        tong_kg = pd.to_numeric(
            df["Kg"].astype(str).str.replace(",", ""),
            errors="coerce"
        ).fillna(0).sum()

        tong_thanh = pd.to_numeric(
            df["Thanh"],
            errors="coerce"
        ).fillna(0).sum()

        tong_m3 = pd.to_numeric(
            df["M³"],
            errors="coerce"
        ).fillna(0).sum()

        df.loc[len(df)] = {
            "STT": "",
            "Ngày nhập": "",
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
        }
        pdf = tao_pdf_kho_tuoi(
            df,
            ten_kh,
            ten_go
        )

        # ===== Tạo Excel =====
        buffer = io.BytesIO()

        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(
                writer,
                index=False,
                sheet_name="Kho tươi"
            )

        buffer.seek(0)

        c1, c2 = st.columns(2)

        with c1:
            st.download_button(
                "📄 Xuất PDF",
                data=pdf,
                file_name="Kho_tuoi.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary"
            )

        with c2:
            st.download_button(
                "📊 Xuất Excel",
                data=buffer,
                file_name="Kho_tuoi.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                type="primary"
            )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )
        

    else:

        st.subheader("🔥 Kho hàng khô")

        c1, c2 = st.columns(2)

        with c1:

            ds_kh = lay_ds_khach_hang()

            options = [{"id": None, "ten": "Tất cả"}]
            options.extend(ds_kh)

            ten_kh = st.selectbox(
                "Khách hàng",
                [x["ten"] for x in options],
                key="kh_kho"
            )

            khach_hang_id = next(
                x["id"]
                for x in options
                if x["ten"] == ten_kh
            )

        with c2:

            ds_go = lay_ds_loai_go()

            options_go = [{"id": None, "ten_go": "Tất cả"}]
            options_go.extend(ds_go)

            ten_go = st.selectbox(
                "Loại gỗ",
                [x["ten_go"] for x in options_go],
                key="go_kho"
            )

            loai_go_id = next(
                x["id"]
                for x in options_go
                if x["ten_go"] == ten_go
            )

        ds = lay_kho_kho(
            khach_hang_id,
            loai_go_id
        )

        if len(ds) == 0:
            st.info("Kho khô đang trống.")
            return

        df = pd.DataFrame(ds)

        df.columns = [
            "ID",
            "Ngày nhập",
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
            "Ngày vào hầm",
            "Ngày ra hầm"
        ]

        df.drop(columns=["ID"], inplace=True)

        df.insert(0, "STT", range(1, len(df) + 1))

        df["Ngày nhập"] = pd.to_datetime(
            df["Ngày nhập"]
        ).dt.strftime("%d/%m/%Y")

        VN = ZoneInfo("Asia/Ho_Chi_Minh")

        ngay_vao = (
            pd.to_datetime(df["Ngày vào hầm"])
            .dt.tz_localize("UTC")
            .dt.tz_convert(VN)
        )

        ngay_ra = (
            pd.to_datetime(df["Ngày ra hầm"])
            .dt.tz_localize("UTC")
            .dt.tz_convert(VN)
        )

        df["Ngày vào hầm"] = ngay_vao.dt.strftime("%d/%m/%Y %H:%M")
        df["Ngày ra hầm"] = ngay_ra.dt.strftime("%d/%m/%Y %H:%M")

        for c in ["Dày", "Rộng", "Dài"]:
            df[c] = df[c].apply(
                lambda x: "" if pd.isna(x) else int(x)
            )

        df["Thanh"] = df["Thanh"].apply(
            lambda x: "" if pd.isna(x) else f"{int(x):,}"
        )

        df["Kg"] = df["Kg"].apply(
            lambda x: "" if pd.isna(x) else f"{x:,.0f}"
        )

        df["M³"] = df["M³"].apply(
            lambda x: "" if pd.isna(x) else f"{x:.3f}"
        )

        tong_kg = pd.to_numeric(
            df["Kg"].astype(str).str.replace(",", ""),
            errors="coerce"
        ).fillna(0).sum()

        tong_thanh = pd.to_numeric(
            df["Thanh"].astype(str).str.replace(",", ""),
            errors="coerce"
        ).fillna(0).sum()

        tong_m3 = pd.to_numeric(
            df["M³"],
            errors="coerce"
        ).fillna(0).sum()

        df.loc[len(df)] = {
            "STT": "",
            "Ngày nhập": "",
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
            "Ngày vào hầm": "",
            "Ngày ra hầm": ""
        }
        pdf = tao_pdf_kho_kho(
            df,
            ten_kh,
            ten_go
        )

        buffer = io.BytesIO()

        with pd.ExcelWriter(
            buffer,
            engine="openpyxl"
        ) as writer:

            df.to_excel(
                writer,
                index=False,
                sheet_name="Kho khô"
            )

        buffer.seek(0)

        c1, c2 = st.columns(2)

        with c1:
            st.download_button(
                "📄 Xuất PDF",
                data=pdf,
                file_name="Kho_kho.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary"
            )

        with c2:
            st.download_button(
                "📊 Xuất Excel",
                data=buffer,
                file_name="Kho_kho.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                type="primary"
            )
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )