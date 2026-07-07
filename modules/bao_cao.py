import streamlit as st
import pandas as pd
import io

from datetime import date
from utils.pdf_bao_cao import tao_pdf_bao_cao

from database.db import (
    lay_ds_khach_hang,
    lay_bao_cao_nhap,
    lay_ds_loai_go,
    lay_lich_su_ham
)


def show():

    st.header("📊 Báo cáo")

    tab_nhap, tab_ham = st.tabs([
        "📥 Nhập hàng",
        "🔥 Lịch sử hầm sấy"
    ])

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

        if xem:
            

            ds = lay_bao_cao_nhap(
                tu_ngay,
                den_ngay,
                khach_hang_id
            )

            if not ds:
                st.warning("Không có dữ liệu.")
            else:
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

    with tab_ham:

        st.subheader("🔥 Lịch sử hầm sấy")

        # =========================
        # Hàng 1
        # =========================

        c1, c2 = st.columns(2)

        with c1:
            tu_ngay = st.date_input(
                "Từ ngày",
                value=date.today(),
                key="ham_tu_ngay"
            )

        with c2:
            den_ngay = st.date_input(
                "Đến ngày",
                value=date.today(),
                key="ham_den_ngay"
            )

        # =========================
        # Hàng 2
        # =========================

        c1, c2, c3, c4 = st.columns([3, 3, 2, 1])

        with c1:

            ds_kh = lay_ds_khach_hang()

            options = [{"id": None, "ten": "Tất cả"}]
            options.extend(ds_kh)

            ten_kh = st.selectbox(
                "Khách hàng",
                [x["ten"] for x in options],
                key="ham_khach_hang"
            )

            khach_hang_id = next(
                x["id"]
                for x in options
                if x["ten"] == ten_kh
            )

        with c2:

            ds_go = lay_ds_loai_go()

            options = [{"id": None, "ten_go": "Tất cả"}]
            options.extend(ds_go)

            ten_go = st.selectbox(
                "Loại gỗ",
                [x["ten_go"] for x in options],
                key="ham_loai_go"
            )

            loai_go_id = next(
                x["id"]
                for x in options
                if x["ten_go"] == ten_go
            )

        with c3:

            thao_tac = st.selectbox(
                "Thao tác",
                [
                    "Tất cả",
                    "VAO_HAM",
                    "RA_HAM",
                    "THU_HOI"
                ],
                format_func=lambda x: {
                    "Tất cả": "Tất cả",
                    "VAO_HAM": "Đưa vào hầm",
                    "RA_HAM": "Ra hầm",
                    "THU_HOI": "Thu hồi"
                }[x],
                key="ham_thao_tac"
            )

        with c4:

            st.write("")
            st.write("")

            xem = st.button(
                "🔍 Xem",
                use_container_width=True,
                key="xem_lich_su_ham"
            )

        st.divider()

        if xem:

            ds = lay_lich_su_ham(
                tu_ngay,
                den_ngay,
                khach_hang_id,
                loai_go_id,
                thao_tac
            )

            if not ds:
                st.info("Không có dữ liệu.")

            else:

                df = pd.DataFrame(ds)

                # =========================
                # Giờ Việt
                # =========================

                df["ngay"] = (
                    pd.to_datetime(df["ngay"], utc=True)
                    .dt.tz_convert("Asia/Ho_Chi_Minh")
                    .dt.strftime("%d/%m/%Y %H:%M")
                )

                # =========================
                # Tính Kg và M3
                # =========================

                kg = []
                m3 = []

                for _, row in df.iterrows():

                    if row["loai_hang"] == "KG":
                        kg.append(row["so_luong"])
                        m3.append(None)
                    else:
                        kg.append(None)
                        m3.append(row["so_luong"])

                df["Kg"] = kg
                df["M³"] = m3

                # =========================
                # Tính tổng (trước khi format)
                # =========================

                tong_kg = df["Kg"].fillna(0).sum()
                tong_thanh = df["so_thanh"].fillna(0).sum()
                tong_m3 = df["M³"].fillna(0).sum()

                # =========================
                # Đổi tên cột
                # =========================

                df.rename(columns={
                    "ngay": "Thời gian",
                    "so_ham": "Hầm",
                    "so_phieu": "Phiếu",
                    "ten": "Khách hàng",
                    "ten_go": "Loại gỗ",
                    "hanh_dong": "Thao tác",
                    "so_thanh": "Thanh"
                }, inplace=True)

                # =========================
                # Format
                # =========================

                df["Kg"] = df["Kg"].apply(
                    lambda x: "" if pd.isna(x) else f"{x:,.0f}"
                )

                df["Thanh"] = df["Thanh"].apply(
                    lambda x: "" if pd.isna(x) else int(x)
                )

                df["M³"] = df["M³"].apply(
                    lambda x: "" if pd.isna(x) else f"{x:.3f}"
                )

                # =========================
                # Xóa cột dư
                # =========================

                df.drop(
                    columns=[
                        "so_luong",
                        "loai_hang"
                    ],
                    inplace=True
                )

                df.insert(0, "STT", range(1, len(df) + 1))

                # =========================
                # Tổng cộng
                # =========================

                df.loc[len(df)] = {
                    "STT": "TỔNG CỘNG",
                    "Thời gian": "",
                    "Hầm": "",
                    "Phiếu": "",
                    "Khách hàng": "",
                    "Loại gỗ": "",
                    "Thao tác": "",
                    "Kg": f"{tong_kg:,.0f}" if tong_kg else "",
                    "Thanh": f"{tong_thanh:,.0f}" if tong_thanh else "",
                    "M³": f"{tong_m3:.3f}" if tong_m3 else ""
                }

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )