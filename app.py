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
from modules.cong_no import show as cong_no
from modules.xuat_hang import show as xuat_hang

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🪵",
    layout="wide"
)

# Khởi tạo dữ liệu nền
if "db_init" not in st.session_state:
    tao_database()
    st.session_state.db_init = True

if "page" not in st.session_state:
    st.session_state.page = "nhap"

# Biến lưu trạng thái nhóm nào đang được bấm mở (Mặc định mở nhóm đầu tiên)
if "open_group" not in st.session_state:
    st.session_state.open_group = "📥 Giao dịch Kho"

# ==========================
# ÁP DỤNG CSS CUSTOM
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
# THANH MENU SIDEBAR XỔ PHÂN CẤP
# ==========================
with st.sidebar:
    st.markdown("<h1 style='margin-bottom: 0;'> MUỐN GHI CÁI GÌ GHI </h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #8C2F48; font-size: 0.9em;'> 123 Chẳng hạn </p>", unsafe_allow_html=True)
    st.divider()


    # Cấu trúc Menu
    nhom_menu = {
        "📥 Giao dịch Kho": {
            "nhap": "📥 Nhập hàng tươi/khô",
            "xuat": "🚚 Xuất hàng",
            "say": "🔥 Vận hành hầm sấy",
            "kho": "🏬 Quản lý kho hàng"
        },
        "⚙️ Quản lý Danh mục": {
            "loaigo": "🪵 Danh mục loại gỗ",
            "kh": "👤 Danh mục khách hàng",
            "phanloai": "📦 Danh mục phân loại"
        },
        "📊 Kế toán & Thống kê": {
            "congno": "💰 Thanh toán & Công nợ",
            "bc": "📊 Báo cáo thống kê"
        }
    }

    # Vẽ các nhóm menu lên giao diện
    for group_name, sub_menus in nhom_menu.items():
        # Kiểm tra xem nhóm này có đang mở hay không để đổi icon mũi tên
        is_open = st.session_state.open_group == group_name
        arrow = "▼" if is_open else "►"
        
        # 1. NÚT NHÓM LỚN
        if st.button(f"{arrow} {group_name}", width="stretch", key=f"grp_{group_name}"):
            # Nếu đang đóng thì mở ra, nếu đang mở thì đóng lại
            st.session_state.open_group = group_name if not is_open else ""
            st.rerun()

        # 2. XỔ CÁC NÚT CON (Chỉ chạy khi nhóm này đang được mở)
        if st.session_state.open_group == group_name:
            # Bọc trong một container để áp dụng hiệu ứng thụt lề CSS
            with st.container():
                st.markdown('<div class="sidebar-sub-menu">', unsafe_allow_html=True)
                for page_key, page_name in sub_menus.items():
                    
                    # Kiểm tra nút con nào đang active để tô màu hồng đậm
                    is_active = st.session_state.page == page_key
                    
                    if st.button(
                        page_name, 
                        width="stretch", 
                        key=f"sub_{page_key}",
                        type="primary" if is_active else "secondary"
                    ):
                        st.session_state.page = page_key
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
        
        st.write("") # Tạo khoảng cách nhỏ giữa các nhóm lớn

# ==========================
# KHU VỰC HIỂN THỊ NỘI DUNG MAIN
# ==========================
st.title(f"🌸 {APP_NAME}")
st.divider()

# BỘ ĐIỀU HƯỚNG ROUTER CHÍNH XÁC
if st.session_state.page == "nhap":
    nhap_kho()

elif st.session_state.page == "xuat":
    xuat_hang()

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

elif st.session_state.page == "congno":
    cong_no()