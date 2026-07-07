import streamlit as st
import io
import pandas as pd
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from utils.pdf_go_trong_ham import tao_pdf_go_trong_ham

from database.db import (
    lay_ham_say,
    lay_chi_tiet_ham,
    lay_kho_tuoi_kg,
    lay_kho_tuoi_m3,  
    dua_kg_vao_ham,
    dua_m3_vao_ham,
    ra_ham,
    thu_hoi_ham,
    lay_ds_thu_hoi_ham
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

@st.dialog("↩️ Thu hồi khỏi hầm", width="large")
def dialog_thu_hoi_ham():

    if st.session_state.xac_nhan_thu_hoi:

        lo = st.session_state.lo_thu_hoi

        st.error("⚠ XÁC NHẬN THU HỒI")

        st.write(f"**Hầm:** {lo['so_ham']}")
        st.write(f"**Phiếu:** {lo['so_phieu']}")
        st.write(f"**Khách hàng:** {lo['khach_hang']}")
        st.write(f"**Loại gỗ:** {lo['ten']}")

        if lo["kg"] is not None:

            st.info(f"{float(lo['kg']):,.0f} kg")

        else:

            st.info(
                f"{int(lo['thanh']):,} thanh\n\n"
                f"{float(lo['m3']):.3f} m³"
            )

        st.warning("""
    Sau khi thu hồi:

    • Lô này sẽ bị xóa khỏi hầm.

    • Gỗ sẽ trở lại Kho tươi.

    Không thể hoàn tác.
    """)

        c1, c2 = st.columns(2)

        with c1:

            if st.button(
                "❌ Hủy",
                use_container_width=True
            ):
                st.session_state.xac_nhan_thu_hoi = False
                st.session_state.lo_thu_hoi = None
                st.session_state.mo_dialog_thu_hoi = False
                st.rerun()

        with c2:

            if st.button(
                "✅ Đồng ý",
                use_container_width=True,
                type="primary"
            ):

                thu_hoi_ham(lo["id"])

                st.session_state.xac_nhan_thu_hoi = False
                st.session_state.lo_thu_hoi = None
                st.session_state.mo_dialog_thu_hoi = False

                st.success("Đã thu hồi thành công.")

                st.rerun()

        return

    ds = lay_ds_thu_hoi_ham()

    if len(ds) == 0:
        st.info("Không có lô nào đang trong hầm.")
        return

    lua_chon = {}

    for row in ds:

        if row["kg"] is not None:

            text = (
                f"Hầm {row['so_ham']} | "
                f"Phiếu {row['so_phieu']} | "
                f"{row['khach_hang']} | "
                f"{row['ten']} | "
                f"{float(row['kg']):,.0f} kg"
            )

        else:

            text = (
                f"Hầm {row['so_ham']} | "
                f"Phiếu {row['so_phieu']} | "
                f"{row['khach_hang']} | "
                f"{row['ten']} "
                f"({int(row['day'])}×{int(row['rong'])}×{int(row['dai'])}) | "
                f"{int(row['thanh']):,} thanh | "
                f"{float(row['m3']):.3f} m³"
            )
        lua_chon[text] = row

    chon = st.selectbox(
        "Chọn lô cần thu hồi",
        list(lua_chon.keys())
    )

    lo = lua_chon[chon]

    st.divider()

    c1, c2 = st.columns(2)

    with c1:
        st.write(f"**Hầm:** {lo['so_ham']}")
        st.write(f"**Phiếu:** {lo['so_phieu']}")
        st.write(f"**Khách hàng:** {lo['khach_hang']}")

    with c2:
        if lo["kg"] is not None:

            st.write(f"**Loại gỗ:** {lo['ten']}")

        else:

            st.write(
                f"**Loại gỗ:** "
                f"{lo['ten']} "
                f"({int(lo['day'])} × {int(lo['rong'])} × {int(lo['dai'])})"
            )

        if lo["kg"] is not None:

            st.write(f"**Khối lượng:** {float(lo['kg']):,.0f} kg")

        else:

            st.write(f"**Số lượng:** {int(lo['thanh']):,} thanh")
            st.write(f"**Thể tích:** {float(lo['m3']):.3f} m³")

    st.warning(
        "⚠ Thu hồi sẽ bị mất thời gian sấy và trở về kho tươi lại."
    )

    if st.button(
        "↩️ Thu hồi",
        use_container_width=True,
        type="primary"
    ):
        st.session_state.lo_thu_hoi = lo
        st.session_state.xac_nhan_thu_hoi = True
        st.rerun()

def show():

    if "mo_dialog_thu_hoi" not in st.session_state:
        st.session_state.mo_dialog_thu_hoi = False

    if "xac_nhan_thu_hoi" not in st.session_state:
        st.session_state.xac_nhan_thu_hoi = False

    if "lo_thu_hoi" not in st.session_state:
        st.session_state.lo_thu_hoi = None

    if "xac_nhan_thu_hoi" not in st.session_state:
        st.session_state.xac_nhan_thu_hoi = False

    if "ham_say_thu_hoi" not in st.session_state:
        st.session_state.ham_say_thu_hoi = None

    if "ra_ham" not in st.session_state:
        st.session_state.ra_ham = False

    if "go_ra_ham" not in st.session_state:
        st.session_state.go_ra_ham = None

    if "go_dua_ham" not in st.session_state:
        st.session_state.go_dua_ham = None

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
            st.session_state.go_dua_ham = None
            st.rerun()
    with c3:

        if st.button(
            "⬅ Quay lại",
            use_container_width=True
        ):
            st.session_state.ham_duoc_chon = None
            st.session_state.them_vao_ham = False
            st.session_state.ra_ham = False
            st.session_state.go_dua_ham = None
            st.session_state.go_ra_ham = None
            st.rerun()
    if st.session_state.them_vao_ham:

        st.subheader("📥 Đưa vào hầm")

        ds_kg = lay_kho_tuoi_kg()
        ds_m3 = lay_kho_tuoi_m3()

        ds = []

        for x in ds_kg:
            x["loai"] = "KG"
            ds.append(x)

        for x in ds_m3:
            x["loai"] = "M3"
            ds.append(x)

        c1, c2, c3, c4, c5, c6 = st.columns([1,2,3,3,2,1])

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
            st.markdown("**Vào hầm**")

        st.divider()

        if len(ds) == 0:
            st.info("Kho tươi đang trống.")
        else:

            for dong in ds:

                c1,c2,c3,c4,c5,c6 = st.columns([1,2,3,3,2,1])

                with c1:
                    st.write(dong["so_phieu"])

                with c2:
                    st.write(dong["khach_hang"])

                with c3:
                    st.write(dong["ten"])

                with c4:
                    if dong["loai"] == "KG":
                        st.write("•")
                    else:
                        st.write(
                            f'{int(dong["day"])} × '
                            f'{int(dong["rong"])} × '
                            f'{int(dong["dai"])}'
                        )

                with c5:
                    if dong["loai"] == "KG":
                        st.write(f'{dong["kg"]:,.0f} kg')
                    else:
                        st.write(f'{int(dong["thanh"]):,} thanh')

                with c6:
                    if st.button("📥", key=f'dua_{dong["loai"]}_{dong["id"]}'):

                        st.session_state.go_dua_ham = dong
                        st.rerun()
    if st.session_state.go_dua_ham is not None:

        dong = st.session_state.go_dua_ham

        st.warning("⚠ Xác nhận đưa vào hầm")

        st.write(f"**Số phiếu:** {dong['so_phieu']}")
        st.write(f"**Khách hàng:** {dong['khach_hang']}")
        st.write(f"**Loại gỗ:** {dong['ten']}")

        if dong["loai"] == "KG":

            st.write(f"**Khối lượng còn:** {dong['kg']:,.0f} kg")

            kg = st.number_input(
                "Kg đưa vào",
                min_value=0.0,
                max_value=float(dong["kg"]),
                value=0.0,
                step=1.0,
                format="%.0f",
                key="kg_dua_ham"
            )

        else:

            st.write(f"**Thanh còn:** {int(dong['thanh']):,}")
            st.write(f"**M³ còn:** {dong['m3']:.3f}")

            thanh = st.number_input(
                "Thanh đưa vào",
                min_value=1,
                max_value=int(dong["thanh"]),
                value=1,
                step=1,
                key="thanh_dua_ham"
            )

            st.info(
                f"≈ {dong['m3'] * thanh / dong['thanh']:.3f} m³"
            )

        c1, c2 = st.columns(2)

        with c1:

            if st.button(
                "Hủy",
                use_container_width=True,
                key="huy_dua_ham"
            ):

                st.session_state.go_dua_ham = None
                st.rerun()

        with c2:

            if st.button(
                "📥 Xác nhận",
                type="primary",
                use_container_width=True,
                key="xac_nhan_dua_ham"
            ):

                if dong["loai"] == "KG":

                    dua_kg_vao_ham(
                        dong["id"],
                        so_ham
                    )

                else:

                    dua_m3_vao_ham(
                        dong["id"],
                        so_ham,
                        thanh
                    )

                st.success("Đã đưa vào hầm.")

                st.session_state.go_dua_ham = None
                st.session_state.them_vao_ham = False

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
                    st.write(dong["ten"])

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
        st.write(f"**Loại gỗ:** {dong['ten']}")

        if dong["kg"] is not None:

            st.write(f"**Khối lượng còn:** {dong['kg']:,.0f} kg")

            kg_ra = st.number_input(
                "Kg muốn ra",
                min_value=0.0,
                max_value=float(dong["kg"]),
                value=float(dong["kg"]),
                step=1.0,
                format="%.0f"
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

        ngay_vao = pd.to_datetime(
            df["Ngày vào hầm"],
            utc=True
        )

        VN = ZoneInfo("Asia/Ho_Chi_Minh")

        ngay_vao_vn = ngay_vao.dt.tz_convert(VN)

        df["Đã sấy"] = ngay_vao.apply(
            lambda x: (
                lambda n, g: f"{n} ngày {g:02d} giờ"
            )(*tinh_thoi_gian_say(x))
        )

        df["Đã sấy"] = df["Đã sấy"].apply(mau_thoi_gian)

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

        tong = {
            "STT": "",
            "Ngày nhập": "TỔNG CỘNG",
            "Số phiếu": "",
            "Khách hàng": "",
            "Tên gỗ": "",
            "Dày": "",
            "Rộng": "",
            "Dài": "",
            "Kg": f"{tong_kg:,.0f}" if tong_kg else "",
            "Thanh": f"{tong_thanh:,.0f}" if tong_thanh else "",
            "M³": f"{tong_m3:.3f}" if tong_m3 else "",
            "Ngày vào hầm": "",
            "Đã sấy": ""
        }

        df = pd.concat([df, pd.DataFrame([tong])], ignore_index=True)

        pdf = tao_pdf_go_trong_ham(df, so_ham)

        buffer = io.BytesIO()

        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Gỗ trong hầm")

        buffer.seek(0)

        c1, c2 = st.columns(2)

        with c1:
            st.download_button(
                "📄 Xuất PDF",
                data=pdf,
                file_name="Go_trong_ham.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary"
            )

        with c2:
            st.download_button(
                "📊 Xuất Excel",
                data=buffer,
                file_name="Go_trong_ham.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                type="primary"
            )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        if st.button(
            "↩️ Thu hồi khỏi hầm",
            use_container_width=True
        ):
            st.session_state.mo_dialog_thu_hoi = True
            st.rerun()

        # Đặt ngoài if button
        if st.session_state.mo_dialog_thu_hoi:
            dialog_thu_hoi_ham()