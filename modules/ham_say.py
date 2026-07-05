import streamlit as st
import pandas as pd
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from database.db import (
    lay_ham_say,
    lay_chi_tiet_ham,
    lay_kho_tuoi_kg,
    lay_kho_tuoi_m3,  
    dua_kg_vao_ham,
    dua_m3_vao_ham,
    ra_ham
)


def tinh_thoi_gian_say(ngay_vao):

    now = datetime.now(timezone.utc)

    if ngay_vao.tzinfo is None:
        ngay_vao = ngay_vao.replace(tzinfo=timezone.utc)

    delta = now - ngay_vao

    ngay = delta.days
    gio = delta.seconds // 3600

    return ngay, gio
    

def mau_thoi_gian(text):

    ngay = int(text.split()[0])

    if ngay < 30:
        return "🟢 " + text

    elif ngay < 40:
        return "🟡 " + text

    elif ngay <= 45:
        return "🟠 " + text

    else:
        return "🔴 " + text


def show():

    if "ra_ham" not in st.session_state:
        st.session_state.ra_ham = False

    if "go_ra_ham" not in st.session_state:
        st.session_state.go_ra_ham = None

    if "m3_duoc_chon" not in st.session_state:
        st.session_state.m3_duoc_chon = None

    if "ham_duoc_chon" not in st.session_state:
        st.session_state.ham_duoc_chon = None

    if "them_vao_ham" not in st.session_state:
        st.session_state.them_vao_ham = False

    if "chi_tiet_duoc_chon" not in st.session_state:
        st.session_state.chi_tiet_duoc_chon = None

    st.header("🔥 Hầm sấy")

    ds_ham = lay_ham_say()

    so_lo = {i: 0 for i in range(1, 7)}

    for row in ds_ham:
        so_lo[row["so_ham"]] = row["so_lo"]

    cols = st.columns(3)

    for i in range(6):

        so_ham = i + 1

        with cols[i % 3]:

            with st.container(border=True):

                st.subheader(f"🔥 Hầm {so_ham}")

                if so_lo[so_ham] > 0:
                    st.write("**Trạng thái:** 🔥 Đang sấy")
                else:
                    st.write("**Trạng thái:** 🟢 Trống")

                st.write(f"**Số lô:** {so_lo[so_ham]}")

                if st.button(
                    "👀 Xem",
                    key=f"ham_{so_ham}",
                    use_container_width=True
                ):
                    st.session_state.ham_duoc_chon = so_ham
                    st.session_state.them_vao_ham = False
                    st.session_state.chi_tiet_duoc_chon = None
                    st.rerun()

    st.divider()

    if st.session_state.ham_duoc_chon is None:
        st.info("Chọn một hầm để xem.")
        return

    so_ham = st.session_state.ham_duoc_chon

    st.subheader(f"📦 Chi tiết Hầm {so_ham}")

    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button(
            "📥 Đưa vào hầm",
            type="primary" if st.session_state.them_vao_ham else "secondary",
            use_container_width=True
        ):
            st.session_state.them_vao_ham = True
            st.session_state.ra_ham = False
            st.rerun()

    with c2:
        if st.button(
            "📤 Ra hầm",
            type="primary" if st.session_state.ra_ham else "secondary",
            use_container_width=True
        ):
            st.session_state.ra_ham = True
            st.session_state.them_vao_ham = False
            st.rerun()
    with c3:

        if st.button(
            "⬅ Quay lại",
            use_container_width=True
        ):
            st.session_state.ham_duoc_chon = None
            st.session_state.them_vao_ham = False
            st.session_state.ra_ham = False
            st.rerun()

    # =====================================================
    # KHO TƯƠI (GỖ KG)
    # =====================================================

    if st.session_state.them_vao_ham:

        st.divider()

        st.subheader("📥 Kho tươi (Gỗ KG)")

        c1, c2, c3, c4, c5, c6 = st.columns(
            [1, 2, 3, 2, 2, 1]
        )

        with c1:
            st.markdown("**Phiếu**")

        with c2:
            st.markdown("**Khách**")

        with c3:
            st.markdown("**Loại gỗ**")

        with c4:
            st.markdown("**Loại**")

        with c5:
            st.markdown("**Khối lượng**")

        with c6:
            st.markdown("**Vào Hầm**")

        st.divider()

        ds = lay_kho_tuoi_kg()

        if len(ds) == 0:

            st.info("Không còn kiện gỗ nào.")

        else:

            for dong in ds:

                c1, c2, c3, c4, c5, c6 = st.columns(
                    [1, 2, 3, 2, 2, 1]
                )

                with c1:
                    st.write(dong["so_phieu"])

                with c2:
                    st.write(dong["khach_hang"])

                with c3:
                    st.write(dong["ten_go"])

                with c4:
                    st.write("KG")

                with c5:
                    st.write(f"{dong['kg']:,.0f} kg")

                with c6:

                    if st.button(
                        "📥",
                        key=f"dua_{dong['id']}"
                    ):

                        dua_kg_vao_ham(
                            dong["id"],
                            so_ham
                        )

                        st.success("Đã đưa vào hầm.")

                        st.rerun()

        st.divider()

        st.subheader("📥 Kho tươi (Gỗ M³)")

        c1, c2, c3, c4, c5, c6, c7 = st.columns(
            [1, 2, 2.5, 3, 2, 2, 1]
        )

        with c1:
            st.markdown("**Phiếu**")

        with c2:
            st.markdown("**Khách**")

        with c3:
            st.markdown("**Loại gỗ**")

        with c4:
            st.markdown("**Kích thước**")

        with c5:
            st.markdown("**Thanh**")

        with c6:
            st.markdown("**M³**")

        with c7:
            st.markdown("**Vào Hầm**")

        st.divider()

        ds_m3 = lay_kho_tuoi_m3()

        if len(ds_m3) == 0:

            st.info("Không còn gỗ M³ trong kho.")

        else:

            for dong in ds_m3:

                c1, c2, c3, c4, c5, c6, c7 = st.columns(
                    [1, 2, 2.5, 3, 2, 2, 1]
                )

                with c1:
                    st.write(dong["so_phieu"])

                with c2:
                    st.write(dong["khach_hang"])

                with c3:
                    st.write(dong["ten_go"])

                with c4:
                    st.write(
                        f"{int(dong['day'])} × "
                        f"{int(dong['rong'])} × "
                        f"{int(dong['dai'])}"
                    )

                with c5:
                    st.write(f"{int(dong['thanh']):,}")

                with c6:
                    st.write(f"{dong['m3']:.3f}")

                with c7:

                    if st.button(
                        "📥",
                        key=f"dua_m3_{dong['id']}"
                    ):
                        st.session_state.m3_duoc_chon = dong

        if st.session_state.m3_duoc_chon is not None:

            dong = st.session_state.m3_duoc_chon

            st.divider()

            st.subheader("📦 Đưa gỗ vào hầm")

            st.write(f"**Khách hàng:** {dong['khach_hang']}")
            st.write(f"**Loại gỗ:** {dong['ten_go']}")

            st.info(
                f"Còn lại: {int(dong['thanh']):,} thanh | {dong['m3']:.3f} m³"
            )

            so_thanh = st.number_input(
                "Số thanh đưa vào",
                min_value=1,
                step=1,
                format="%d"
            )

            if so_thanh > dong["thanh"]:

                st.error(
                    f"❌ Chỉ còn {int(dong['thanh']):,} thanh."
                )

            else:

                m3 = dong["m3"] * so_thanh / dong["thanh"]

                st.success(
                    f"≈ {m3:.3f} m³"
                )

                if st.button(
                    "✅ Xác nhận",
                    type="primary"
                ):

                    dua_m3_vao_ham(
                        dong["id"],
                        so_ham,
                        so_thanh
                    )

                    st.session_state.m3_duoc_chon = None

                    st.success("Đã đưa gỗ vào hầm.")

                    st.rerun()

    # ==========================================
    # RA HẦM
    # ==========================================

    if st.session_state.ra_ham:

        st.divider()

        st.subheader("📤 Ra hầm")

        c1, c2, c3, c4, c5, c6, c7 = st.columns(
            [1.2, 2.5, 2.5, 3.5, 2, 2, 1.5]
        )

        with c1:
            st.markdown("**Phiếu**")

        with c2:
            st.markdown("**Khách**")

        with c3:
            st.markdown("**Loại gỗ**")

        with c4:
            st.markdown("**Kích thước**")

        with c5:
            st.markdown("**Số lượng**")

        with c6:
            st.markdown("**Đã sấy**")

        with c7:
            st.markdown("**Ra Hầm**")

        st.divider()

        ds_ham = lay_chi_tiet_ham(so_ham)

        if len(ds_ham) == 0:

            st.info("Không có gỗ trong hầm.")

        else:

            for dong in ds_ham:

                c1, c2, c3, c4, c5, c6, c7 = st.columns(
                    [1.2, 2.5, 2.5, 3.5, 2, 2, 1.5]
                )

                with c1:
                    st.write(dong["so_phieu"])

                with c2:
                    st.write(dong["khach_hang"])

                with c3:
                    st.write(dong["ten_go"])

                with c4:

                    if dong["kg"] is None:

                        st.write(
                            f'{int(dong["day"])} × '
                            f'{int(dong["rong"])} × '
                            f'{int(dong["dai"])}'
                        )

                    else:

                        st.write("-")

                with c5:

                    if dong["kg"] is not None:
                        st.write(f'{dong["kg"]:,.0f} kg')
                    else:
                        st.write(f'{int(dong["thanh"]):,} thanh')

                with c6:

                    ngay, gio = tinh_thoi_gian_say(
                        dong["ngay_vao"]
                    )

                    st.write(f"🟢 {ngay} ngày")

                with c7:

                    if st.button(
                        "📤",
                        key=f'ra_{dong["id"]}'
                    ):
                        st.session_state.go_ra_ham = dong
    if st.session_state.go_ra_ham is not None:

        dong = st.session_state.go_ra_ham

        st.warning("⚠ Xác nhận ra hầm")

        st.write(f"**Số phiếu:** {dong['so_phieu']}")
        st.write(f"**Khách hàng:** {dong['khach_hang']}")
        st.write(f"**Loại gỗ:** {dong['ten_go']}")

        if dong["kg"] is not None:

            st.write(f"**Khối lượng còn:** {dong['kg']:,.0f} kg")

            kg_ra = st.number_input(
                "Kg muốn ra",
                min_value=0.001,
                max_value=float(dong["kg"]),
                value=float(dong["kg"]),
                step=0.001,
                format="%.3f"
            )

        else:

            st.write(f"**Thanh còn:** {int(dong['thanh']):,}")
            st.write(f"**M³ còn:** {dong['m3']:.3f}")

            thanh_ra = st.text_input(
                "Thanh muốn ra",
                value=str(int(dong["thanh"]))
            )

            try:
                thanh_ra = int(thanh_ra)
            except ValueError:
                st.error("❌ Phải nhập số nguyên.")
                st.stop()

            if thanh_ra <= 0:
                st.error("❌ Số thanh phải lớn hơn 0.")
                st.stop()

            if thanh_ra > dong["thanh"]:
                st.error(f"❌ Chỉ còn {int(dong['thanh']):,} thanh trong hầm.")
                st.stop()

            m3_ra = dong["m3"] * thanh_ra / dong["thanh"]

            st.info(f"Sẽ xuất khoảng {m3_ra:.3f} m³")

        c1, c2 = st.columns(2)

        with c1:

            if st.button(
                "Hủy",
                use_container_width=True
            ):
                st.session_state.go_ra_ham = None
                st.rerun()

        with c2:

            if st.button(
                "📤 Xác nhận",
                type="primary",
                use_container_width=True
            ):

                if dong["kg"] is not None:

                    ra_ham(
                        dong["id"],
                        kg_ra=kg_ra
                    )

                else:

                    ra_ham(
                        dong["id"],
                        thanh_ra=thanh_ra
                    )

                st.success("Đã ra hầm.")

                st.session_state.go_ra_ham = None
                st.session_state.ra_ham = False

                st.rerun()
    # =====================================================
    # CHI TIẾT HẦM
    # =====================================================

    ds = lay_chi_tiet_ham(so_ham)

    st.divider()

    st.subheader("📦 Gỗ trong hầm")

    if len(ds) == 0:

        st.info("Hầm đang trống.")

    else:

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
            "Ngày vào hầm"
        ]

        df.drop(columns=["ID"], inplace=True)

        df.insert(0, "STT", range(1, len(df) + 1))

        df["Ngày nhập"] = pd.to_datetime(
            df["Ngày nhập"]
        ).dt.strftime("%d/%m/%Y")

        ngay_vao = pd.to_datetime(df["Ngày vào hầm"])

        VN = ZoneInfo("Asia/Ho_Chi_Minh")

        ngay_vao_vn = (
            ngay_vao
            .dt.tz_localize("UTC")
            .dt.tz_convert(VN)
        )

        df["Đã sấy"] = ngay_vao.apply(
            lambda x: (
                lambda n, g: f"{n} ngày {g:02d} giờ"
            )(*tinh_thoi_gian_say(x))
        )

        df["Đã sấy"] = df["Đã sấy"].apply(
            mau_thoi_gian
        )

        df["Ngày vào hầm"] = ngay_vao_vn.dt.strftime(
            "%d/%m/%Y %H:%M"
        )

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

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )