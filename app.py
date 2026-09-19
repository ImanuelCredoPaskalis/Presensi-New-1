"""
Entry Point: app.py
Sistem Presensi Mahasiswa & Monitoring Lab Micro Teaching FisMat
Desain: Nocturne Precision Lab (Dark Minimalist Glassmorphism)
Database: Google Sheets Direct Integration
"""

import streamlit as st
from utils.auth_helper import is_admin, verify_admin_pin, logout_admin

# 1. Konfigurasi Dasar Halaman
st.set_page_config(
    page_title="Presensi Mahasiswa - Lab FisMat",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Injeksi Styling Tema Nocturne Precision Lab
from utils.ui_components import inject_custom_css, render_sidebar_branding, render_sidebar_footer
inject_custom_css()

# 3. Sidebar Branding
render_sidebar_branding()

# 4. Modul Admin Login di Sidebar
with st.sidebar:
    if is_admin():
        st.markdown(
            """
            <div style="padding: 6px 12px; background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 8px; font-size: 12px; color: #4edea3; margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between;">
              <span><strong>Mode Admin</strong> Aktif</span>
              <span class="pulse-emerald"></span>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Kunci / Keluar Admin", use_container_width=True, help="Kunci kembali akses konfigurasi"):
            logout_admin()
            st.rerun()
    else:
        with st.expander("Akses Admin", expanded=False):
            pin_input = st.text_input("PIN Admin", type="password", placeholder="Masukkan PIN...", key="sidebar_pin_input")
            if st.button("Buka Akses Admin", use_container_width=True):
                if verify_admin_pin(pin_input):
                    st.success("Akses Admin Terbuka!")
                    st.rerun()
                else:
                    st.error("PIN Salah!")

# 5. Konfigurasi Navigasi Modern (5 Modul Utama)
pages = [
    st.Page("pages/1_Presensi_Mahasiswa.py", title="Presensi Mahasiswa", icon=":material/check_circle:", default=True),
    st.Page("pages/2_Dashboard_Live.py", title="Dashboard Live", icon=":material/monitoring:"),
    st.Page("pages/3_Data_Mahasiswa.py", title="Data Mahasiswa", icon=":material/school:"),
    st.Page("pages/4_Rekap_Laporan.py", title="Rekap & Laporan", icon=":material/description:"),
    st.Page("pages/5_Pengaturan.py", title="Pengaturan", icon=":material/settings:"),
]

pg = st.navigation(pages)
pg.run()

# 6. Sidebar Footer (Status Koneksi & Versi)
render_sidebar_footer()
