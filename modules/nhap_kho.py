import streamlit as st

from database.db import (
    lay_ds_loai_go,
    lay_ds_khach_hang,
    them_phieu_nhap,
    them_chi_tiet_phieu_nhap,
    cap_nhat_ton_kho
)

def show():

    if "phieu_nhap_tam" not in st.session_state:
        st.session_state.phieu_nhap_tam = []

    if "dong_sua" not in st.session_state:
        st.session_state.dong_sua = None

    st.header("📥 Nhận gỗ")

    st.subheader("Thông tin phiếu")

    c1, c2 = st.columns(2)

    with c1:
        ngay = st.date_input("Ngày nhập")

    with c2:

        ds_kh = lay_ds_khach_hang()
        if len(ds_kh) == 0:

            st.warning("Chưa có Khách hàng.")

            st.stop()

        ds_ten_kh = [row["ten"] for row in ds_kh]

        ten_kh = st.selectbox(
            "Khách hàng",
            ds_ten_kh
        )

        khach_hang = next(
            row
            for row in ds_kh
            if row["ten"] == ten_kh
        )

    st.divider()

    st.subheader("Chi tiết nhập")

    ds_go = lay_ds_loai_go()
    if len(ds_go) == 0:

        st.warning("Chưa có loại gỗ.")

        st.stop()

    ds_ten_go = [
        f'{row["ma_go"]} - {row["ten_go"]}'
        for row in ds_go
    ]

    vi_tri = 0
    don_gia_mac_dinh = 0.0

    if st.session_state.dong_sua is not None:

        dong = st.session_state.phieu_nhap_tam[
            st.session_state.dong_sua
        ]

        ten_day_du = f'{dong["ma"]} - {dong["ten"]}'

        for idx, item in enumerate(ds_ten_go):
            if item == ten_day_du:
                vi_tri = idx
                break

        don_gia_mac_dinh = dong["don_gia"]

    ten_go = st.selectbox(
        "Loại gỗ",
        ds_ten_go,
        index=vi_tri
    )
    don_gia = st.number_input(
        "Đơn giá sấy",
        min_value=0.0,
        value=don_gia_mac_dinh,
        step=1000.0,
        format="%.0f"
    )

    loai_go = next(
        row
        for row in ds_go
        if f'{row["ma_go"]} - {row["ten_go"]}' == ten_go
    )
    if loai_go["kieu_tinh"] == "M3":

        st.info(
            f'📦 Quy cách: '
            f'{int(loai_go["day"])} × '
            f'{int(loai_go["rong"])} × '
            f'{int(loai_go["dai"])}'
        )

        so_thanh_mac_dinh = 1

        if st.session_state.dong_sua is not None:
            so_thanh_mac_dinh = int(dong["so_thanh"])

        so_thanh = st.number_input(
            "Số thanh",
            min_value=1,
            value=so_thanh_mac_dinh,
            step=1
        )

    else:

        trong_luong_mac_dinh = 0.0

        if (
            st.session_state.dong_sua is not None
            and dong["kieu"] == "TRONG_LUONG"
        ):
            trong_luong_mac_dinh = dong["so_luong"]

        trong_luong = st.number_input(
            "Trọng lượng (kg)",
            min_value=0.0,
            value=trong_luong_mac_dinh,
            step=1.0
        )

    st.divider()


    ten_nut = "💾 Cập nhật" if st.session_state.dong_sua is not None else "➕ Thêm vào phiếu"

    if st.button(
        ten_nut,
        width="stretch"
    ):

        if loai_go["kieu_tinh"] == "M3":

            khoi = (
                loai_go["day"]
                * loai_go["rong"]
                * loai_go["dai"]
                * so_thanh
            ) / 1000000000

            thanh_tien = khoi * don_gia

            data = {

                "ma": loai_go["ma_go"],
                "ten": loai_go["ten_go"],
                "kieu": "M3",
                "so_thanh": so_thanh,
                "so_luong": round(khoi, 4),
                "don_gia": don_gia,
                "thanh_tien": thanh_tien

            }

            if st.session_state.dong_sua is None:
                st.session_state.phieu_nhap_tam.append(data)
            else:
                st.session_state.phieu_nhap_tam[
                    st.session_state.dong_sua
                ] = data

                st.session_state.dong_sua = None

        else:

            thanh_tien = trong_luong * don_gia

            data = {

                "ma": loai_go["ma_go"],
                "ten": loai_go["ten_go"],
                "kieu": "TRONG_LUONG",
                "so_thanh": "",
                "so_luong": trong_luong,
                "don_gia": don_gia,
                "thanh_tien": thanh_tien

            }

            if st.session_state.dong_sua is None:
                st.session_state.phieu_nhap_tam.append(data)
            else:
                st.session_state.phieu_nhap_tam[
                    st.session_state.dong_sua
                ] = data

                st.session_state.dong_sua = None

        st.rerun()

    if st.session_state.dong_sua is not None:

        if st.button(
            "❌ Hủy sửa",
            width="stretch"
        ):

            st.session_state.dong_sua = None

            st.rerun()
    st.divider()

    st.subheader("Danh sách đang nhập")

    if len(st.session_state.phieu_nhap_tam) == 0:

        st.info("Chưa có dòng nào.")

    else:

        c1, c2, c3, c4, c5, c6, c7, c8, c9, c10 = st.columns(
            [1,2,4,2,2,2,2,2,1,1]
        )

        c1.write("STT")
        c2.write("Mã")
        c3.write("Tên")
        c4.write("Kiểu")
        c5.write("Số thanh")
        c6.write("Số lượng")
        c7.write("Đơn giá")
        c8.write("Thành tiền")
        c9.write("Sửa")
        c10.write("Xóa")

        st.divider()

        for i, dong in enumerate(
            st.session_state.phieu_nhap_tam,
            start=1
        ):

            c1, c2, c3, c4, c5, c6, c7, c8, c9, c10 = st.columns(
                [1,2,4,2,2,2,2,2,1,1]
            )

            c1.write(i)

            c2.write(dong["ma"])

            c3.write(dong["ten"])

            if dong["kieu"] == "M3":
                c4.write("📦 m³")
            else:
                c4.write("⚖️ Kg")

            c5.write(dong["so_thanh"])

            c6.write(dong["so_luong"])

            c7.write(f"{dong['don_gia']:,.0f}")

            c8.write(f"{dong['thanh_tien']:,.0f}")

            if c9.button("✏️", key=f"sua_{i}"):

                st.session_state.dong_sua = i - 1

                st.rerun()

            if c10.button("🗑️", key=f"xoa_{i}"):

                st.session_state.phieu_nhap_tam.pop(i - 1)

                st.rerun()
    st.divider()

    if st.button(
        "🧹 Xóa tất cả",
        width="stretch"
    ):

        st.session_state.phieu_nhap_tam.clear()

        st.rerun()
    
    st.divider()

    if st.button(
        "💾 Lưu phiếu",
        width="stretch",
        type="primary",
        key="luu_phieu"
    ):
        # 1. Kiểm tra dữ liệu trước khi lưu
        if len(st.session_state.phieu_nhap_tam) == 0:
            st.warning("Chưa có dữ liệu để lưu.")
        else:
            # 2. Thực hiện các thao tác lưu vào Database
            try:
                id_phieu = them_phieu_nhap(str(ngay), khach_hang["id"])

                for dong in st.session_state.phieu_nhap_tam:
                    loai = next(
                        row for row in ds_go if row["ma_go"] == dong["ma"]
                    )

                    them_chi_tiet_phieu_nhap(
                        id_phieu,
                        loai["id"],
                        dong["so_thanh"] if dong["so_thanh"] != "" else 0,
                        dong["so_luong"],
                        dong["don_gia"],
                        dong["thanh_tien"]
                    )

                    if loai["kieu_tinh"] == "M3":
                        cap_nhat_ton_kho(
                            loai["id"], dong["so_thanh"], dong["so_luong"], 0
                        )
                    else:
                        cap_nhat_ton_kho(
                            loai["id"], 0, 0, dong["so_luong"]
                        )
                
                # 3. Sau khi lưu xong thì xóa danh sách tạm và báo thành công
                st.session_state.phieu_nhap_tam.clear()
                st.success("Đã lưu phiếu nhập.")
                
                # 4. Quan trọng: Dùng st.rerun() để làm mới giao diện ngay lập tức
                st.rerun()
                
            except Exception as e:
                st.error(f"Đã có lỗi xảy ra: {e}")
