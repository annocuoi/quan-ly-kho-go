import streamlit as st

from database.db import (
    lay_ds_loai_go,
    lay_ds_ten_go,
    lay_ds_quy_cach,
    them_loai_go,
    sua_loai_go,
    xoa_loai_go
)


@st.dialog("➕ Thêm loại gỗ")
def them_dialog():

    ten = st.text_input("Tên gỗ")

    kieu_hien_thi = st.selectbox(
        "Kiểu tính",
        [
            "📦 Tính theo khối (m³)",
            "⚖️ Tính theo trọng lượng"
        ]
    )

    kieu_tinh = (
        "M3"
        if kieu_hien_thi == "📦 Tính theo khối (m³)"
        else "TRONG_LUONG"
    )

    day = None
    rong = None
    dai = None

    if kieu_tinh == "M3":

        c1, c2, c3 = st.columns(3)

        with c1:
            day = st.number_input("Dày (mm)", min_value=0.0)

        with c2:
            rong = st.number_input("Rộng (mm)", min_value=0.0)

        with c3:
            dai = st.number_input("Dài (mm)", min_value=0.0)

    if st.button("💾 Lưu", width="stretch"):

        if ten.strip() == "":
            st.warning("Chưa nhập tên gỗ")
            return

        if kieu_tinh == "M3":

            if day <= 0:
                st.warning("Chưa nhập độ dày")
                return

            if rong <= 0:
                st.warning("Chưa nhập độ rộng")
                return

            if dai <= 0:
                st.warning("Chưa nhập chiều dài")
                return

        them_loai_go(
            ten.strip(),
            kieu_tinh,
            day,
            rong,
            dai
        )

        st.success("Đã thêm thành công")
        st.rerun()

@st.dialog("Sửa loại gỗ")
def sua_dialog(row):

    ten = st.text_input(
        "Tên gỗ",
        value=row["ten"]
    )

    kieu_hien_thi = st.selectbox(
        "Kiểu tính",
        [
            "📦 Tính theo khối (m³)",
            "⚖️ Tính theo trọng lượng"
        ],
        index=0 if row["kieu_tinh"] == "M3" else 1
    )

    kieu_tinh = (
        "M3"
        if kieu_hien_thi == "📦 Tính theo khối (m³)"
        else "TRONG_LUONG"
    )

    day = row["day"]
    rong = row["rong"]
    dai = row["dai"]

    if kieu_tinh == "M3":

        c1, c2, c3 = st.columns(3)

        with c1:
            day = st.number_input(
                "Dày (mm)",
                value=float(row["day"] or 0)
            )

        with c2:
            rong = st.number_input(
                "Rộng (mm)",
                value=float(row["rong"] or 0)
            )

        with c3:
            dai = st.number_input(
                "Dài (mm)",
                value=float(row["dai"] or 0)
            )

    if st.button("💾 Cập nhật", width="stretch"):

        if ten.strip() == "":
            st.warning("Chưa nhập tên gỗ")
            return

        sua_loai_go(
            row["id"],
            ten.strip(),
            kieu_tinh,
            day,
            rong,
            dai
        )

        st.success("Đã cập nhật")
        st.rerun()

def show():

    st.header("🪵 Danh mục loại gỗ")

    if st.button("➕ Thêm loại gỗ", width="stretch"):
        them_dialog()

    st.divider()

    c1, c2 = st.columns(2)

    with c1:

        ds_ten = lay_ds_ten_go()

        options = [{"ten": "Tất cả"}]
        options.extend(ds_ten)

        ten_go = st.selectbox(
            "Tên gỗ",
            [x["ten"] for x in options]
        )

    with c2:

        loai_go_id = None

        if ten_go == "Tất cả":

            st.selectbox(
                "Quy cách",
                ["Tất cả"],
                disabled=True
            )

        else:

            ds_qc = lay_ds_quy_cach(ten_go)

            if len(ds_qc) == 0:

                st.selectbox(
                    "Quy cách",
                    ["Không có"],
                    disabled=True
                )

            else:

                options_qc = [{"id": None, "ten": "Tất cả"}]

                for x in ds_qc:

                    options_qc.append({
                        "id": x["id"],
                        "ten": f"{int(x['day'])} × {int(x['rong'])} × {int(x['dai'])}"
                    })

                ten_qc = st.selectbox(
                    "Quy cách",
                    [x["ten"] for x in options_qc]
                )

                loai_go_id = next(
                    x["id"]
                    for x in options_qc
                    if x["ten"] == ten_qc
                )

    ds = lay_ds_loai_go(
        None if ten_go == "Tất cả" else ten_go,
        loai_go_id
    )

    st.subheader("Danh sách")

    if len(ds) == 0:
        st.info("Chưa có dữ liệu.")
        return

    cot1, cot2, cot3, cot4, cot5, cot6 = st.columns(
    [1, 4, 2, 3, 1, 1]
    )

    cot1.write("STT")
    cot2.write("Tên")
    cot3.write("Kiểu")
    cot4.write("Quy cách")
    cot5.write("Sửa")
    cot6.write("Xóa")

    st.divider()

    for i, row in enumerate(ds, start=1):

        c1, c2, c3, c4, c5, c6 = st.columns(
            [1, 4, 2, 3, 1, 1]
        )

        c1.write(i)

        c2.write(row["ten"])

        c3.write(
            "📦 Khối (m³)"
            if row["kieu_tinh"] == "M3"
            else "⚖️ Trọng lượng"
        )

        if row["kieu_tinh"] == "M3":
            quy_cach = (
                f'{int(row["day"])} × '
                f'{int(row["rong"])} × '
                f'{int(row["dai"])}'
            )
        else:
            quy_cach = "-"

        c4.write(quy_cach)

        if c5.button("✏️", key=f"sua_{row['id']}"):
            sua_dialog(row)

        if c6.button("🗑️", key=f"xoa_{row['id']}"):

            xoa_loai_go(row["id"])

            st.success("Đã xóa thành công")

            st.rerun()