import streamlit as st
import pandas as pd

from database.db import (
    lay_so_phieu_xuat_moi,
    lay_ds_khach_hang,
    lay_kho_da_phan_loai,
    luu_phieu_xuat,
    lay_ds_phieu_xuat,
    lay_chi_tiet_phieu_xuat
)


def show():

    st.header("🚚 Xuất hàng")

    if "ds_xuat" not in st.session_state:
        st.session_state.ds_xuat = []

    tab1, tab2 = st.tabs([
        "📝 Lập phiếu xuất",
        "📜 Lịch sử xuất"
    ])

    with tab1:

        col1, col2 = st.columns(2)

        with col1:
            so_phieu = lay_so_phieu_xuat_moi()

            st.text_input(
                "Số phiếu",
                value=so_phieu,
                disabled=True
            )

        with col2:
            ngay = st.date_input(
                "Ngày xuất"
            )

        ds_kh = lay_ds_khach_hang()

        kh = st.selectbox(
            "Khách hàng",
            ds_kh,
            format_func=lambda x: x["ten"]
        )
        # Khóa danh sách xuất theo khách hàng
        if "kh_xuat" not in st.session_state:
            st.session_state.kh_xuat = kh["id"]

        if st.session_state.kh_xuat != kh["id"]:

            st.session_state.kh_xuat = kh["id"]
            st.session_state.ds_xuat = []

            st.rerun()

        ghi_chu = st.text_area("Ghi chú")
        st.divider()

        st.subheader("📦 Kho đã phân loại")

        ds_kho = lay_kho_da_phan_loai(
            khach_hang_id=kh["id"]
        )

        if ds_kho:

            df = pd.DataFrame(ds_kho)

            df["Nguồn"] = df["loai_nhap"].map({
                "TUOI": "🌲 Gia công",
                "KHO": "📦 Hàng mua"
            })

            df = df.rename(columns={
                "ten": "Loại gỗ",
                "phan_loai": "Phân loại",
                "day": "Dày",
                "rong": "Rộng",
                "dai": "Dài",
                "thanh": "Thanh",
                "m3": "m³",
                "kg": "Kg"
            })
            df = df.fillna("")

            st.dataframe(
                df[
                    [
                        "Nguồn",
                        "Loại gỗ",
                        "Phân loại",
                        "Dày",
                        "Rộng",
                        "Dài",
                        "Thanh",
                        "m³",
                        "Kg"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )
            lo = st.selectbox(
                "Lô gỗ",
                ds_kho,
                key="lo_xuat",
                format_func=lambda x: (
                    f'{"📦 Hàng mua" if x["loai_nhap"]=="KHO" else "🌲 Gia công"} | '
                    f'{x["ten"]} | {x["phan_loai"]} | '
                    f'{int(x["day"])}x{int(x["rong"])}x{int(x["dai"])}'
                    if x["kieu_tinh"] == "M3"
                    else
                    f'{"📦 Hàng mua" if x["loai_nhap"]=="KHO" else "🌲 Gia công"} | '
                    f'{x["ten"]} | {x["phan_loai"]} | Kg'
                )
            )
            # Số lượng đã chọn xuất của lô này
            thanh_da_chon = 0
            m3_da_chon = 0.0

            for item in st.session_state.ds_xuat:

                if item["kho_phan_loai_id"] == lo["kho_phan_loai_id"]:

                    thanh_da_chon = item["so_thanh"]
                    m3_da_chon = item["so_luong"]
                    break

            if lo["kieu_tinh"] == "M3":
                thanh_con = lo["thanh"] - thanh_da_chon
                m3_con = lo["m3"] - m3_da_chon
            else:
                thanh_con = 0
                m3_con = 0

            col1, col2 = st.columns(2)

            with col1:
                if lo["kieu_tinh"] == "M3":
                    st.metric(
                        "Thanh còn",
                        int(thanh_con)
                    )                                 
                else:
                    st.metric(
                        "Kg còn",
                        round(lo["kg"], 3)
                    )

            with col2:
                if lo["kieu_tinh"] == "M3":
                    st.metric(
                        "m³ còn",
                        round(m3_con, 3)
                    )

            st.divider()
            co_the_them = True

            if lo["kieu_tinh"] == "M3":

                if thanh_con <= 0:

                    st.warning("Lô này đã hết.")
                    co_the_them = False

                else:

                    so_thanh = st.number_input(
                        "Số thanh xuất",
                        min_value=1,
                        max_value=int(thanh_con),
                        value=1,
                        step=1
                    )

                    so_luong = (
                        float(lo["m3"])
                        * so_thanh
                        / float(lo["thanh"])
                    )

            else:

                if lo["kg"] <= 0:

                    st.warning("Lô này đã hết.")
                    co_the_them = False

                else:

                    so_thanh = 0

                    so_luong = st.number_input(
                        "Kg xuất",
                        min_value=0.0,
                        max_value=float(lo["kg"]),
                        value=0.0,
                        step=1.0
                    )
            
            if lo["loai_nhap"] == "KHO":

                don_gia_ban = st.number_input(
                    "Đơn giá bán",
                    min_value=0.0,
                    value=float(lo["don_gia"]),
                    step=1000.0
                )

            else:

                don_gia_ban = 0

            if co_the_them and st.button(
                "➕ Thêm vào phiếu",
                use_container_width=True
            ):

                da_co = False

                for item in st.session_state.ds_xuat:

                    if item["kho_phan_loai_id"] != lo["kho_phan_loai_id"]:
                        continue

                    if lo["kieu_tinh"] == "M3":

                        thanh_moi = item["so_thanh"] + so_thanh

                        if thanh_moi > lo["thanh"]:
                            st.error("Xuất vượt số thanh còn.")
                            st.stop()

                        item["so_thanh"] = thanh_moi

                        item["so_luong"] = (
                            float(lo["m3"])
                            * item["so_thanh"]
                            / float(lo["thanh"])
                        )

                    else:

                        kg_moi = item["so_luong"] + so_luong

                        if kg_moi > lo["kg"]:
                            st.error("Xuất vượt số kg còn.")
                            st.stop()

                        item["so_luong"] = kg_moi
    
                    if lo["loai_nhap"] == "KHO":
                        item["don_gia_ban"] = don_gia_ban
                        item["thanh_tien"] = item["so_luong"] * don_gia_ban

                    da_co = True
                    break
                
                if not da_co:

                    item = {

                        "kho_phan_loai_id": lo["kho_phan_loai_id"],

                        "ten": lo["ten"],

                        "phan_loai": lo["phan_loai"],

                        "day": lo["day"],

                        "rong": lo["rong"],

                        "dai": lo["dai"],

                        "so_thanh": so_thanh,

                        "so_luong": so_luong,

                        "loai_nhap": lo["loai_nhap"]

                    }

                    if lo["loai_nhap"] == "KHO":

                        item["don_gia_ban"] = don_gia_ban

                        if lo["kieu_tinh"] == "M3":
                            item["thanh_tien"] = so_luong * don_gia_ban
                        else:
                            item["thanh_tien"] = so_luong * don_gia_ban
                    st.session_state.ds_xuat.append(item)

                st.rerun()
        
            st.divider()

            st.subheader("📋 Các mặt hàng sẽ xuất")

            if st.session_state.ds_xuat:

                for i, item in enumerate(st.session_state.ds_xuat):

                    c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(
                        [3,2,1,1,1,1.2,1.2,0.8]
                    )

                    with c1:
                        st.write(item["ten"])

                    with c2:
                        st.write(item["phan_loai"])

                    with c3:
                        if item["day"] is not None:
                            st.write(
                                f'{int(item["day"])}x{int(item["rong"])}x{int(item["dai"])}'
                            )
                        else:
                            st.write("Kg")

                    with c4:
                        if item["day"] is not None:
                            st.write(f'{item["so_thanh"]} thanh')
                        else:
                            st.write("-")

                    with c5:
                        if item["day"] is not None:
                            st.write(f'{item["so_luong"]:.3f} m³')
                        else:
                            st.write(f'{item["so_luong"]:.3f} kg')

                    with c6:

                        if item["loai_nhap"] == "KHO":
                            st.write(f'{item["don_gia_ban"]:,.0f}')
                        else:
                            st.write("-")

                    with c7:

                        if item["loai_nhap"] == "KHO":
                            st.write(f'{item["thanh_tien"]:,.0f}')
                        else:
                            st.write("-")

                    with c8:

                        if st.button(
                            "❌",
                            key=f"xoa_{i}",
                            use_container_width=True
                        ):

                            st.session_state.ds_xuat.pop(i)

                            st.rerun()

            else:

                st.info("Chưa có mặt hàng nào.")

            if st.session_state.ds_xuat:

                col1, col2 = st.columns(2)

                with col1:

                    if st.button(
                        "💾 Lưu phiếu xuất",
                        use_container_width=True,
                        type="primary"
                    ):

                        try:

                            luu_phieu_xuat(

                                so_phieu=so_phieu,

                                ngay=ngay,

                                khach_hang_id=kh["id"],

                                ghi_chu=ghi_chu,

                                ds_hang=st.session_state.ds_xuat

                            )

                            st.session_state.ds_xuat = []
                            # Xóa lựa chọn lô
                            if "lo_xuat" in st.session_state:
                                del st.session_state["lo_xuat"]

                            st.success("Đã lưu phiếu xuất.")

                            st.rerun()

                        except Exception as e:

                            st.error(str(e))

                with col2:

                    if st.button(
                        "🗑 Xóa danh sách",
                        use_container_width=True
                    ):

                        st.session_state.ds_xuat = []

                        st.rerun()
        

        else:

            st.info("Khách hàng chưa có hàng trong kho đã phân loại.")

    with tab2:

        st.header("🚚 Lịch sử xuất")

        ds = lay_ds_phieu_xuat()

        if len(ds) == 0:

            st.info("Chưa có phiếu xuất.")

        else:

            c1, c2, c3, c4, c5, c6, c7 = st.columns(
                [1, 2, 4, 2, 1, 1, 1]
            )

            c1.write("Số phiếu")
            c2.write("Ngày xuất")
            c3.write("Khách hàng")
            c4.write("Mặt hàng")
            c5.write("👁")
            c6.write("✏️")
            c7.write("🗑")

            st.divider()

            for row in ds:

                c1, c2, c3, c4, c5, c6, c7 = st.columns(
                    [1, 2, 4, 2, 1, 1, 1]
                )

                c1.write(row["so_phieu"])
                c2.write(row["ngay"].strftime("%d/%m/%Y"))
                c3.write(row["khach_hang"])
                c4.write(row["so_mat_hang"])

                if c5.button(
                    "👁",
                    key=f"xem_xuat_{row['id']}"
                ):
                    st.session_state.xem_phieu_xuat = row["id"]
                    st.rerun()

                if c6.button(
                    "✏️",
                    key=f"sua_xuat_{row['id']}"
                ):
                    st.session_state.sua_phieu_xuat = row["id"]
                    st.info("Chức năng sửa sẽ làm tiếp.")

                if c7.button(
                    "🗑",
                    key=f"xoa_xuat_{row['id']}"
                ):
                    st.warning("Chưa làm chức năng xóa.")
            if "xem_phieu_xuat" in st.session_state:

                ct = lay_chi_tiet_phieu_xuat(
                    st.session_state.xem_phieu_xuat
                )

                st.subheader("📦 Chi tiết phiếu xuất")

                df = pd.DataFrame(ct)

                df = df.rename(columns={
                    "id": "Mã",
                    "ten": "Tên gỗ",
                    "kieu_tinh": "Kiểu tính",
                    "day": "Dày",
                    "rong": "Rộng",
                    "dai": "Dài",
                    "phan_loai": "Phân loại",
                    "so_thanh": "Số thanh",
                    "kg": "Kg",
                    "m3": "m³",
                    "don_gia_ban": "Đơn giá",
                    "thanh_tien": "Thành tiền"
                })

                tong = {
                    "Mã": "",
                    "Tên gỗ": "TỔNG CỘNG",
                    "Kiểu tính": "",
                    "Dày": "",
                    "Rộng": "",
                    "Dài": "",
                    "Phân loại": "",
                    "Số thanh": df["Số thanh"].fillna(0).sum(),
                    "Kg": df["Kg"].fillna(0).sum(),
                    "m³": df["m³"].fillna(0).sum(),
                    "Đơn giá": "",
                    "Thành tiền": df["Thành tiền"].fillna(0).sum()
                }

                df.loc[len(df)] = tong

                df = df.fillna("")

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

                if st.button("Đóng"):

                    del st.session_state["xem_phieu_xuat"]

                    st.rerun()