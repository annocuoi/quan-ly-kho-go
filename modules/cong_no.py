import streamlit as st

from database.db import (
    lay_no_phai_thu,
    lay_no_phai_tra,
    lay_tong_hop_cong_no,
    them_thanh_toan,
    lay_ds_thanh_toan,
    lay_chi_tiet_cong_no
)


@st.dialog("📄 Chi tiết phiếu", width="large")
def dialog_chi_tiet(cong_no_id):

    phieu = lay_chi_tiet_cong_no(cong_no_id)
    ds = lay_ds_thanh_toan(cong_no_id)

    st.write(f"**Số phiếu:** {phieu['so_phieu']}")
    st.write(f"**Khách hàng:** {phieu['khach_hang']}")
    st.write(f"**Ngày:** {phieu['ngay'].strftime('%d/%m/%Y')}")
    st.write(f"**Tổng tiền:** {phieu['so_tien']:,.0f}")
    st.write(f"**Đã thanh toán:** {phieu['da_thanh_toan']:,.0f}")
    st.write(f"**Còn lại:** {phieu['con_lai']:,.0f}")

    st.divider()

    if not ds:
        st.info("Phiếu này chưa có lần thanh toán nào.")
        return

    c1, c2, c3, c4 = st.columns([1,2,2,5])

    c1.write("**STT**")
    c2.write("**Ngày**")
    c3.write("**Số tiền**")
    c4.write("**Ghi chú**")

    st.divider()

    tong = 0

    for i, row in enumerate(ds, start=1):

        tong += row["so_tien"]

        c1, c2, c3, c4 = st.columns([1,2,2,5])

        c1.write(i)

        c2.write(
            row["ngay"].strftime("%d/%m/%Y")
        )

        c3.write(
            f"{row['so_tien']:,.0f}"
        )

        c4.write(
            row["ghi_chu"] or ""
        )

    st.divider()

    st.metric(
        "Đã thanh toán",
        f"{tong:,.0f}"
    )


@st.dialog("💵 Thanh toán")
def dialog_thanh_toan(cong_no_id, loai):

    phieu = lay_chi_tiet_cong_no(cong_no_id)

    if loai == "THU":
        st.subheader("💵 Thu tiền")
    else:
        st.subheader("💸 Trả tiền")
        
    st.write(f"Phiếu: {cong_no_id}")
    st.write(f"**Số phiếu:** {phieu['so_phieu']}")
    st.write(f"**Khách hàng:** {phieu['khach_hang']}")
    st.write(f"**Còn lại:** {phieu['con_lai']:,.0f}")

    st.divider()

    ngay = st.date_input("Ngày")

    so_tien = st.number_input(
        "Số tiền",
        min_value=0.0,
        step=1000.0,
        format="%.0f"
    )

    ghi_chu = st.text_input("Ghi chú")

    if st.button("💾 Lưu", use_container_width=True):
        
        if so_tien <= 0:
            st.warning("Nhập số tiền lớn hơn 0.")
            st.stop()

        them_thanh_toan(
            cong_no_id=cong_no_id,
            ngay=str(ngay),
            so_tien=so_tien,
            ghi_chu=ghi_chu
        )

        st.success("Đã lưu.")
        st.rerun()


def tab_no_phai_thu():

    st.subheader("📥 Nợ phải thu")

    ds = lay_no_phai_thu()

    if not ds:
        st.info("Không có dữ liệu.")
        return

    c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns(
        [1, 2, 2, 3, 2, 2, 2, 1, 1]
    )

    c1.write("**STT**")
    c2.write("**Phiếu**")
    c3.write("**Ngày**")
    c4.write("**Khách hàng**")
    c5.write("**Phải thu**")
    c6.write("**Đã thu**")
    c7.write("**Còn lại**")
    c8.write("👁")
    c9.write("💵")

    st.divider()

    tong_phai_thu = 0
    tong_con_lai = 0

    for i, row in enumerate(ds, start=1):

        tong_phai_thu += row["so_tien"]
        tong_con_lai += row["con_lai"]

        c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns(
            [1, 2, 2, 3, 2, 2, 2, 1, 1]
        )

        c1.write(i)

        c2.write(row["so_phieu"] or "")

        c3.write(
            row["ngay"].strftime("%d/%m/%Y")
            if row["ngay"] else ""
        )

        c4.write(row["khach_hang"])

        c5.write(f"{row['so_tien']:,.0f}")

        c6.write(f"{row['da_thanh_toan']:,.0f}")

        if row["con_lai"] > 0:
            c7.write(f"**{row['con_lai']:,.0f}**")
        else:
            c7.success("Đã thu")

        if c8.button(
            "👁",
            key=f"xem_thu_{row['id']}"
        ):
            dialog_chi_tiet(row["id"])

        if c9.button(
            "💵",
            key=f"thu_{row['id']}",
            disabled=row["con_lai"] <= 0
        ):
            dialog_thanh_toan(
                row["id"],
                "THU"
            )

    st.divider()

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Tổng phải thu",
        f"{tong_phai_thu:,.0f}"
    )

    c2.metric(
        "Đã thu",
        f"{tong_phai_thu - tong_con_lai:,.0f}"
    )

    c3.metric(
        "Còn phải thu",
        f"{tong_con_lai:,.0f}"
    )

def tab_no_phai_tra():

    st.subheader("📤 Nợ phải trả")

    ds = lay_no_phai_tra()

    if not ds:
        st.info("Không có dữ liệu.")
        return

    c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns(
        [1, 2, 2, 3, 2, 2, 2, 1, 1]
    )

    c1.write("**STT**")
    c2.write("**Phiếu**")
    c3.write("**Ngày**")
    c4.write("**Khách hàng**")
    c5.write("**Phải trả**")
    c6.write("**Đã trả**")
    c7.write("**Còn lại**")
    c8.write("👁")
    c9.write("💸")

    st.divider()

    tong_phai_tra = 0
    tong_con_lai = 0

    for i, row in enumerate(ds, start=1):

        tong_phai_tra += row["so_tien"]
        tong_con_lai += row["con_lai"]

        c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns(
            [1, 2, 2, 3, 2, 2, 2, 1, 1]
        )

        c1.write(i)

        c2.write(row["so_phieu"] or "")

        c3.write(
            row["ngay"].strftime("%d/%m/%Y")
            if row["ngay"] else ""
        )

        c4.write(row["khach_hang"])

        c5.write(f"{row['so_tien']:,.0f}")

        c6.write(f"{row['da_thanh_toan']:,.0f}")

        if row["con_lai"] > 0:
            c7.write(f"**{row['con_lai']:,.0f}**")
        else:
            c7.success("Đã trả")

        if c8.button(
            "👁",
            key=f"xem_tra_{row['id']}"
        ):
            dialog_chi_tiet(row["id"])

        if c9.button(
            "💸",
            key=f"tra_{row['id']}",
            disabled=row["con_lai"] <= 0
        ):
            dialog_thanh_toan(
                row["id"],
                "TRA"
            )

    st.divider()

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Tổng phải trả",
        f"{tong_phai_tra:,.0f}"
    )

    c2.metric(
        "Đã trả",
        f"{tong_phai_tra - tong_con_lai:,.0f}"
    )

    c3.metric(
        "Còn phải trả",
        f"{tong_con_lai:,.0f}"
    )


def tab_tong_hop():

    st.subheader("📊 Tổng hợp")

    ds = lay_tong_hop_cong_no()

    if not ds:
        st.info("Không có dữ liệu.")
        return

    c1, c2, c3, c4 = st.columns([4,2,2,2])

    c1.write("**Khách hàng**")
    c2.write("**Phải thu**")
    c3.write("**Phải trả**")
    c4.write("**Chênh lệch**")

    st.divider()

    tong_thu = 0
    tong_tra = 0
    tong_chenh = 0

    for row in ds:

        tong_thu += row["no_phai_thu"]
        tong_tra += row["no_phai_tra"]
        tong_chenh += row["chenh_lech"]

        c1, c2, c3, c4 = st.columns([4,2,2,2])

        c1.write(row["ten"])
        c2.write(f"{row['no_phai_thu']:,.0f}")
        c3.write(f"{row['no_phai_tra']:,.0f}")
        c4.write(f"**{row['chenh_lech']:,.0f}**")

    st.divider()

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Tổng phải thu",
        f"{tong_thu:,.0f}"
    )

    c2.metric(
        "Tổng phải trả",
        f"{tong_tra:,.0f}"
    )

    c3.metric(
        "Chênh lệch",
        f"{tong_chenh:,.0f}"
    )


def show():

    st.header("💰 Thanh toán")

    tab1, tab2, tab3 = st.tabs([
        "📥 Nợ phải thu",
        "📤 Nợ phải trả",
        "📊 Tổng hợp"
    ])

    with tab1:
        tab_no_phai_thu()

    with tab2:
        tab_no_phai_tra()

    with tab3:
        tab_tong_hop()
