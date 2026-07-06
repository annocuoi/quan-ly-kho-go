import streamlit as st

from config import APP_NAME
from database.db import tao_database

from modules.loai_go import show as loai_go
from modules.nhap_kho import show as nhap_kho
from modules.khach_hang import show as khach_hang
from modules.kho import show as kho
from modules.bao_cao import show as bao_cao
from modules.ham_say import show as ham_say
from modules.phan_loai_go import show as phan_loai_go


st.set_page_config(
    page_title=APP_NAME,
    page_icon="🪵",
    layout="wide"
)

if "db_init" not in st.session_state:
    tao_database()
    st.session_state.db_init = True


if "page" not in st.session_state:
    st.session_state.page = "nhap"


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
        "nhap": "📥 Nhập hàng",
        "loaigo": "🪵 Loại gỗ",
        "kh": "👤 Khách hàng",
        "kho": "🏬 Kho",
        "say": "🔥 Hầm sấy",
        "phanloai": "📦 Phân loại",
        "bc": "📊 Báo cáo"
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

if st.session_state.page == "nhap":
    nhap_kho()

elif st.session_state.page == "loaigo":
    loai_go()

elif st.session_state.page == "kh":
    khach_hang()

elif st.session_state.page == "kho":
    kho()

elif st.session_state.page == "bc":
    bao_cao()

elif st.session_state.page == "say":
    ham_say()

elif st.session_state.page == "phanloai":
    phan_loai_go()