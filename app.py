import streamlit as st

from config import APP_NAME
from database.db import tao_database

from modules.dashboard import show as dashboard
from modules.loai_go import show as loai_go
from modules.nhap_kho import show as nhap_kho
from modules.ham_say import show as ham_say
from modules.ton_kho import show as ton_kho
from modules.khach_hang import show as khach_hang
from modules.bao_cao import show as bao_cao
from modules.tra_khach import show as tra_khach
from modules.cong_no import show as cong_no
from modules.phieu_thu import show as phieu_thu


st.set_page_config(
    page_title=APP_NAME,
    page_icon="🪵",
    layout="wide"
)

if "db_init" not in st.session_state:
    tao_database()
    st.session_state.db_init = True


if "page" not in st.session_state:
    st.session_state.page = "dashboard"


# ==========================
# CSS
# ==========================

try:
    with open("assets/style.css", encoding="utf-8") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )
except:
    pass


# ==========================
# SIDEBAR
# ==========================

with st.sidebar:

    st.title("🪵 Kho Gỗ")

    st.divider()

    menus = {
        "dashboard": "🏠 Dashboard",
        "nhap": "📥 Nhận gỗ",
        "xuat": "🔥 Hầm sấy",
        "tra": "📤 Trả khách",
        "cong_no": "💰 Công nợ",
        "ton": "📦 Tồn kho",
        "loaigo": "🪵 Loại gỗ",
        "kh": "👤 Khách hàng",
        "baocao": "📊 Báo cáo"
    }

    for key, text in menus.items():

        if st.button(text, width="stretch"):

            st.session_state.page = key



# ==========================
# HEADER
# ==========================
st.empty()
st.title(APP_NAME)

st.divider()


# ==========================
# ROUTER
# ==========================

if st.session_state.page == "dashboard":
    dashboard()

elif st.session_state.page == "loaigo":

    st.header("🪵 Loại gỗ")

    st.write("TEST")

elif st.session_state.page == "nhap":
    nhap_kho()

elif st.session_state.page == "xuat":
    ham_say()

elif st.session_state.page == "ton":
    ton_kho()

elif st.session_state.page == "kh":
    khach_hang()

elif st.session_state.page == "baocao":
    bao_cao()

elif st.session_state.page == "tra":
    tra_khach()

elif st.session_state.page == "cong_no":
    cong_no()

elif st.session_state.page == "phieu_thu":
    phieu_thu()