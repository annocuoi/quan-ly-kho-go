import streamlit as st
import pandas as pd
from database.db import (
    lay_ds_phieu_nhap,
    lay_chi_tiet_phieu_nhap,
    lay_tong_nhap,
    lay_ds_khach_hang,
    lay_ds_ton_kho,
    lay_bao_cao_doanh_thu
)


def show():

    st.header("📊 Báo cáo")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📥 Nhận gỗ",
        "📤 Trả khách",
        "💰 Doanh thu",
        "👤 Công nợ",
        "📦 Tồn",
        "🔥 Hầm sấy"
    ])

    with tab1:
        c1, c2, c3 = st.columns(3)

        with c1:
            tu_ngay = st.date_input(
                "Từ ngày",
                key="tu_ngay_nhap"
            )

        with c2:
            den_ngay = st.date_input(
                "Đến ngày",
                key="den_ngay_nhap"
            )

        with c3:

            ds_kh = ["Tất cả"]

            ds_kh += [
                row["ten"]
                for row in lay_ds_khach_hang()
            ]

            chon_kh = st.selectbox(
                "Khách hàng",
                ds_kh,
                key="kh_nhap"
            )

        st.divider()
        tong = lay_tong_nhap()

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Số phiếu",
            tong["so_phieu"] or 0
        )

        c2.metric(
            "Tổng m³",
            round(tong["tong_m3"] or 0, 3)
        )

        c3.metric(
            "Tổng kg",
            round(tong["tong_kg"] or 0, 1)
        )

        c4.metric(
            "Tổng thanh",
            tong["tong_thanh"] or 0
        )

        st.divider()

        ds_phieu = lay_ds_phieu_nhap()

        if len(ds_phieu) == 0:

            st.info("Chưa có phiếu nhập.")

        else:

            ds_loc = []

            for phieu in ds_phieu:

                ngay = phieu["ngay"]

                if str(ngay) < str(tu_ngay):
                    continue

                if str(ngay) > str(den_ngay):
                    continue

                if (
                    chon_kh != "Tất cả"
                    and phieu["khach_hang"] != chon_kh
                ):
                    continue

                ds_loc.append(phieu)

            if len(ds_loc) == 0:

                st.info("Không có dữ liệu.")

            else:

                for phieu in ds_loc:

                    with st.expander(

                        f'📅 {phieu["ngay"]} | '
                        f'{phieu["khach_hang"]}'
                    ):

                        st.write(f'**Khách hàng:** {phieu["khach_hang"]}')

                        st.divider()

                        ds_ct = lay_chi_tiet_phieu_nhap(phieu["id"])

                        c1, c2, c3, c4, c5 = st.columns(
                            [2,4,2,2,2]
                        )

                        c1.write("Mã")

                        c2.write("Tên")

                        c3.write("Kiểu")

                        c4.write("Số thanh")

                        c5.write("Số lượng")

                        st.divider()

                        for dong in ds_ct:

                            c1, c2, c3, c4, c5 = st.columns(
                                [2,4,2,2,2]
                            )

                            c1.write(dong["ma_go"])

                            c2.write(dong["ten_go"])

                            if dong["kieu_tinh"] == "M3":

                                c3.write("📦 m³")

                            else:

                                c3.write("⚖️ Kg")

                            c4.write(dong["so_thanh"])

                            c5.write(dong["so_luong"])

    with tab5:

        tim = st.text_input(
            "🔍 Tìm mã hoặc tên gỗ"
        )

        st.divider()

        ds = lay_ds_ton_kho()

        if len(ds) == 0:

            st.info("Chưa có dữ liệu tồn kho.")

        else:

            du_lieu = []

            tong_thanh = 0
            tong_m3 = 0
            tong_kg = 0

            for dong in ds:

                if (
                    dong["so_thanh"] == 0
                    and dong["so_m3"] == 0
                    and dong["so_kg"] == 0
                ):
                    continue

                if tim != "":

                    txt = tim.lower()

                    if (
                        txt not in dong["ma_go"].lower()
                        and txt not in dong["ten_go"].lower()
                    ):
                        continue

                tong_thanh += dong["so_thanh"]
                tong_m3 += dong["so_m3"]
                tong_kg += dong["so_kg"]

                du_lieu.append({

                    "Mã": dong["ma_go"],

                    "Tên gỗ": dong["ten_go"],

                    "Kiểu": "m³" if dong["kieu_tinh"] == "M3" else "Kg",

                    "Số thanh": dong["so_thanh"],

                    "m³": round(dong["so_m3"],3),

                    "Kg": round(dong["so_kg"],1)

                })

            if len(du_lieu) == 0:

                st.info("Không có dữ liệu.")

            else:

                df = pd.DataFrame(du_lieu)

                st.dataframe(
                    df,
                    width="stretch",
                    hide_index=True,
                    height=450
                )

                st.divider()

                c1, c2, c3 = st.columns(3)

                c1.info(f"📦 Tổng thanh: {tong_thanh}")

                c2.info(f"📐 Tổng m³: {round(tong_m3,3)}")

                c3.info(f"⚖️ Tổng kg: {round(tong_kg,1)}")

    with tab3:

        c1, c2 = st.columns(2)

        with c1:
            tu_ngay = st.date_input(
                "Từ ngày",
                key="dt_tu_ngay",
                format="DD/MM/YYYY"
            )

        with c2:
            den_ngay = st.date_input(
                "Đến ngày",
                key="dt_den_ngay",
                format="DD/MM/YYYY"
            )

        st.divider()

        ds = lay_bao_cao_doanh_thu(
            str(tu_ngay),
            str(den_ngay)
        )

        if len(ds) == 0:
            st.info("Không có dữ liệu.")
        else:

            tong_dt = 0
            tong_thu = 0
            tong_no = 0

            du_lieu = []

            for row in ds:

                tong_dt += row["doanh_thu"]
                tong_thu += row["da_thu"]
                tong_no += row["con_no"]

                du_lieu.append({
                    "Khách hàng": row["ten"],
                    "Số lô": row["so_lo"],
                    "Doanh thu": f"{row['doanh_thu']:,.0f}".replace(",", ".") + " đ",
                    "Đã thu": f"{row['da_thu']:,.0f}".replace(",", ".") + " đ",
                    "Còn nợ": f"{row['con_no']:,.0f}".replace(",", ".") + " đ"
                })

            st.dataframe(
                pd.DataFrame(du_lieu),
                width="stretch",
                hide_index=True
            )

            st.divider()

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Doanh thu",
                f"{tong_dt:,.0f}".replace(",", ".") + " đ"
            )

            c2.metric(
                "Đã thu",
                f"{tong_thu:,.0f}".replace(",", ".") + " đ"
            )

            c3.metric(
                "Còn nợ",
                f"{tong_no:,.0f}".replace(",", ".") + " đ"
            )
    with tab4:

        st.info("Đang phát triển...")

    with tab2:

        st.info("Đang phát triển...")

    with tab6:

        st.info("Đang phát triển...")