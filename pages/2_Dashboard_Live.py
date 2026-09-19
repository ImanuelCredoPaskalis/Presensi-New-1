"""
Modul 2: Dashboard Live & Telemetri
Visualisasi KPI Bento, Donut Chart, Beban Jam Sibuk Lab, dan Live Activity Feed.
"""

from datetime import datetime
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.ui_components import render_global_header, get_status_badge_html, safe_html
from utils.gsheets_manager import get_sheets_manager
from utils.export_manager import export_to_csv

render_global_header("Dashboard Live")

sm = get_sheets_manager()
connection_status = sm.get_status()
today_str = datetime.now().strftime("%Y-%m-%d")

# Auto-refresh yang benar-benar berjalan setiap 15 detik.
try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=15_000, key="dashboard_live_refresh")
except ImportError:
    pass

# Ambil data
df_master = sm.get_master_mahasiswa()
df_presensi = sm.get_presensi(today_str)
logs = sm.get_logs(limit=8)

# Perhitungan metrik
total_asisten = len(df_master) if not df_master.empty else 6
hadir_lab = len(df_presensi[df_presensi["Status_Terkini"] == "Hadir di Lab"])
di_kelas = len(df_presensi[df_presensi["Status_Terkini"] == "Sedang di Kelas"])
sedang_tugas = len(df_presensi[df_presensi["Status_Terkini"] == "Sedang Tugas"])
izin_khusus = len(df_presensi[df_presensi["Status_Terkini"] == "Izin Keluar"])
selesai_pulang = len(df_presensi[df_presensi["Status_Terkini"] == "Pulang"])

total_checked_in = hadir_lab + di_kelas + sedang_tugas + izin_khusus + selesai_pulang
belum_hadir = max(0, total_asisten - total_checked_in)
pct_checkin = int((total_checked_in / total_asisten * 100)) if total_asisten > 0 else 0
utilisasi_lab = int((hadir_lab / total_asisten * 100)) if total_asisten > 0 else 0

# =========================================================
# HEADER BANNER & QUICK CONTROL BAR
# =========================================================
sync_copy = "Tersinkron Google Sheets" if connection_status["online"] else "Mode Lokal — menunggu konfigurasi Google Sheets"
st.markdown(
    f"""
    <div class="glass-panel" style="margin-bottom: 20px; background: linear-gradient(135deg, rgba(23, 27, 38, 0.95), rgba(15, 19, 29, 0.95)); border: 1px solid rgba(76, 215, 246, 0.2);">
      <div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 16px;">
        <div>
          <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
            <span class="badge-emerald"><span class="pulse-emerald"></span> Telemetry Aktif</span>
            <span style="color: #869397;">•</span>
            <span style="font-family: 'JetBrains Mono'; font-size: 12px; color: #bcc9cd;">{sync_copy}</span>
          </div>
          <h2 style="font-family: 'Space Grotesk', sans-serif; font-size: 24px; font-weight: 700; color: #dfe2f1; margin: 0 0 4px 0; letter-spacing: -0.01em;">
            Dashboard & Pemantauan Presensi Hari Ini
          </h2>
          <p style="font-size: 13px; color: #869397; margin: 0;">
            Monitoring kehadiran real-time dan audit pergerakan mahasiswa asisten Lab Micro Teaching Fisika & Matematika.
          </p>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Control Bar: Tombol Segarkan & Ekspor
ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([4, 4, 4])
with ctrl_col1:
    if st.button("Segarkan Data (Auto 15s)", use_container_width=True, icon=":material/sync:"):
        st.cache_data.clear()
        st.rerun()

with ctrl_col2:
    filter_status_dash = st.selectbox(
        "Filter Status:",
        ["Semua Status", "Hadir di Lab", "Sedang di Kelas", "Sedang Tugas", "Belum Hadir"],
        label_visibility="collapsed"
    )

with ctrl_col3:
    csv_bytes = export_to_csv(df_presensi)
    st.download_button(
        "Ekspor Ringkasan CSV",
        data=csv_bytes,
        file_name=f"ringkasan_presensi_{today_str}.csv",
        mime="text/csv",
        use_container_width=True,
        icon=":material/file_download:"
    )

st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)

# =========================================================
# 6 BENTO METRIC CARDS
# =========================================================
b1, b2, b3 = st.columns(3)

with b1:
    st.markdown(
        f"""
        <div class="bento-card">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-family: 'JetBrains Mono'; font-size: 10px; color: #869397; text-transform: uppercase;">Total Asisten</span>
            <span class="material-symbols-outlined" style="color: #869397; font-size: 18px;">group</span>
          </div>
          <div style="margin-top: 10px;">
            <div style="font-family: 'Space Grotesk'; font-size: 28px; font-weight: 700; color: #dfe2f1;">{total_asisten}</div>
            <div style="font-size: 11px; color: #4edea3; margin-top: 2px;">• 100% Terdaftar</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with b2:
    st.markdown(
        f"""
        <div class="bento-card" style="border-color: rgba(78, 222, 163, 0.25);">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-family: 'JetBrains Mono'; font-size: 10px; color: #4edea3; text-transform: uppercase;">Hadir di Lab</span>
            <span class="material-symbols-outlined" style="color: #4edea3; font-size: 18px;">science</span>
          </div>
          <div style="margin-top: 10px;">
            <div style="font-family: 'Space Grotesk'; font-size: 28px; font-weight: 700; color: #4edea3;">{hadir_lab}</div>
            <div style="font-size: 11px; color: #4edea3; margin-top: 2px;">• {utilisasi_lab}% Utilisasi</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with b3:
    st.markdown(
        f"""
        <div class="bento-card" style="border-color: rgba(76, 215, 246, 0.25);">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-family: 'JetBrains Mono'; font-size: 10px; color: #4cd7f6; text-transform: uppercase;">Kuliah / Kelas</span>
            <span class="material-symbols-outlined" style="color: #4cd7f6; font-size: 18px;">menu_book</span>
          </div>
          <div style="margin-top: 10px;">
            <div style="font-family: 'Space Grotesk'; font-size: 28px; font-weight: 700; color: #4cd7f6;">{di_kelas}</div>
            <div style="font-size: 11px; color: #bcc9cd; margin-top: 2px;">• Sedang berlangsung</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
b4, b5, b6 = st.columns(3)

with b4:
    st.markdown(
        f"""
        <div class="bento-card" style="border-color: rgba(192, 193, 255, 0.25);">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-family: 'JetBrains Mono'; font-size: 10px; color: #c0c1ff; text-transform: uppercase;">Tugas Luar</span>
            <span class="material-symbols-outlined" style="color: #c0c1ff; font-size: 18px;">directions_run</span>
          </div>
          <div style="margin-top: 10px;">
            <div style="font-family: 'Space Grotesk'; font-size: 28px; font-weight: 700; color: #c0c1ff;">{sedang_tugas}</div>
            <div style="font-size: 11px; color: #bcc9cd; margin-top: 2px;">• Dispensasi Lab</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with b5:
    st.markdown(
        f"""
        <div class="bento-card">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-family: 'JetBrains Mono'; font-size: 10px; color: #869397; text-transform: uppercase;">Izin / Sakit</span>
            <span class="material-symbols-outlined" style="color: #869397; font-size: 18px;">history_toggle_off</span>
          </div>
          <div style="margin-top: 10px;">
            <div style="font-family: 'Space Grotesk'; font-size: 28px; font-weight: 700; color: #dfe2f1;">{izin_khusus}</div>
            <div style="font-size: 11px; color: #869397; margin-top: 2px;">• {izin_khusus} catatan aktif</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with b6:
    st.markdown(
        f"""
        <div class="bento-card" style="border-color: rgba(255, 180, 171, 0.25);">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-family: 'JetBrains Mono'; font-size: 10px; color: #ffb4ab; text-transform: uppercase;">Belum Hadir</span>
            <span class="material-symbols-outlined" style="color: #ffb4ab; font-size: 18px;">schedule</span>
          </div>
          <div style="margin-top: 10px;">
            <div style="font-family: 'Space Grotesk'; font-size: 28px; font-weight: 700; color: #ffb4ab;">{belum_hadir}</div>
            <div style="font-size: 11px; color: #ffb4ab; margin-top: 2px;">• Menunggu</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

# =========================================================
# DISTRIBUSI STATUS & LIVE ACTIVITY FEED (2 KOLOM)
# =========================================================
grid_left, grid_right = st.columns([6, 6], gap="large")

# ----------------- WIDGET KIRI: DISTRIBUSI STATUS KEHADIRAN -----------------
with grid_left:
    st.markdown(
        """
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
          <div>
            <div style="font-family: 'JetBrains Mono'; font-size: 10px; color: #869397; text-transform: uppercase;">Analitik Kehadiran</div>
            <h3 style="font-family: 'Space Grotesk'; font-size: 18px; font-weight: 700; color: #dfe2f1; margin: 0;">Distribusi Status Kehadiran</h3>
          </div>
          <span class="badge-cyan"><span class="pulse-emerald"></span> Live Telemetry</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Plotly Donut Chart
    labels = ["Di Lab", "Kelas", "Tugas", "Belum Hadir"]
    values = [max(1, hadir_lab), max(0, di_kelas), max(0, sedang_tugas), max(0, belum_hadir)]
    colors = ["#4edea3", "#4cd7f6", "#c0c1ff", "#ffb4ab"]

    fig_donut = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.65,
                marker=dict(colors=colors, line=dict(color="#0f131d", width=2)),
                textinfo="none",
                hoverinfo="label+value+percent"
            )
        ]
    )
    fig_donut.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.12,
            xanchor="center",
            x=0.5,
            font=dict(color="#bcc9cd", size=11, family="Manrope")
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=10, b=10),
        height=290,
        annotations=[
            dict(
                text=f"<b>{pct_checkin}%</b><br><span style='font-size:10px; color:#869397;'>CHECK-IN</span>",
                x=0.5, y=0.5,
                font=dict(size=18, color="#dfe2f1", family="Space Grotesk"),
                showarrow=False
            )
        ]
    )
    st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})

    stat_lab, stat_kelas, stat_tugas = st.columns(3)
    with stat_lab:
        st.metric("Di Lab", hadir_lab, help="Asisten yang aktif berada di laboratorium")
    with stat_kelas:
        st.metric("Di Kelas", di_kelas, help="Asisten yang sedang mengikuti sesi kelas")
    with stat_tugas:
        st.metric("Tugas Luar", sedang_tugas, help="Asisten yang sedang menjalankan tugas luar")

# ----------------- WIDGET KANAN: LIVE ACTIVITY FEED -----------------
with grid_right:
    st.markdown(
        """
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
          <div>
            <div style="font-family: 'JetBrains Mono'; font-size: 10px; color: #869397; text-transform: uppercase;">Audit Real-time</div>
            <h3 style="font-family: 'Space Grotesk'; font-size: 18px; font-weight: 700; color: #dfe2f1; margin: 0;">Live Activity Feed</h3>
          </div>
          <span class="pulse-emerald"></span>
        </div>
        """,
        unsafe_allow_html=True
    )

    if not logs:
        st.info("Belum ada aktivitas logging hari ini.")
    else:
        # Komponen native agar setiap catatan tidak mungkin dirender sebagai markup/kode.
        for l in logs[:6]:
            nama_mhs = str(l.get("Nama_Mahasiswa", "Asisten"))
            keterangan = str(l.get("Keterangan", "Aktivitas presensi"))
            timestamp = str(l.get("Timestamp", ""))
            jam = timestamp.split(" ")[1][:5] if " " in timestamp else timestamp[:5]
            aksi = str(l.get("Aksi", "Aktivitas"))
            with st.container(border=True, height=72):
                feed_name, feed_time = st.columns([5, 1])
                with feed_name:
                    st.write(f"**{nama_mhs}** · {aksi}")
                    st.caption(keterangan)
                with feed_time:
                    st.caption(jam)

# =========================================================
# TABEL AUDIT STATUS KEHADIRAN HARI INI
# =========================================================
st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
st.markdown(
    """
    <div style="margin-bottom: 12px;">
      <h3 style="font-family: 'Space Grotesk'; font-size: 18px; font-weight: 700; color: #dfe2f1; margin: 0;">Daftar Status Kehadiran & Aktivitas Asisten Hari Ini</h3>
      <p style="font-size: 12px; color: #869397; margin: 2px 0 0 0;">Audit jam masuk, kelas, tugas luar, dan akumulasi durasi shift.</p>
    </div>
    """,
    unsafe_allow_html=True
)

df_dash_tbl = df_presensi.copy()
if filter_status_dash != "Semua Status":
    df_dash_tbl = df_dash_tbl[df_dash_tbl["Status_Terkini"] == filter_status_dash]

if df_dash_tbl.empty:
    st.info("Tidak ada data presensi yang cocok dengan filter status saat ini.")
else:
    dashboard_columns = [
        "Nama_Mahasiswa", "Program_Studi", "Jam_Masuk", "Nama_Mata_Kuliah",
        "Durasi_Kelas", "Keterangan_Tugas", "Durasi_Shift", "Status_Terkini"
    ]
    dashboard_labels = {
        "Nama_Mahasiswa": "Nama Mahasiswa",
        "Program_Studi": "Program Studi",
        "Jam_Masuk": "Jam Masuk",
        "Nama_Mata_Kuliah": "Mata Kuliah",
        "Durasi_Kelas": "Durasi Kelas",
        "Keterangan_Tugas": "Tugas Luar",
        "Durasi_Shift": "Total Shift",
        "Status_Terkini": "Status Terkini",
    }
    dashboard_data = df_dash_tbl[dashboard_columns].rename(columns=dashboard_labels).reset_index(drop=True)
    dashboard_data.index = dashboard_data.index + 1
    dashboard_data.index.name = "No"
    st.dataframe(dashboard_data, use_container_width=True, hide_index=False)
