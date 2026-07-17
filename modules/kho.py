import streamlit as st
import pandas as pd
import io
from zoneinfo import ZoneInfo
from utils.pdf_kho_kho import tao_pdf_kho_kho
from utils.pdf_kho_tuoi import tao_pdf_kho_tuoi
from utils.pdf_kho_da_phan_loai import tao_pdf_kho_da_phan_loai
from database.db import (
    lay_ds_khach_hang,
    lay_ds_loai_go,
    lay_kho_tuoi,
    lay_kho_kho,
    lay_ds_phan_loai,
    luu_phan_loai,
    lay_kho_da_phan_loai,
    lay_ds_ten_go,
    lay_ds_quy_cach,
    lay_ds_quy_cach_da_phan_loai,
    lay_chi_tiet_nhap_hang_kho,
    lay_kho_hang_mua,  
    luu_phan_loai_hang_mua
)

def chon_lo():
    ds = lay_kho_kho(None, None)

    if len(ds) == 0:
        st.info("Không còn lô nào.")
        return None

    lua_chon = {}
    for row in ds:
        if row["kg"] is not None:
            text = (
                f"Phiếu: {row['so_phieu']} | "
                f"Khách: {row['khach_hang']} | "
                f"Gỗ: {row['ten']} | "
                f"Kg: {float(row['kg']):,.0f}"
            )
        else:
            text = (
                f"Phiếu: {row['so_phieu']} | "
                f"Khách: {row['khach_hang']} | "
                f"Gỗ: {row['ten']} | "
                f"{int(row['day'])}×{int(row['rong'])}×{int(row['dai'])} | "
                f"{int(row['thanh']):,} thanh | "
                f"{row['m3']:.3f} m³"
            )
        
        row["nguon"] = "KHO_KHO"
        lua_chon[text] = row

    chon = st.selectbox("Chọn lô", list(lua_chon.keys()))
    return lua_chon[chon]

def chon_lo_hang_mua():

    ds = lay_kho_hang_mua(None, None)

    if len(ds) == 0:
        st.info("Không còn lô nào.")
        return None

    lua_chon = {}

    for row in ds:

        if row["kg"] is not None:

            text = (
                f"Phiếu: {row['so_phieu']} | "
                f"Khách: {row['khach_hang']} | "
                f"Gỗ: {row['ten']} | "
                f"Kg: {float(row['kg']):,.0f}"
            )

        else:

            text = (
                f"Phiếu: {row['so_phieu']} | "
                f"Khách: {row['khach_hang']} | "
                f"Gỗ: {row['ten']} | "
                f"{int(row['day'])}×{int(row['rong'])}×{int(row['dai'])} | "
                f"{int(row['thanh']):,} thanh | "
                f"{row['m3']:.3f} m³"
            )

        row["nguon"] = "HANG_MUA"
        lua_chon[text] = row

    chon = st.selectbox(
        "Chọn lô",
        list(lua_chon.keys())
    )

    return lua_chon[chon]

def hien_thi_thong_tin_lo(lo):
    st.divider()
    st.write(f"**Phiếu:** {lo['so_phieu']}")
    st.write(f"**Khách:** {lo['khach_hang']}")
    st.write(f"**Loại gỗ:** {lo['ten']}")
    if lo["kieu_tinh"] == "M3":
        st.write(
            f"**Loại gỗ:** {lo['ten']} "
            f"({int(lo['day'])} × {int(lo['rong'])} × {int(lo['dai'])})"
        )
    else:
        st.write(f"**Loại gỗ:** {lo['ten']}")


    if lo["kg"] is not None:
        st.info(f"Còn {float(lo['kg']):,.0f} kg")
    else:
        st.info(f"Còn {int(lo['thanh']):,} thanh | {lo['m3']:.3f} m³")
    st.divider()

# Bọc fragment chuẩn để cô lập toàn bộ logic nhập liệu, thêm và xóa
@st.fragment()
def nhap_phan_loai(lo):
    
    ds = lay_ds_phan_loai()
    lua_chon = {x["ten"]: x["id"] for x in ds}

    ten_phan_loai = st.selectbox("Loại phân loại", list(lua_chon.keys()))

    lo_kg_float = float(lo["kg"]) if lo["kg"] is not None else None

    if lo_kg_float is None:

        day = st.number_input(
            "Dày",
            value=float(lo["day"]),
            min_value=0.0,
            step=0.1
        )

        rong = st.number_input(
            "Rộng",
            value=float(lo["rong"]),
            min_value=0.0,
            step=0.1
        )

        dai = st.number_input(
            "Dài",
            value=float(lo["dai"]),
            min_value=0.0,
            step=1.0
        )

    else:

        day = None
        rong = None
        dai = None

    # Tạo key động cho ô nhập liệu dựa trên số lần làm mới để reset giá trị cũ khi bấm Xóa
    input_key = f"input_{st.session_state.dialog_refresh_trigger}"

    if lo_kg_float is not None:
        so_luong = st.number_input("Kg phân loại", min_value=0.0, step=1.0, key=input_key)
        da_phan = sum(float(x.get("kg", 0)) for x in st.session_state.ds_phan_loai)      
    else:
        so_luong = st.number_input("Số thanh phân loại", min_value=1, step=1, key=input_key)
        m3 = round(
            day *
            rong *
            dai *
            so_luong /
            1000000000,
            6
        )

        st.info(f"Thể tích: {m3:.3f} m³")
        da_thanh = sum(int(x.get("thanh", 0)) for x in st.session_state.ds_phan_loai)

    if st.button("➕ Thêm phân loại", use_container_width=True, type="primary"):

        loi = False

        if lo_kg_float is not None:

            if round(so_luong + da_phan, 2) > round(lo_kg_float, 2):
                st.error("❌ Vượt số kg còn lại.")
                loi = True

        else:

            if so_luong + da_thanh > int(lo["thanh"]):
                st.error("❌ Vượt số thanh còn lại.")
                loi = True

        if not loi:

            da_co = False

            for item in st.session_state.ds_phan_loai:

                if item["loai"] == ten_phan_loai:

                    item["day"] = day
                    item["rong"] = rong
                    item["dai"] = dai

                    if lo_kg_float is not None:

                        item["kg"] = item.get("kg", 0) + so_luong

                    else:

                        item["thanh"] = item.get("thanh", 0) + so_luong

                        item["m3"] = round(
                            item["day"] *
                            item["rong"] *
                            item["dai"] *
                            item["thanh"] /
                            1000000000,
                            6
                        )

                    da_co = True
                    break

            if not da_co:

                if lo_kg_float is not None:

                    st.session_state.ds_phan_loai.append({

                        "loai": ten_phan_loai,

                        "day": day,
                        "rong": rong,
                        "dai": dai,

                        "kg": so_luong,
                        "thanh": 0,
                        "m3": 0

                    })

                else:

                    m3 = round(
                        day *
                        rong *
                        dai *
                        so_luong /
                        1000000000,
                        6
                    )

                    st.session_state.ds_phan_loai.append({

                        "loai": ten_phan_loai,

                        "day": day,
                        "rong": rong,
                        "dai": dai,

                        "kg": 0,
                        "thanh": so_luong,
                        "m3": m3

                    })

            # Chỉ rerun khi thêm thành công
            st.session_state.dialog_refresh_trigger += 1
            st.rerun(scope="fragment")

    if len(st.session_state.ds_phan_loai):
        st.divider()
        st.subheader("📋 Danh sách phân loại")

        xoa_index = None

        with st.container(key=f"container_bangg_{st.session_state.dialog_refresh_trigger}"):
            for i, item in enumerate(st.session_state.ds_phan_loai):
                c1, c2, c3, c4 = st.columns([4, 2, 2, 1])
                c1.write(item["loai"])

                if lo_kg_float is not None:
                    c2.write(f"{float(item.get('kg', 0)):,.0f} kg")
                else:
                    c2.write(f"{int(item.get('thanh', 0)):,} thanh")
                    c3.write(f"{float(item.get('m3', 0)):.3f} m³")

                if c4.button("🗑️", key=f"xoa_{i}_{st.session_state.dialog_refresh_trigger}"):
                    xoa_index = i

        if xoa_index is not None:
            st.session_state.ds_phan_loai.pop(xoa_index)
            # Tăng trigger để reset giá trị trong ô input và F5 fragment lập tức xóa hàng
            st.session_state.dialog_refresh_trigger += 1
            st.rerun(scope="fragment")

    if lo_kg_float is not None:
        da_phan = sum(float(x.get("kg", 0)) for x in st.session_state.ds_phan_loai)
        con_lai = lo_kg_float - da_phan
        st.info(f"📦 Còn lại: {con_lai:,.0f} kg")
    else:
        da_thanh = sum(int(x.get("thanh", 0)) for x in st.session_state.ds_phan_loai)
        da_m3 = sum(float(x.get("m3", 0)) for x in st.session_state.ds_phan_loai)
        con_thanh = int(lo["thanh"]) - da_thanh
        con_m3 = float(lo["m3"]) - da_m3
        st.info(f"📦 Còn lại: {con_thanh:,} thanh | {con_m3:.3f} m³")
        
    st.divider()

    if st.button("💾 Hoàn tất phân loại", use_container_width=True, type="primary"):

        if lo.get("nguon") == "HANG_MUA":

            luu_phan_loai_hang_mua(
                lo["id"],
                st.session_state.ds_phan_loai
            )

        else:

            luu_phan_loai(
                lo["id"],
                st.session_state.ds_phan_loai
            )

        st.session_state.ds_phan_loai = []
        st.success("Đã phân loại thành công.")
        st.rerun(scope="app")

@st.dialog("📦 Phân loại kho khô", width="large")
def dialog_phan_loai():
    if "ds_phan_loai" not in st.session_state:
        st.session_state.ds_phan_loai = []
        
    if "dialog_refresh_trigger" not in st.session_state:
        st.session_state.dialog_refresh_trigger = 0

    lo = chon_lo()
    if lo is None:
        return

    hien_thi_thong_tin_lo(lo)
    nhap_phan_loai(lo)

@st.dialog("📦 Phân loại hàng mua", width="large")
def dialog_phan_loai_hang_mua():

    if "ds_phan_loai" not in st.session_state:
        st.session_state.ds_phan_loai = []

    if "dialog_refresh_trigger" not in st.session_state:
        st.session_state.dialog_refresh_trigger = 0

    lo = chon_lo_hang_mua()
    if lo is None:
        return

    hien_thi_thong_tin_lo(lo)
    nhap_phan_loai(lo)

def show():
    if "tab_nhom" not in st.session_state:
        st.session_state.tab_nhom = "gia_cong"

    if "tab_kho" not in st.session_state:
        st.session_state.tab_kho = "tuoi"

    st.header("🏬 Kho")

    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button(
            "🌲 Kho gia công",
            type="primary" if st.session_state.tab_nhom == "gia_cong" else "secondary",
            use_container_width=True,
        ):
            st.session_state.tab_nhom = "gia_cong"
            st.rerun()

    with c2:
        if st.button(
            "📦 Kho hàng mua",
            type="primary" if st.session_state.tab_nhom == "mua" else "secondary",
            use_container_width=True,
        ):
            st.session_state.tab_nhom = "mua"
            st.rerun()

    with c3:
        if st.button(
            "🟤 Kho đã phân loại",
            type="primary" if st.session_state.tab_nhom == "da_phan_loai" else "secondary",
            use_container_width=True,
        ):
            st.session_state.tab_nhom = "da_phan_loai"
            st.rerun()

    st.divider()

    if st.session_state.tab_nhom == "gia_cong":

        c1, c2 = st.columns(2)

        with c1:
            if st.button(
                "🟢 Kho hàng tươi",
                type="primary" if st.session_state.tab_kho == "tuoi" else "secondary",
                use_container_width=True,
            ):
                st.session_state.tab_kho = "tuoi"
                st.rerun()

        with c2:
            if st.button(
                "🟡 Kho khô chưa phân loại",
                type="primary" if st.session_state.tab_kho == "chua_phan_loai" else "secondary",
                use_container_width=True,
            ):
                st.session_state.tab_kho = "chua_phan_loai"
                st.rerun()

        st.divider()

        if st.session_state.tab_kho == "tuoi":
            st.subheader("🟢 Kho hàng tươi")

            c1, c2, c3 = st.columns(3)

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

            with c2:

                ds_ten = lay_ds_ten_go()

                ds_ten = [{"ten": "Tất cả"}] + ds_ten

                ten_go = st.selectbox(
                    "Tên gỗ",
                    [x["ten"] for x in ds_ten]
                )

                if ten_go == "Tất cả":
                    ten_go = None

            with c3:

                loai_go_id = None

                if ten_go is None:

                    st.selectbox(
                        "Quy cách",
                        ["Tất cả"],
                        disabled=True
                    )

                else:

                    ds_qc = lay_ds_quy_cach(ten_go)

                    options_qc = [{"id": None, "ten": "Tất cả"}]

                    for x in ds_qc:

                        options_qc.append({
                            "id": x["id"],
                            "ten": f'{int(x["day"])} × {int(x["rong"])} × {int(x["dai"])}'
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

            ds = lay_kho_tuoi(
                khach_hang_id,
                ten_go,
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
                "Dày",
                "Rộng",
                "Dài",
                "Kg",
                "Thanh",
                "M³",
                "Đơn giá",
                "Thành tiền"
            ]
            df.drop(columns=["ID"], inplace=True)
            df.insert(0, "STT", range(1, len(df) + 1))
            df["Ngày nhập"] = pd.to_datetime(df["Ngày nhập"]).dt.strftime("%d/%m/%Y")

            for c in ["Dày", "Rộng", "Dài", "Thanh"]:
                df[c] = df[c].apply(lambda x: "" if pd.isna(x) else int(x))

            df["Kg"] = df["Kg"].apply(lambda x: "" if pd.isna(x) else f"{x:,.0f}")
            df["M³"] = df["M³"].apply(lambda x: "" if pd.isna(x) else f"{x:.3f}")
            df["Đơn giá"] = df["Đơn giá"].apply(
                lambda x: "" if pd.isna(x) else f"{x:,.0f}"
            )

            df["Thành tiền"] = df["Thành tiền"].apply(
                lambda x: "" if pd.isna(x) else f"{x:,.0f}"
            )

            tong_kg = pd.to_numeric(df["Kg"].astype(str).str.replace(",", ""), errors="coerce").fillna(0).sum()
            tong_thanh = pd.to_numeric(df["Thanh"], errors="coerce").fillna(0).sum()
            tong_m3 = pd.to_numeric(df["M³"], errors="coerce").fillna(0).sum()
            tong_tien = pd.to_numeric(
                df["Thành tiền"].astype(str).str.replace(",", ""),
                errors="coerce"
            ).fillna(0).sum()

            df.loc[len(df)] = {
                "STT": "",
                "Ngày nhập": "",
                "Số phiếu": "",
                "Khách hàng": "",
                "Tên gỗ": "TỔNG CỘNG",
                "Dày": "",
                "Rộng": "",
                "Dài": "",
                "Kg": f"{tong_kg:,.0f}" if tong_kg else "",
                "Thanh": f"{tong_thanh:,.0f}" if tong_thanh else "",
                "M³": f"{tong_m3:.3f}" if tong_m3 else "",
                "Đơn giá": "",
                "Thành tiền": f"{tong_tien:,.0f}" if tong_tien else "",
            }
            pdf = tao_pdf_kho_tuoi(df, ten_kh, ten_go)

            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Kho tươi")
            buffer.seek(0)

            c1, c2 = st.columns(2)
            with c1:
                st.download_button("📄 Xuất PDF", data=pdf, file_name="Kho_tuoi.pdf", mime="application/pdf", use_container_width=True, type="primary")
            with c2:
                st.download_button("📊 Xuất Excel", data=buffer, file_name="Kho_tuoi.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True, type="primary")

            st.dataframe(df, use_container_width=True, hide_index=True)

        elif st.session_state.tab_kho == "chua_phan_loai":
            st.subheader("🟡 Kho khô chưa phân loại")
            c1, c2, c3 = st.columns(3)

            with c1:
                ds_kh = lay_ds_khach_hang()
                options = [{"id": None, "ten": "Tất cả"}]
                options.extend(ds_kh)
                ten_kh = st.selectbox("Khách hàng", [x["ten"] for x in options], key="kh_kho")
                khach_hang_id = next(x["id"] for x in options if x["ten"] == ten_kh)

            with c2:

                ds_ten = lay_ds_ten_go()

                ds_ten = [{"ten": "Tất cả"}] + ds_ten

                ten_go = st.selectbox(
                    "Tên gỗ",
                    [x["ten"] for x in ds_ten],
                    key="ten_go_kho"
                )

                if ten_go == "Tất cả":
                    ten_go = None

            with c3:

                loai_go_id = None

                if ten_go is None:

                    st.selectbox(
                        "Quy cách",
                        ["Tất cả"],
                        disabled=True,
                        key="qc_kho"
                    )

                else:

                    ds_qc = lay_ds_quy_cach(ten_go)

                    if len(ds_qc) == 0:

                        st.selectbox(
                            "Quy cách",
                            ["Không có"],
                            disabled=True,
                            key="qc_kho"
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
                            [x["ten"] for x in options_qc],
                            key="qc_kho"
                        )

                        loai_go_id = next(
                            x["id"]
                            for x in options_qc
                            if x["ten"] == ten_qc
                        )

            ds = lay_kho_kho(khach_hang_id, loai_go_id)
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
                "Kiểu tính",
                "Dày",
                "Rộng",
                "Dài",
                "Kg",
                "Thanh",
                "M³",
                "Ngày vào hầm",
                "Ngày ra hầm",
                "Đơn giá",
                "Thành tiền"
            ]
            df.drop(columns=["ID"], inplace=True)
            df.insert(0, "STT", range(1, len(df) + 1))
            df["Ngày nhập"] = pd.to_datetime(df["Ngày nhập"]).dt.strftime("%d/%m/%Y")

            VN = ZoneInfo("Asia/Ho_Chi_Minh")
            ngay_vao = pd.to_datetime(df["Ngày vào hầm"]).dt.tz_localize("UTC").dt.tz_convert(VN)
            ngay_ra = pd.to_datetime(df["Ngày ra hầm"]).dt.tz_localize("UTC").dt.tz_convert(VN)
            df["Ngày vào hầm"] = ngay_vao.dt.strftime("%d/%m/%Y %H:%M")
            df["Ngày ra hầm"] = ngay_ra.dt.strftime("%d/%m/%Y %H:%M")

            for c in ["Dày", "Rộng", "Dài"]:
                df[c] = df[c].apply(lambda x: "" if pd.isna(x) else int(x))

            df["Thanh"] = df["Thanh"].apply(lambda x: "" if pd.isna(x) else f"{int(x):,}")
            df["Kg"] = df["Kg"].apply(lambda x: "" if pd.isna(x) else f"{x:,.0f}")
            df["M³"] = df["M³"].apply(lambda x: "" if pd.isna(x) else f"{x:.3f}")
            df["Đơn giá"] = df["Đơn giá"].apply(
                lambda x: "" if pd.isna(x) else f"{x:,.0f}"
            )

            df["Thành tiền"] = df["Thành tiền"].apply(
                lambda x: "" if pd.isna(x) else f"{x:,.0f}"
            )

            tong_kg = pd.to_numeric(df["Kg"].astype(str).str.replace(",", ""), errors="coerce").fillna(0).sum()
            tong_thanh = pd.to_numeric(df["Thanh"].astype(str).str.replace(",", ""), errors="coerce").fillna(0).sum()
            tong_m3 = pd.to_numeric(df["M³"], errors="coerce").fillna(0).sum()

            tong_tien = pd.to_numeric(
                df["Thành tiền"].astype(str).str.replace(",", ""),
                errors="coerce"
            ).fillna(0).sum()

            df.loc[len(df)] = {
                "STT": "",
                "Ngày nhập": "",
                "Số phiếu": "",
                "Khách hàng": "",
                "Tên gỗ": "TỔNG CỘNG",
                "Dày": "",
                "Rộng": "",
                "Dài": "",
                "Kg": f"{tong_kg:,.0f}" if tong_kg else "",
                "Thanh": f"{tong_thanh:,.0f}" if tong_thanh else "",
                "M³": f"{tong_m3:.3f}" if tong_m3 else "",
                "Ngày vào hầm": "",
                "Ngày ra hầm": "",
                "Đơn giá": "",
                "Thành tiền": f"{tong_tien:,.0f}" if tong_tien else ""
            }
            pdf = tao_pdf_kho_kho(df, ten_kh, ten_go)

            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Kho khô")
            buffer.seek(0)

            c1, c2 = st.columns(2)
            with c1:
                st.download_button("📄 Xuất PDF", data=pdf, file_name="Kho_kho.pdf", mime="application/pdf", use_container_width=True, type="primary")
            with c2:
                st.download_button("📊 Xuất Excel", data=buffer, file_name="Kho_kho.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True, type="primary")
            
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.divider()

            if st.button("📦 Phân loại kho khô", use_container_width=True, type="primary"):
                dialog_phan_loai() 

    elif st.session_state.tab_nhom == "mua":

        st.subheader("📦 Kho hàng mua")

        c1, c2, c3 = st.columns(3)

        with c1:

            ds_kh = lay_ds_khach_hang()

            options = [{"id": None, "ten": "Tất cả"}]
            options.extend(ds_kh)

            ten_kh = st.selectbox(
                "Khách hàng",
                [x["ten"] for x in options],
                key="kh_mua"
            )

            khach_hang_id = next(
                x["id"]
                for x in options
                if x["ten"] == ten_kh
            )

        with c2:

            ds_ten = lay_ds_ten_go()

            ds_ten = [{"ten": "Tất cả"}] + ds_ten

            ten_go = st.selectbox(
                "Tên gỗ",
                [x["ten"] for x in ds_ten],
                key="ten_go_mua"
            )

            if ten_go == "Tất cả":
                ten_go = None

        with c3:

            loai_go_id = None

            if ten_go is None:

                st.selectbox(
                    "Quy cách",
                    ["Tất cả"],
                    disabled=True,
                    key="qc_mua"
                )

            else:

                ds_qc = lay_ds_quy_cach(ten_go)

                options_qc = [{"id": None, "ten": "Tất cả"}]

                for x in ds_qc:

                    options_qc.append({
                        "id": x["id"],
                        "ten": f'{int(x["day"])} × {int(x["rong"])} × {int(x["dai"])}'
                    })

                ten_qc = st.selectbox(
                    "Quy cách",
                    [x["ten"] for x in options_qc],
                    key="qc_mua"
                )

                loai_go_id = next(
                    x["id"]
                    for x in options_qc
                    if x["ten"] == ten_qc
                )

        ds = lay_kho_hang_mua(
            khach_hang_id,
            loai_go_id
        )

        if len(ds) == 0:
            st.info("Kho hàng mua đang trống.")
        else:

            df = pd.DataFrame(ds)

            df.columns = [
                "ID",
                "Ngày nhập",
                "Số phiếu",
                "Khách hàng",
                "Tên gỗ",
                "Kiểu tính",
                "Dày",
                "Rộng",
                "Dài",
                "Kg",
                "Thanh",
                "M³",
                "Đơn giá",
                "Thành tiền"
            ]

            df.drop(columns=["ID"], inplace=True)

            df.insert(0, "STT", range(1, len(df) + 1))

            df["Ngày nhập"] = pd.to_datetime(
                df["Ngày nhập"]
            ).dt.strftime("%d/%m/%Y")

            df["Kiểu tính"] = df["Kiểu tính"].replace({
                "M3": "Khối (m³)",
                "TRONG_LUONG": "Trọng lượng (Kg)"
            })

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
            df["Đơn giá"] = df["Đơn giá"].apply(
                lambda x: "" if pd.isna(x) else f"{x:,.0f}"
            )

            df["Thành tiền"] = df["Thành tiền"].apply(
                lambda x: "" if pd.isna(x) else f"{x:,.0f}"
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

            tong_tien = pd.to_numeric(
                df["Thành tiền"].astype(str).str.replace(",", ""),
                errors="coerce"
            ).fillna(0).sum()

            df.loc[len(df)] = {
                "STT": "",
                "Ngày nhập": "",
                "Số phiếu": "",
                "Khách hàng": "",
                "Tên gỗ": "TỔNG CỘNG",
                "Kiểu tính": "",
                "Dày": "",
                "Rộng": "",
                "Dài": "",
                "Kg": f"{tong_kg:,.0f}" if tong_kg else "",
                "Thanh": f"{tong_thanh:,.0f}" if tong_thanh else "",
                "M³": f"{tong_m3:.3f}" if tong_m3 else "",
                "Đơn giá": "",
                "Thành tiền": f"{tong_tien:,.0f}" if tong_tien else ""
            }

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

        st.divider()

        if st.button(
            "📦 Chuyển sang kho đã phân loại",
            type="primary",
            use_container_width=True
        ):
            dialog_phan_loai_hang_mua()

    elif st.session_state.tab_nhom == "da_phan_loai":
        st.subheader("🟤 Kho khô đã phân loại")
        ds_quy_cach = []
        chon_qc = []

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            ds_kh = lay_ds_khach_hang()
            options = [{"id": None, "ten": "Tất cả"}]
            options.extend(ds_kh)

            ten_kh = st.selectbox(
                "Khách hàng",
                [x["ten"] for x in options],
                key="kh_da_phan_loai"
            )

            khach_hang_id = next(
                x["id"]
                for x in options
                if x["ten"] == ten_kh
            )

        with c2:

            ds_phan_loai = lay_ds_phan_loai()

            lua_chon_pl = [{"id": None, "ten": "Tất cả"}] + ds_phan_loai

            phan_loai = st.selectbox(
                "Phân loại",
                lua_chon_pl,
                format_func=lambda x: x["ten"]
            )

        with c3:

            ds_ten = lay_ds_ten_go()

            ds_ten = [{"ten": "Tất cả"}] + ds_ten

            ten_go = st.selectbox(
                "Tên gỗ",
                [x["ten"] for x in ds_ten],
                key="ten_go_da_phan_loai"
            )

            if ten_go == "Tất cả":
                ten_go = None

        with c4:

            loai_go_id = None
            day = None
            rong = None
            dai = None
            if ten_go is None:

                st.selectbox(
                    "Quy cách",
                    ["Tất cả"],
                    disabled=True,
                    key="qc_da_phan_loai"
                )

            else:

                ds_qc = lay_ds_quy_cach_da_phan_loai(ten_go)

                if len(ds_qc) == 0:

                    st.selectbox(
                        "Quy cách",
                        ["Không có"],
                        disabled=True,
                        key="qc_da_phan_loai"
                    )

                else:

                    options_qc = [{"id": None, "ten": "Tất cả"}]

                    for x in ds_qc:

                        options_qc.append({
                            "day": x["day"],
                            "rong": x["rong"],
                            "dai": x["dai"],
                            "ten": (
                                f"{x['day']:g} × {x['rong']:g} × {x['dai']:g}"
                                if x["day"] is not None
                                else "(Kg)"
                            )
                        })

                    with st.expander("📏 Chọn quy cách", expanded=False):

                        tat_ca = st.checkbox("✔ Chọn tất cả", key="tat_ca_qc")

                        chon_qc = []

                        for qc in options_qc:

                            if qc["ten"] == "Tất cả":
                                continue

                            if st.checkbox(
                                qc["ten"],
                                value=tat_ca,
                                key=f"qc_{qc['ten']}"
                            ):
                                chon_qc.append(qc["ten"])

                    ds_quy_cach = [
                        x
                        for x in options_qc
                        if x["ten"] in chon_qc
                    ]

        ds = lay_kho_da_phan_loai(
            khach_hang_id,
            ten_go,
            ds_quy_cach,
            phan_loai["id"]
        )

        if len(ds) == 0:
            st.info("Chưa có dữ liệu.")
            return

        df = pd.DataFrame(ds)

        df = df.rename(columns={
            "ngay": "Ngày",
            "so_phieu": "Phiếu",
            "khach_hang": "Khách",
            "ten": "Loại gỗ",
            "phan_loai": "Phân loại",
            "day": "Dày",
            "rong": "Rộng",
            "dai": "Dài",
            "kg": "Kg",
            "thanh": "Thanh",
            "m3": "M³"
            #"don_gia": "Đơn giá",
            #"thanh_tien": "Thành tiền"
        })
        df["Nguồn"] = df["loai_nhap"].map({
            "TUOI": "🌲 Gia công",
            "KHO": "📦 Hàng mua"
        })

        df = df[
            [
                "Nguồn",
                "Ngày",
                "Phiếu",
                "Khách",
                "Loại gỗ",
                "Phân loại",
                "Dày",
                "Rộng",
                "Dài",
                "Kg",
                "Thanh",
                "M³"
            ]
        ]

        df.insert(0, "STT", range(1, len(df) + 1))

        df["Ngày"] = pd.to_datetime(df["Ngày"]).dt.strftime("%d/%m/%Y")


        def format_kich_thuoc(x):

            if pd.isna(x):
                return ""

            if float(x).is_integer():
                return int(x)

            return float(x)


        for cot in ["Dày", "Rộng", "Dài"]:

            df[cot] = df[cot].apply(format_kich_thuoc)


        tong_kg = pd.to_numeric(df["Kg"], errors="coerce").fillna(0).sum()
        tong_thanh = pd.to_numeric(df["Thanh"], errors="coerce").fillna(0).sum()
        tong_m3 = pd.to_numeric(df["M³"], errors="coerce").fillna(0).sum()
        #tong_tien = pd.to_numeric(
            #df["Thành tiền"].astype(str).str.replace(",", ""),
            #errors="coerce"
        #).fillna(0).sum()


        df["Kg"] = df["Kg"].apply(
            lambda x: "" if pd.isna(x) else f"{float(x):,.0f}"
        )

        df["Thanh"] = df["Thanh"].apply(
            lambda x: "" if pd.isna(x) else f"{int(x):,}"
        )

        df["M³"] = df["M³"].apply(
            lambda x: "" if pd.isna(x) else f"{float(x):.3f}"
        )
        #df["Đơn giá"] = df["Đơn giá"].apply(
            #lambda x: "" if pd.isna(x) else f"{x:,.0f}"
        #)

        #df["Thành tiền"] = df["Thành tiền"].apply(
         #   lambda x: "" if pd.isna(x) else f"{x:,.0f}"
        #)


        df.loc[len(df)] = {
            "STT": "",
            "Nguồn": "",
            "Ngày": "",
            "Phiếu": "",
            "Khách": "",
            "Loại gỗ": "TỔNG CỘNG",
            "Phân loại": "",
            "Dày": "",
            "Rộng": "",
            "Dài": "",
            "Kg": f"{tong_kg:,.0f}" if tong_kg else "",
            "Thanh": f"{tong_thanh:,.0f}" if tong_thanh else "",
            "M³": f"{tong_m3:.3f}" if tong_m3 else ""
            #"Đơn giá": "",
            #"Thành tiền": f"{tong_tien:,.0f}" if tong_tien else ""
        }

        ten_qc = ", ".join(chon_qc) if chon_qc else "Tất cả"

        df_pdf = df.copy()

        if "Nguồn" in df_pdf.columns:
            df_pdf.drop(columns=["Nguồn"], inplace=True)

        pdf = tao_pdf_kho_da_phan_loai(
            df_pdf,
            ten_kh,
            ten_go if ten_go else "Tất cả",
            ten_qc
        )

        buffer = io.BytesIO()

        with pd.ExcelWriter(
            buffer,
            engine="openpyxl"
        ) as writer:
            df_pdf.to_excel(
                writer,
                index=False,
                sheet_name="Kho đã phân loại"
            )

        buffer.seek(0)

        c1, c2 = st.columns(2)

        with c1:
            st.download_button(
                "📄 Xuất PDF",
                data=pdf,
                file_name="Kho_da_phan_loai.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary"
            )

        with c2:
            st.download_button(
                "📊 Xuất Excel",
                data=buffer,
                file_name="Kho_da_phan_loai.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                type="primary"
            )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )