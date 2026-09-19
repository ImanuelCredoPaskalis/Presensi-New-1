"""
Module: ui_components.py
Komponen UI render HTML untuk tema Nocturne Precision Lab di Streamlit.
"""

import os
from html import escape
from datetime import datetime
import streamlit as st
from utils.time_calculator import get_current_date_id, get_current_time_wib
from utils.gsheets_manager import get_sheets_manager
from utils.auth_helper import is_admin, logout_admin


def safe_html(value) -> str:
    """Escape nilai dinamis sebelum dirender lewat HTML kustom."""
    return escape(str(value if value is not None else ""))


def inject_custom_css():
    """Membaca dan menginjeksikan theme.css ke halaman Streamlit."""
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "styles", "theme.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)


def render_sidebar_branding():
    """Render elemen branding dan status koneksi pada sidebar Streamlit."""
    sm = get_sheets_manager()
    status = sm.get_status()
    
    with st.sidebar:
        # Logo & Judul
        st.markdown(
            """
            <div style="padding: 10px 0 16px 0; border-bottom: 1px solid rgba(255,255,255,0.08); display: flex; align-items: center; gap: 12px;">
              <div style="width: 36px; height: 36px; border-radius: 8px; background: rgba(6, 182, 212, 0.15); border: 1px solid rgba(6, 182, 212, 0.3); display: flex; align-items: center; justify-content: center;">
                <span class="material-symbols-outlined" style="color: #4cd7f6; font-size: 22px;">science</span>
              </div>
              <div style="min-width: 0;">
                <div style="font-family: 'Space Grotesk', sans-serif; font-size: 15px; font-weight: 700; color: #4cd7f6; letter-spacing: -0.01em; line-height: 1.2;">PRESENSI MAHASISWA</div>
                <div style="font-size: 11px; color: #869397; margin-top: 2px;">Lab Micro Teaching FisMat</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )


def render_sidebar_footer():
    """Render footer info versi dan status koneksi di bagian bawah sidebar."""
    sm = get_sheets_manager()
    status = sm.get_status()
    is_live = status["online"]
    status_text = "Google Sheets Terhubung" if is_live else "Mode Lokal — Google Sheets Belum Dihubungkan"
    
    with st.sidebar:
        st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div style="background: rgba(28, 31, 42, 0.85); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 12px; margin-top: auto;">
              <div style="display: flex; align-items: center; justify-content: space-between;">
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 600; color: #dfe2f1;">Versi 2.0 • Web Edition</span>
                <span class="pulse-emerald"></span>
              </div>
              <div style="font-size: 11px; color: #869397; margin: 4px 0 6px 0;">Micro Teaching Fisika & Matematika</div>
              <div style="display: flex; align-items: center; gap: 6px; font-size: 11px; color: #4edea3; font-family: 'JetBrains Mono', monospace;">
                <span class="material-symbols-outlined" style="font-size: 14px;">cloud_done</span>
                <span>{status_text}</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )


def render_global_header(page_title: str):
    """Render breadcrumb, live clock WIB, cloud sync badge, dan tombol kunci admin."""
    sm = get_sheets_manager()
    status = sm.get_status()
    now_time = datetime.now().strftime("%H:%M:%S WIB")
    admin_auth = is_admin()

    col1, col2 = st.columns([6, 6])
    with col1:
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 8px; font-size: 13px; color: #869397; margin-bottom: 8px;">
              <span>Lab FisMat</span>
              <span class="material-symbols-outlined" style="font-size: 14px;">chevron_right</span>
              <span style="color: #4cd7f6; font-weight: 600;">{page_title}</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        sync_label = "Tersinkron Google Sheets" if status["online"] else "Mode Lokal"
        admin_badge = "<span style='color: #4edea3; font-weight:600;'>[Admin Aktif]</span>" if admin_auth else "<span style='color: #869397;'>[Mode Pengguna]</span>"
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; justify-content: flex-end; gap: 12px; font-size: 12px; margin-bottom: 8px;">
              <div style="background: rgba(38,42,53,0.7); border: 1px solid rgba(255,255,255,0.08); padding: 4px 10px; border-radius: 6px; font-family: 'JetBrains Mono'; color: #4cd7f6; font-weight: 600;">
                <span class="material-symbols-outlined" style="font-size: 13px; vertical-align: middle;">schedule</span> {now_time}
              </div>
              <div style="background: rgba(38,42,53,0.5); border: 1px solid rgba(255,255,255,0.08); padding: 4px 10px; border-radius: 6px; color: #4edea3; font-size: 11px;">
                <span class="pulse-emerald" style="vertical-align: middle; margin-right: 4px;"></span> {sync_label}
              </div>
              <div style="font-size: 11px;">
                {admin_badge}
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )


def render_telemetry_banner(title: str, subtitle: str, extra_metric_val: str = "5 Orang", extra_metric_lbl: str = "Total Asisten"):
    """Render banner besar di atas halaman Presensi dan Dashboard."""
    date_str = get_current_date_id()
    now_clock = datetime.now().strftime("%H:%M:%S")
    
    st.markdown(
        f"""
        <div class="glass-panel" style="margin-bottom: 20px; background: linear-gradient(135deg, rgba(23, 27, 38, 0.95), rgba(15, 19, 29, 0.95)); border: 1px solid rgba(76, 215, 246, 0.2);">
          <div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 16px;">
            <div>
              <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                <span class="badge-emerald"><span class="pulse-emerald"></span> Telemetry Aktif</span>
                <span style="color: #869397;">•</span>
                <span style="font-family: 'JetBrains Mono'; font-size: 12px; color: #bcc9cd;">{date_str}</span>
              </div>
              <h2 style="font-family: 'Space Grotesk', sans-serif; font-size: 24px; font-weight: 700; color: #dfe2f1; margin: 0 0 4px 0; letter-spacing: -0.01em;">
                {title}
              </h2>
              <p style="font-size: 13px; color: #869397; margin: 0; max-width: 650px;">
                {subtitle}
              </p>
            </div>
            <div style="display: flex; align-items: center; gap: 20px;">
              <div style="text-align: right;">
                <div style="font-family: 'JetBrains Mono'; font-size: 10px; color: #869397; text-transform: uppercase; letter-spacing: 0.05em;">Waktu Server</div>
                <div style="display: flex; align-items: baseline; gap: 6px; margin-top: 2px;">
                  <span class="clock-text">{now_clock}</span>
                  <span style="background: rgba(38,42,53,0.8); border: 1px solid rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 4px; font-family: 'JetBrains Mono'; font-size: 11px; color: #4edea3; font-weight: 600;">WIB</span>
                </div>
              </div>
              <div style="padding-left: 20px; border-left: 1px solid rgba(255,255,255,0.08); text-align: right;">
                <div style="font-family: 'JetBrains Mono'; font-size: 10px; color: #869397; text-transform: uppercase;">{extra_metric_lbl}</div>
                <div style="font-family: 'Space Grotesk'; font-size: 20px; font-weight: 700; color: #dfe2f1; margin-top: 2px;">{extra_metric_val}</div>
              </div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def get_status_badge_html(status: str) -> str:
    """Mengembalikan badge HTML berwarna sesuai status."""
    st_clean = str(status).strip()
    if st_clean == "Hadir di Lab":
        return '<span class="badge-emerald"><span class="pulse-emerald"></span> Hadir di Lab</span>'
    elif st_clean == "Sedang di Kelas":
        return '<span class="badge-amber">Sedang di Kelas</span>'
    elif st_clean == "Sedang Tugas":
        return '<span class="badge-cyan">Sedang Tugas</span>'
    elif st_clean == "Izin Keluar":
        return '<span class="badge-amber">Izin Keluar</span>'
    elif st_clean == "Pulang":
        return '<span class="badge-rose">Pulang / Selesai</span>'
    else:
        return '<span class="badge-muted">Belum Presensi</span>'
